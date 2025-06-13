from pydantic import BaseModel as PydanticBaseModel, ConfigDict
from typing import Any, Dict

class BaseModel(PydanticBaseModel):
    """Base model for all schemas with common configuration"""
    
    model_config = ConfigDict(
        # Allow population by field name or alias
        populate_by_name=True,
        # Use enum values instead of enum names in JSON
        use_enum_values=True,
        # Validate assignment when setting attributes
        validate_assignment=True,
        # Allow arbitrary types (useful for some complex types)
        arbitrary_types_allowed=True,
        # Convert string to datetime and other type conversions
        str_strip_whitespace=True,
        # Generate examples in OpenAPI schema
        json_schema_extra={
            "examples": []
        }
    )

class BaseResponse(BaseModel):
    """Base response model for API responses"""
    success: bool = True
    message: str = ""
    errors: Dict[str, Any] = {}

class PaginatedResponse(BaseResponse):
    """Base model for paginated responses"""
    total: int = 0
    page: int = 1
    per_page: int = 10
    total_pages: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.total > 0 and self.per_page > 0:
            self.total_pages = (self.total + self.per_page - 1) // self.per_page