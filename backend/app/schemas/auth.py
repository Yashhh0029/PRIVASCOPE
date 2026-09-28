import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError("Invalid email format")
        return v

class UserLogin(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str

class GoogleAuthRequest(BaseModel):
    credential: Optional[str] = Field(None, description="Google ID Token issued by Google Identity Services")
    id_token: Optional[str] = Field(None, description="Alias for Google ID Token")

    @model_validator(mode="after")
    def validate_credential(self):
        token = self.credential or self.id_token
        if not token:
            raise ValueError("Google authentication requires 'credential' or 'id_token'")
        self.credential = token
        return self

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    auth_provider: str = "local"
    email_verified: bool = False
    avatar_url: Optional[str] = None
    is_active: bool = True
    last_login_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
