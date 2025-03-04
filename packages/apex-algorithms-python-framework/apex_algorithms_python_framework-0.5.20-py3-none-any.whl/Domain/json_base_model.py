from dataclasses import dataclass, asdict, fields
from datetime import datetime
from typing import Any, Dict, Type, TypeVar, Union, get_origin, get_args
from enum import Enum
import json

T = TypeVar("T", bound="JsonBaseModel")

@dataclass
class JsonBaseModel:
    """
    A generic base class for models with dataclass support.
    Provides generic encode and decode methods.
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

                if field_type == datetime and isinstance(value, str):
                    parsed_data[field_name] = datetime.fromisoformat(value)

                elif isinstance(field_type, type) and issubclass(field_type, Enum):
                    if isinstance(value, str) and value.startswith(f"{field_type.__name__}."):
                        value = value.split(".", 1)[1]
                    parsed_data[field_name] = field_type(value)

                elif hasattr(field_type, "__dataclass_fields__"):
                    parsed_data[field_name] = field_type.decode(value)

                elif get_origin(field_type) is list:
                    item_type = get_args(field_type)[0]
                    if hasattr(item_type, "__dataclass_fields__"):
                        parsed_data[field_name] = [item_type.decode(item) for item in value]
                    else:
                        parsed_data[field_name] = value

                elif hasattr(field_type, "decode") and callable(getattr(field_type, "decode")):
                    parsed_data[field_name] = field_type.decode(value)

                else:
                    parsed_data[field_name] = value

            elif field.default is not None or field.default_factory is not None:
                parsed_data[field_name] = field.default if field.default != field.default_factory else field.default_factory()
            else:
                raise ValueError(f"Missing required field: {field_name}")

        return cls(**parsed_data)

    def __custom_serializer(self, obj):
        """
        Private serializer for JSON encoding, only accessible within BaseModel.

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
        if hasattr(obj, "__dataclass_fields__"):
            return {**asdict(obj), "__class__": obj.__class__.__name__}
        if isinstance(obj, list):
            return [self.__custom_serializer(item) for item in obj]
        if isinstance(obj, dict):
            return {key: self.__custom_serializer(value) for key, value in obj.items()}
        raise TypeError(f"Type {type(obj)} not serializable")

    def encode(self) -> str:
        """
        Encodes the instance into a JSON string.

        Returns:
            A JSON string representation of the instance, including the class name.
        """
        serialized_data = asdict(self)
        serialized_data["__class__"] = self.__class__.__name__
        return json.dumps(serialized_data, default=self.__custom_serializer, indent=4)