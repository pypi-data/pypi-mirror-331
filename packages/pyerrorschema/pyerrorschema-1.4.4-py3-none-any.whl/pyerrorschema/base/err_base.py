import inspect
import json
import textwrap
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self, TypeVar

from ..utils import get_parent_class, restrict_arguments

ErrorSchemaType = TypeVar("ErrorSchemaType", bound="ErrorSchema")


class ErrorSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(default="")
    msg: str = Field(default="")

    def __repr__(self) -> str:
        attrs = [f"{k}={repr(v)}" for k, v in self.model_dump().items() if not k.startswith('_')]
        attrs_str = textwrap.indent(',\n'.join(attrs), '    ')
        return f"{self.__class__.__name__}(\n{attrs_str}\n)"

    def __str__(self) -> str:
        return self.__repr__()

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def to_string(self) -> str:
        """Convert the error schema to a string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def list_available_errors(cls) -> List[str]:
        """List all available error types."""
        return [
            name
            for name, _ in inspect.getmembers(cls, predicate=inspect.ismethod)
            if name.endswith("_error") and not name.startswith("_")
        ]

    ### Factory methods ###

    @classmethod
    def _create_error(cls, error_type: str, default_msg: str, **kwargs) -> Self:
        """Base factory method to create an instance for an error.

        It will format the error message be like:
        <readable_error_type>: <msg>

        where <readable_error_type> is the error type with underscores replaced
        by spaces and capitalized, e.g. "validation_error" -> "Validation error".
        If the "exc" argument is provided, it will be used as the error message.
        Otherwise, the "msg" argument will be used as the error message.

        Priority order:
        1. exc
        2. msg
        3. default_msg

        Args:
            error_type (str): The type of the error.
            default_msg (str): The default message of the error.
            **kwargs: Additional keyword arguments to pass to the error schema.

        Returns:
            ErrorSchema: The error schema instance.
        """

        msg = kwargs.pop("msg", default_msg)
        if "exc" in kwargs:
            msg += f" ({str(kwargs['exc'])})"

        pretty_type = error_type.replace("_", " ").capitalize()
        msg = msg[0].lower() + msg[1:]

        return cls(
            type=error_type,
            msg=f"{pretty_type}: {msg}",
            **kwargs,
        )

    @classmethod
    @restrict_arguments("type")
    def database_error(cls, **kwargs) -> Self:
        """Factory method to create an instance for a database error."""
        return cls._create_error("database_error", "Database error occurred.", **kwargs)

    @classmethod
    @restrict_arguments("type")
    def file_error(cls, **kwargs) -> Self:
        """Factory method to create an instance for a file error."""
        return cls._create_error("file_error", "File error occurred.", **kwargs)

    @classmethod
    @restrict_arguments("type")
    def runtime_error(cls, **kwargs) -> Self:
        """Factory method to create an instance for a runtime error."""
        return cls._create_error("runtime_error", "Runtime error occurred.", **kwargs)

    @classmethod
    @restrict_arguments("type")
    def parse_error(cls, **kwargs) -> Self:
        """Factory method to create an instance for a parse error."""
        return cls._create_error("parse_error", "Parse error occurred.", **kwargs)

    @classmethod
    @restrict_arguments("type")
    def value_error(cls, **kwargs) -> Self:
        """Factory method to create an instance for a value error."""
        return cls._create_error("value_error", "Value error occurred.", **kwargs)

    @classmethod
    def customized_error(cls, **kwargs) -> Self:
        """Factory method to create an instance for a customized error."""
        error_type = kwargs.pop("type", "customized_error")
        return cls._create_error(error_type, "Customized error occurred.", **kwargs)

    ## Subclasses ##

    class Base(ABC):
        """Base class for all error schema subclasses.

        This class provides a general error method for all error schema subclasses.
        Each subclass can define its own `display_name` attribute to customize the
        error message prefix. If not set, the class name will be used.

        Example:
            class File(Base):
                # Uses class name in error messages
                pass

            class DB(Base):
                # Customizes error message prefix
                display_name: str = "Database"

            # Usage examples:
            File.general(action="reading config.json")
            # Output: "File error occurred while reading config.json."

            DB.general(reason="connection timeout")
            # Output: "Database error occurred since connection timeout."

        The error method will automatically use the corresponding error factory
        (e.g., file_error for File class) from the parent class. If no matching
        error factory exists, it falls back to customized_error.
        """
        display_name: Optional[str] = None

        @classmethod
        def _get_name(cls) -> str:
            """Get the display name for error message formatting.

            Returns the custom name if it is defined, otherwise returns the class name.
            """
            return cls.display_name or cls.__name__

        @classmethod
        @abstractmethod
        def general(
            cls,
            *,
            action: Optional[str] = None,
            reason: Optional[str] = None,
            **kwargs,
        ):
            """Create a general error instance for this error type.

            The error message will be formatted in one of two ways:
            - "<name> error occurred while <action>."
            - "<name> error occurred since <reason>."

            Args:
                action: Description of the action being performed when the error occurred.
                    Example: "reading file", "connecting to database"
                reason: Description of why the error occurred.
                    Example: "invalid format", "connection timeout"
                **kwargs: Additional keyword arguments to pass to the error factory method.

            Raises:
                ValueError: If both action and reason are provided.

            Returns:
                An error instance with the formatted message.
            """

            if action and reason:
                raise ValueError("Only one of 'action' or 'reason' should be provided.")

            name = cls._get_name()
            if action:
                kwargs["msg"] = f"{name} error occurred while {action}."
            elif reason:
                kwargs["msg"] = f"{name} error occurred since {reason}."

            error_method = f"{name.lower()}_error"
            parent_cls = get_parent_class(cls)
            if hasattr(parent_cls, error_method):
                return getattr(parent_cls, error_method)(**kwargs)

            return get_parent_class(cls).customized_error(type=error_method, **kwargs)

    class File(Base):
        """Error schema for file operations.

        Provides methods for common file operation errors with automatic path type detection
        (file vs directory) for more precise error messages.

        Examples:
            >>> File.not_found(path="config.json")
            "File 'config.json' not found."

            >>> File.not_found(path="data/")
            "Directory 'data/' not found."

            >>> File.writing(path="output.txt")
            "Writing to file 'output.txt' failed."
        """

        @classmethod
        def _path_type(cls, path: str) -> str:
            """Get the type of the path."""
            return "file" if Path(path).suffix else "directory"

        @classmethod
        def not_found(cls, path: str, **kwargs):
            """File not found error for a given path."""
            path_type = cls._path_type(path)
            return get_parent_class(cls).file_error(
                msg=f"{path_type.capitalize()} '{path}' not found.", **kwargs,
            )

        @classmethod
        def already_exists(cls, path: str, **kwargs):
            """File already exists error for a given path."""
            path_type = cls._path_type(path)
            return get_parent_class(cls).file_error(
                msg=f"{path_type.capitalize()} '{path}' already exists.", **kwargs,
            )

        @classmethod
        def creating(cls, path: str, **kwargs):
            """Creating error for a given path."""
            path_type = cls._path_type(path)
            return get_parent_class(cls).file_error(
                msg=f"Creating {path_type} '{path}' failed.", **kwargs,
            )

        @classmethod
        def writing(cls, path: str, **kwargs):
            """Writing error for a given path."""
            path_type = cls._path_type(path)
            return get_parent_class(cls).file_error(
                msg=f"Writing to {path_type} '{path}' failed.", **kwargs,
            )

        @classmethod
        def reading(cls, path: str, **kwargs):
            """Reading error for a given path."""
            path_type = cls._path_type(path)
            return get_parent_class(cls).file_error(
                msg=f"Reading from {path_type} '{path}' failed.", **kwargs,
            )

        @classmethod
        def deleting(cls, path: str, **kwargs):
            """Deleting error for a given path."""
            path_type = cls._path_type(path)
            return get_parent_class(cls).file_error(
                msg=f"Deleting {path_type} '{path}' failed.", **kwargs,
            )

        @classmethod
        def copying(cls, path: str, **kwargs):
            """Copying error for a given path."""
            path_type = cls._path_type(path)
            return get_parent_class(cls).file_error(
                msg=f"Copying {path_type} '{path}' failed.", **kwargs,
            )

        @classmethod
        def saving(cls, path: str, **kwargs):
            """Saving error for a given path.

            only file is supported for this method.
            """
            return get_parent_class(cls).file_error(
                msg=f"Saving file '{path}' failed.", **kwargs,
            )

    class Map(Base):
        display_name: str = "Dict"

        @classmethod
        def missing_keys(cls, keys: List[str], **kwargs):
            """Missing keys error for a given keys."""
            concat_keys = "', '".join(keys)
            return get_parent_class(cls).customized_error(
                type="dict_error",
                msg=f"Keys ('{concat_keys}') not found in dictionary.", **kwargs,
            )

    class DB(Base):
        display_name: str = "Database"

        @classmethod
        def no_results(cls, desc: str, **kwargs):
            """No results when querying a database.

            Format for the message: "No results found while <desc>."
            """
            return get_parent_class(cls).database_error(
                msg=f"No results found while {desc}.", **kwargs,
            )
        @classmethod
        def foreign_key_violation(cls, **kwargs):
            """Foreign key violation error."""
            return get_parent_class(cls).database_error(
                msg="Foreign key violation occurred.", **kwargs,
            )

    class Parse(Base):
        display_name: str = "Parse"

        @classmethod
        def invalid_format(cls, expected_format: str, actual_format: str, **kwargs):
            """Invalid format error."""
            return get_parent_class(cls).parse_error(
                msg=f"Expected format '{expected_format}', but got '{actual_format}'.", **kwargs,
            )

        @classmethod
        def inputs_length_inconsistent(cls, **kwargs):
            """Inputs length inconsistent error."""
            return get_parent_class(cls).parse_error(
                msg="The length of inputs is inconsistent.", **kwargs,
            )

    class Value(Base): ...

    class Runtime(Base): ...

    class Assumbly(Base): ...

    class Unknown(Base): ...
