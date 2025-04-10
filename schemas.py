from pydantic import BaseModel, Field
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = Field(default="")
    email: str

    class Config:
        from_attributes = True

class UserPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None