"""
Base models and common types
"""
from bson import ObjectId
from typing import Any
from pydantic_core import core_schema
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """
        Return a Pydantic CoreSchema that validates ObjectId values
        """
        def validate(value: Any) -> ObjectId:
            if isinstance(value, ObjectId):
                return value
            if isinstance(value, str):
                if ObjectId.is_valid(value):
                    return ObjectId(value)
                raise ValueError("Invalid ObjectId string")
            raise ValueError("Invalid ObjectId type")
        
        return core_schema.no_info_plain_validator_function(validate)
    
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return a JSON schema that represents ObjectId as a string"""
        return {"type": "string"}

