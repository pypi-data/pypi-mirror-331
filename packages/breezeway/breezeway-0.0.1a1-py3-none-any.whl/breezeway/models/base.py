import json
import logging
from dataclasses import fields
from typing import Type, TypeVar

T = TypeVar('T', bound='BaseBreezewayModel')


class BaseBreezewayModel:

    @classmethod
    def from_json(cls: Type[T], json_data: str | dict) -> T:
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        field_names = {field.name for field in fields(cls)}
        extra_keys = set(json_data.keys()) - field_names
        if extra_keys:
            logging.warning(f'Ignoring extra JSON values in {str(T)}: {extra_keys}')
        filtered_data = {k: v for k, v in json_data.items() if k in field_names}
        instance = cls(**filtered_data)
        instance.convert_data_types()  # Call method to convert data types after JSON import
        return instance

    def convert_data_types(self):
        """Method to convert data types after JSON import as needed. Add your implementation here."""
        pass
