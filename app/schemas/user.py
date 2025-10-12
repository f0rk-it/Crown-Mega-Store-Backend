from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    google_id: str
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: str
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class GoogleAuthRequest(BaseModel):
    token: str
    

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserResponse