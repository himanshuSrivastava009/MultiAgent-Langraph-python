# gorest_api_tests/src/models/error_models.py
from pydantic import BaseModel, Field, RootModel
from typing import List

class ErrorDetail(BaseModel):
    """
    Pydantic model for a single error object returned by the GoRest API.
    Example: {"field": "email", "message": "has already been taken"}
    """
    field: str = Field(description="The field that caused the error")
    message: str = Field(description="The error message")

class ErrorResponse(RootModel[List[ErrorDetail]]):
    """
    Pydantic RootModel for validating the overall error response from GoRest API.
    The GoRest API typically returns a list of error objects directly,
    e.g., [{"field": "email", "message": "is invalid"}].
    RootModel[List[ErrorDetail]] correctly handles this structure.
    """
    pass
