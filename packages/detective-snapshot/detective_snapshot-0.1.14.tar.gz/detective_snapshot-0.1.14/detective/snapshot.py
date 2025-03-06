import functools
import hashlib
import inspect
import json
import logging
import os
import time
from contextvars import ContextVar
from typing import Any, Callable, Dict, List, Optional

import jsbeautifier
from jsonpath_ng.exceptions import JSONPathError
from jsonpath_ng.ext import parse as parse_ext

from detective.proto_utils import is_protobuf, protobuf_to_dict

# --- Configure Logging ---
logger = logging.getLogger(__name__)

# --- Context Variables for Session Management ---
session_id_var: ContextVar[Optional[str]] = ContextVar("debug_session_id", default=None)
# Store a list of current call data dictionaries
inner_calls_var: ContextVar[Optional[List[Dict[str, Any]]]] = ContextVar(
    "inner_function_calls", default=None
)
session_start_time_var: ContextVar[Optional[float]] = ContextVar(
    "session_start_time", default=None
)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle special objects."""

    def default(self, obj: Any) -> Any:
        if is_protobuf(obj):
            return protobuf_to_dict(obj)
        elif isinstance(obj, dict):
            # Filter out non-serializable keys
            return {
                str(k): self._convert_value(v)
                for k, v in obj.items()
                # if isinstance(k, (str, int, float, bool)) or k is None
            }
        elif isinstance(obj, list):
            return [self._convert_value(item) for item in obj]
        elif hasattr(obj, "to_dict"):
            return self.default(obj.to_dict())
        elif hasattr(obj, "__dataclass_fields__"):
            return {
                field: self.default(getattr(obj, field))
                for field in obj.__dataclass_fields__
            }
        # Special handling for class objects (cls parameter in class methods)
        elif isinstance(obj, type):
            # Only include non-internal attributes that are relevant for debugging
            return {
                k: self._convert_value(v)
                for k, v in obj.__dict__.items()
                if (
                    not k.startswith("__")  # Skip internal attributes
                    and not callable(v)  # Skip methods
                    and not isinstance(
                        v, (staticmethod, classmethod)
                    )  # Skip decorators
                )
            }
        elif hasattr(obj, "__dict__"):
            return self.default(obj.__dict__)
        else:
            try:
                return super().default(obj)
            except TypeError:
                return str(obj)

    def _convert_value(self, value: Any) -> Any:
        """Helper method to convert values while preserving numeric types."""
        if isinstance(value, (int, float)):
            return value  # Keep numeric values as-is
        return self.default(value)

def _sanitize_dict_keys(data: Any) -> Any:
    """Pre-process data to ensure all dictionary keys are strings.

    Args:
        data: Any data structure that might contain dictionaries

    Returns:
        Processed data with all dictionary keys converted to strings
    """
    if isinstance(data, dict):
        return {
            str(k): _sanitize_dict_keys(v)
            for k, v in data.items()
        }
    elif isinstance(data, (list, tuple)):
        return [_sanitize_dict_keys(x) for x in data]
    return data

def get_snapshot_filepath(
    session_id: str, function_name: str, session_start_time: float
) -> str:
    """Generate the filepath for a snapshot file.

    Args:
        session_id: The hash for the current session
        function_name: Name of the outermost function
        session_start_time: Start time of the session

    Returns:
        Path to the snapshot file
    """
    # Get current time in local timezone
    current_time = time.localtime()

    # Format: MMDDHHMMSSS (month, day, hour, minute, second)
    timestamp = time.strftime("%m%d%H%M%S", current_time)

    # Create the base directory
    base_dir = "_snapshots"
    os.makedirs(base_dir, exist_ok=True)

    # Generate filename with function name, timestamp and hash
    filename = f"{function_name}_{timestamp}_{session_id}.json"

    return os.path.join(base_dir, filename)


def _generate_short_hash() -> str:
    """Generate a short 7-character hash."""
    # Use current time and a random component to generate hash
    timestamp = str(time.time())
    # Take first 7 characters of the md5 hash
    return hashlib.md5(timestamp.encode()).hexdigest()[:7]


def _is_debug_enabled() -> bool:
    """Check if debug mode is enabled via environment variables.

    Returns:
        True if either DEBUG or DETECTIVE is set to "true" or "1" (case insensitive)
    """
    debug_vars = ["DEBUG", "DETECTIVE"]
    for var in debug_vars:
        value = os.environ.get(var, "").lower()
        if value in ("true", "1"):
            return True
    return False


def _get_original_function(func: Any) -> Any:
    """Get the original function by unwrapping decorators.

    Args:
        func: The potentially wrapped function

    Returns:
        The original unwrapped function
    """
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func


class Snapshotter:
    def __init__(
        self,
        func: Any,
        input_fields: Optional[List[str]] = None,
        output_fields: Optional[List[str]] = None,
        include_implicit: bool = False,
    ):
        self.func = func
        self.orig_func = _get_original_function(func)  # Get original function

        # If include_implicit is True, add self/cls to input_fields if not already present
        if include_implicit:
            input_fields = list(input_fields or [])  # Convert None to empty list
            sig = inspect.signature(self.orig_func)
            params = list(sig.parameters.keys())
            if params and params[0] in ('self', 'cls'):
                if not any(f == params[0] or f.startswith(f"{params[0]}.") for f in input_fields):
                    input_fields.append(params[0])

        self.input_fields = input_fields
        self.output_fields = output_fields
        self.include_implicit = include_implicit
        self.inner_calls = inner_calls_var.get() or []
        self.is_outermost = not self.inner_calls

        # Initialize session for outermost calls
        if self.is_outermost:
            session_id_var.set(_generate_short_hash())
            session_start_time_var.set(time.time() * 1000)
        self.session_id = session_id_var.get()
        self.session_start_time = session_start_time_var.get()

    def _get_or_create_session_id(self) -> str:
        # Remove this method as we handle session ID in __init__
        session_id = session_id_var.get()
        if session_id is None:
            raise RuntimeError("Session ID not initialized")
        return session_id

    def _prepare_call_data(self, args: Any, kwargs: Any) -> Dict[str, Any]:
        # Use original function for signature inspection
        all_kwargs = inspect.getcallargs(self.orig_func, *args, **kwargs)

        # Only remove 'self' or 'cls' if include_implicit is False AND
        # there are no input_fields that explicitly reference self/cls
        should_include_implicit = self.include_implicit

        # Check if any input_fields explicitly reference self or cls
        if not should_include_implicit and self.input_fields:
            for field in self.input_fields:
                # Check for both direct field names and path references
                if (field in ("self", "cls") or
                    field.startswith("self.") or
                    field.startswith("cls.")):
                    should_include_implicit = True
                    break

        # Remove 'self' or 'cls' if we shouldn't include them
        if not should_include_implicit:
            # Check if this is an instance or class method
            if "self" in all_kwargs:
                del all_kwargs["self"]
            elif "cls" in all_kwargs:
                del all_kwargs["cls"]

        # Apply input field selection if specified
        if self.input_fields:
            all_kwargs = self._extract_and_format_fields(all_kwargs, self.input_fields, True) or all_kwargs

        return {
            "FUNCTION": self.orig_func.__name__,  # Use original function name
            "INPUTS": all_kwargs,
            "OUTPUT": None,
        }

    def _extract_field_values(self, data: Any, jsonpath_expr: str) -> List[Any]:
        """Extract values from data using a single jsonpath expression."""
        try:
            matches = parse_ext(jsonpath_expr).find(data)
            return matches
        except JSONPathError:
            return []
        except Exception:
            return []

    def _update_result(
        self, result: Dict[str, Any], clean_path: str, value: Any
    ) -> None:
        """Update the result dictionary with the value at the cleaned path."""
        try:
            target_expr = parse_ext(f"$.{clean_path}")
            target_expr.update_or_create(result, value)
        except Exception:
            pass

    def _extract_and_format_fields(
        self, data: Any, fields: Optional[List[str]], is_input: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Extract and format specified fields from the data using jsonpath_ng.
        """
        if not fields or data is None:
            return None

        # Convert data to dict once at the start
        data_as_dict = json.loads(json.dumps(data, cls=CustomJSONEncoder))
        result: Dict[str, Any] = {}

        for field_path in fields:
            try:
                jsonpath_str = self._cleanse_field_path(field_path)

                expressions = jsonpath_str.split(" | ")
                for expr in expressions:
                    matches = self._extract_field_values(data_as_dict, expr)
                    if not matches:
                        continue

                    for match in matches:
                        if match.value is not None:
                            clean_path = str(match.full_path).replace(".[", "[")
                            # For input fields, use the original field name as the key
                            if (
                                is_input
                                and "." not in field_path
                                and "[" not in field_path
                            ):
                                result[field_path] = match.value
                            else:
                                self._update_result(result, clean_path, match.value)

                self._clean_empty_structures(result)

            except Exception:
                continue

        return result if result else None

    def _clean_empty_structures(self, data: Any) -> None:
        """Recursively remove empty structures (empty lists, dicts, None values)."""
        if isinstance(data, dict):
            # First clean nested structures
            for key, value in list(data.items()):
                if isinstance(value, (dict, list)):
                    self._clean_empty_structures(value)

                # Remove empty or None values
                if value in (None, {}, []) or (
                    isinstance(value, list) and all(v is None for v in value)
                ):
                    del data[key]

        elif isinstance(data, list):
            # Clean nested structures
            for item in data:
                if isinstance(item, (dict, list)):
                    self._clean_empty_structures(item)

            # Remove None values and empty structures
            while None in data:
                data.remove(None)

            # Remove empty dictionaries and lists
            data[:] = [item for item in data if item not in ({}, [])]

    def _cleanse_field_path(self, field_path: str) -> str:
        if field_path.startswith("args[") or "." in field_path:
            if field_path.startswith("args["):
                field_path = self._handle_args_syntax(field_path)
            else:
                field_path = self._handle_kwargs_syntax(field_path)

        if "(" in field_path and ")" in field_path:
            field_path = self._handle_field_selection(field_path)

        return f"$.{field_path}"

    def _handle_args_syntax(self, field_path: str) -> str:
        """Handle args[N] syntax in field paths."""
        # Extract the argument index
        arg_index = int(field_path[field_path.index("[") + 1 : field_path.index("]")])

        # Get the actual parameter name from inspect.signature
        sig = inspect.signature(self.orig_func)
        param_names = list(sig.parameters.keys())

        # Extract the rest of the path after args[N]
        rest_of_path = self._extract_rest_of_path(field_path)

        # For *args parameter, keep the args[N] syntax
        if any(param.kind == param.VAR_POSITIONAL for param in sig.parameters.values()):
            return f"args[{arg_index}]" + (f".{rest_of_path}" if rest_of_path else "")

        # For named parameters, use the parameter name
        if arg_index < len(param_names):
            return param_names[arg_index] + (f".{rest_of_path}" if rest_of_path else "")

        return field_path

    def _handle_kwargs_syntax(self, field_path: str) -> str:
        """Handle kwargs syntax in field paths."""
        sig = inspect.signature(self.orig_func)
        if any(param.kind == param.VAR_KEYWORD for param in sig.parameters.values()):
            return f"kwargs.{field_path}"
        return field_path

    def _handle_field_selection(self, field_path: str) -> str:
        """Handle (field1, field2) syntax in field paths."""
        pre_paren = field_path[: field_path.index("(")]
        post_paren = field_path[field_path.index(")") + 1 :]
        fields_list = [
            f.strip()
            for f in field_path[
                field_path.index("(") + 1 : field_path.index(")")
            ].split(",")
        ]

        paths = [f"$.{pre_paren}['{field}']{post_paren}" for field in fields_list]
        return " | ".join(paths)

    def _extract_rest_of_path(self, field_path: str) -> str:
        """Extract the path after args[N] and clean it."""
        rest_of_path = field_path[field_path.index("]") + 1 :]
        if rest_of_path.startswith("."):
            rest_of_path = rest_of_path[1:]
        return rest_of_path

    def _write_output(self, data: Dict[str, Any]) -> None:
        # Get the outermost function name
        outermost_function = data["FUNCTION"]

        # Ensure we have valid session data
        if self.session_id is None or self.session_start_time is None:
            raise RuntimeError("Session ID or start time not initialized")

        # Generate filepath using the new function
        filepath = get_snapshot_filepath(
            self.session_id, outermost_function, self.session_start_time
        )

        # Pre-process the data to ensure all dictionary keys are strings
        sanitized_data = _sanitize_dict_keys(data)

        # Write the file
        with open(filepath, "w") as f:
            json_string = json.dumps(sanitized_data, cls=CustomJSONEncoder)
            beautified_json = jsbeautifier.beautify(json_string)
            f.write(beautified_json)

    def _construct_final_output(self) -> Dict[str, Any]:
        if self.inner_calls:
            # Pre-process the data before constructing output
            sanitized_calls = _sanitize_dict_keys(self.inner_calls)
            final_output = {
                "FUNCTION": sanitized_calls[0]["FUNCTION"],
                "INPUTS": sanitized_calls[0]["INPUTS"],
            }

            # Add either OUTPUT or ERROR, but not both
            if "ERROR" in sanitized_calls[0]:
                final_output["ERROR"] = sanitized_calls[0]["ERROR"]
            elif "OUTPUT" in sanitized_calls[0]:
                final_output["OUTPUT"] = sanitized_calls[0]["OUTPUT"]

            if "CALLS" in sanitized_calls[0] and sanitized_calls[0]["CALLS"]:
                final_output["CALLS"] = sanitized_calls[0]["CALLS"]
            return final_output
        return {}

    def _process_output_fields(self, result: Any) -> Any:
        """Process output fields selection if specified, otherwise return original result."""
        if not self.output_fields:
            return result

        # Convert to dict for processing
        result_dict = json.loads(json.dumps(result, cls=CustomJSONEncoder))

        # For array access from root, don't wrap in _output
        if any(field.startswith("[") for field in self.output_fields):
            for field_path in self.output_fields:
                try:
                    matches = self._extract_field_values(result_dict, f"$.{field_path}")
                    if matches:
                        # For array outputs, build the array structure
                        output_array = []
                        current_idx = -1
                        current_obj = {}

                        for match in matches:
                            if match.value is not None:
                                # Get the parent object index from the path
                                path_parts = str(match.full_path).split("[")
                                if len(path_parts) > 1:
                                    idx = int(path_parts[1].split("]")[0])
                                    if idx != current_idx:
                                        if current_obj and current_idx >= 0:
                                            output_array.append(current_obj)
                                        current_obj = {}
                                        current_idx = idx

                                # Add the field to the current object
                                field_name = str(match.path).split(".")[-1]
                                current_obj[field_name] = match.value

                        # Add the last object if exists
                        if current_obj:
                            output_array.append(current_obj)

                        return output_array
                except Exception:
                    continue
            return result

        # Create a wrapper dict to use existing field selection logic
        wrapped_result = {"_output": result_dict}

        # Modify field paths to work with wrapper
        modified_fields = [f"_output.{field}" for field in self.output_fields]

        # Use existing field selection logic
        extracted = self._extract_and_format_fields(
            wrapped_result, modified_fields, False
        )

        if not extracted or "_output" not in extracted:
            return result

        return extracted["_output"]

    def capture(self, *args: Any, **kwargs: Any) -> Any:
        """Capture function inputs and outputs."""
        # Skip if debug mode is not enabled
        if not _is_debug_enabled():
            return self.func(*args, **kwargs)

        # Prepare call data and set up context
        current_call_data = self._prepare_call_data(args, kwargs)
        parent_call_data = self.inner_calls[-1] if not self.is_outermost else None

        # Add current call to the call stack
        self.inner_calls = self.inner_calls + [current_call_data]
        inner_calls_var.set(self.inner_calls)

        # Always call the original function directly and store its result or exception
        original_exception = None
        original_result = None
        try:
            # Execute the function
            original_result = self.func(*args, **kwargs)

            # Process the successful result
            try:
                # Extract and format input fields if specified
                extracted_input = self._extract_and_format_fields(
                    current_call_data["INPUTS"], self.input_fields, True
                )
                if extracted_input:
                    current_call_data["INPUTS"] = extracted_input

                # Process output fields for debug snapshot
                current_call_data["OUTPUT"] = self._process_output_fields(
                    original_result
                )
            except Exception as e:
                # If field processing fails, log it but continue
                logger.debug(
                    f"Detective field processing error: {self.func.__name__} - {str(e)}"
                )
        except Exception as e:
            # Capture the original exception
            original_exception = e
            try:
                # Record the error in the call data
                if "OUTPUT" in current_call_data:
                    del current_call_data["OUTPUT"]
                current_call_data["ERROR"] = {
                    "type": original_exception.__class__.__name__,
                    "message": str(original_exception),
                }
            except Exception as processing_error:
                # If error processing fails, log it but continue
                logger.debug(
                    f"Detective error processing error: {self.func.__name__} - {str(processing_error)}"
                )

        try:
            # Update the call hierarchy
            if not self.is_outermost and parent_call_data is not None:
                # Add this call to parent's CALLS list
                if "CALLS" not in parent_call_data:
                    parent_call_data["CALLS"] = []
                parent_call_data["CALLS"].append(current_call_data)

                # Remove this call from the stack as we're returning to parent
                self.inner_calls = self.inner_calls[:-1]
                inner_calls_var.set(self.inner_calls)
            elif self.is_outermost:
                # For outermost calls, write the complete call tree to a file
                final_output = self._construct_final_output()
                self._write_output(final_output)
                inner_calls_var.set([])
        except Exception as e:
            # If call hierarchy processing fails, log it but continue
            logger.debug(
                f"Detective call hierarchy error: {self.func.__name__} - {str(e)}"
            )
            # Make sure we clean up context vars
            if self.is_outermost:
                inner_calls_var.set([])

        # Always propagate the original function's behavior exactly
        if original_exception:
            raise original_exception
        return original_result


def snapshot(
    input_fields: Optional[List[str]] = None,
    output_fields: Optional[List[str]] = None,
    include_implicit: bool = False,
) -> Callable:
    """Decorator to capture function inputs and outputs.

    Args:
        input_fields: Optional list of input fields to capture
        output_fields: Optional list of output fields to capture
        include_implicit: Whether to include 'self' or 'cls' in the captured inputs
                          even when not explicitly referenced in input_fields

    Returns:
        Decorated function
    """

    def decorator(func: Any) -> Any:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Skip if debug mode is not enabled
            if not _is_debug_enabled():
                return func(*args, **kwargs)

            snapshotter = Snapshotter(
                func, input_fields, output_fields, include_implicit
            )

            return snapshotter.capture(*args, **kwargs)

        return wrapper

    return decorator
