# gorest_api_tests/src/models/user_models.py
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Gender(str, Enum):
    """Enum for user gender."""
    MALE = "male"
    FEMALE = "female"

class Status(str, Enum):
    """Enum for user status."""
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserCreate(BaseModel):
    """
    Pydantic model for creating a new user.
    Represents the payload for POST /users.
    """
    name: str = Field(min_length=1, description="Name of the user")
    email: EmailStr = Field(description="Unique email address of the user")
    gender: Gender = Field(description="Gender of the user (male/female)")
    status: Status = Field(description="Status of the user (active/inactive)")

class UserUpdate(BaseModel):
    """
    Pydantic model for updating an existing user.
    Represents the payload for PATCH /users/{id}.
    All fields are optional for partial updates.
    """
    name: Optional[str] = Field(None, min_length=1, description="Optional new name for the user")
    email: Optional[EmailStr] = Field(None, description="Optional new email address for the user")
    gender: Optional[Gender] = Field(None, description="Optional new gender for the user")
    status: Optional[Status] = Field(None, description="Optional new status for the user")

class User(UserCreate):
    """
    Pydantic model for a full user object, including the ID.
    Inherits from UserCreate for common fields and adds the 'id'.
    Represents the response body for GET /users/{id}, POST /users, PATCH /users/{id}.
    """
    id: int = Field(gt=0, description="Unique ID of the user, must be a positive integer")

# Note: GoRest API returns a list of users for GET /users,
# but for simplicity in this test suite, we focus on single user operations.
# If needed, a RootModel[List[User]] could be added for list responses.
