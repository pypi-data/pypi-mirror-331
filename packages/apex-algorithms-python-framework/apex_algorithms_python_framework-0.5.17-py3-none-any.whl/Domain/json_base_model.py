from dataclasses import dataclass, asdict, fields, is_dataclass
from datetime import datetime, time
from typing import Any, Dict, Type, TypeVar, Union, get_origin, get_args, List
from enum import Enum
import json

T = TypeVar("T", bound="JsonBaseModel")

@dataclass
class JsonBaseModel:
    """
    A generic base class for models with dataclass support.
    Provides automatic JSON encode and decode methods.
    """

    @classmethod
    def decode(cls: Type[T], data: Union[str, Dict[str, Any]]) -> T:
        """
        Decodes a JSON string or dictionary into an instance of the class.

        Args:
            data: A JSON string or dictionary representing the object.

        Returns:
            An instance of the class.

        Raises:
            ValueError: If the data is invalid or required fields are missing.
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {e}")

        parsed_data = {}
        for field in fields(cls):
            field_name = field.name
            field_type = field.type

            if field_name in data:
                value = data[field_name]

                # Convert datetime strings
                if field_type == datetime and isinstance(value, str):
                    parsed_data[field_name] = datetime.fromisoformat(value)

                # Convert time strings
                elif field_type == time and isinstance(value, str):
                    parsed_data[field_name] = time.fromisoformat(value)

                # Convert Enums
                elif isinstance(field_type, type) and issubclass(field_type, Enum):
                    parsed_data[field_name] = field_type(value)

                # If the field is another dataclass, decode it
                elif is_dataclass(field_type) and issubclass(field_type, JsonBaseModel):
                    parsed_data[field_name] = field_type.decode(value)

                # Handle lists of nested dataclasses
                elif get_origin(field_type) is list:
                    item_type = get_args(field_type)[0]
                    if is_dataclass(item_type) and issubclass(item_type, JsonBaseModel):
                        parsed_data[field_name] = [item_type.decode(item) for item in value]
                    else:
                        parsed_data[field_name] = value

                else:
                    parsed_data[field_name] = value

            # Use default values if not in data
            elif field.default is not None or field.default_factory is not None:
                parsed_data[field_name] = field.default if field.default != field.default_factory else field.default_factory()
            else:
                raise ValueError(f"Missing required field: {field_name}")

        return cls(**parsed_data)

    def encode(self) -> str:
        """
        Encodes the instance into a JSON string.

        Returns:
            A JSON string representation of the instance.
        """
        return json.dumps(self._to_serializable_dict(), indent=4)

    def _to_serializable_dict(self):
        """
        Converts the instance into a serializable dictionary.

        Returns:
            A dictionary representation of the instance with proper serialization.
        """
        result = {}
        for field in fields(self):
            value = getattr(self, field.name)

            # Convert nested dataclasses properly
            if isinstance(value, JsonBaseModel):
                result[field.name] = value._to_serializable_dict()

            # Convert lists of dataclasses
            elif isinstance(value, list) and all(isinstance(item, JsonBaseModel) for item in value):
                result[field.name] = [item._to_serializable_dict() for item in value]

            # Use the existing custom serialization for enums, datetime, etc.
            else:
                result[field.name] = self.__custom_serializer(value)

        return result

    def __custom_serializer(self, obj):
        """
        Custom serializer for JSON encoding.

        Args:
            obj: The object to serialize.

        Returns:
            Serialized representation of the object.

        Raises:
            TypeError: If the object type is not serializable.
        """
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, time):
            return obj.isoformat()
        if is_dataclass(obj):
            return obj._to_serializable_dict()
        if isinstance(obj, list):
            return [self.__custom_serializer(item) for item in obj]
        if isinstance(obj, dict):
            return {key: self.__custom_serializer(value) for key, value in obj.items()}
        raise TypeError(f"Type {type(obj)} not serializable")
