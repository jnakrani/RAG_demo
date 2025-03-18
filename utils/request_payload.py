from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

class UserUpdate(BaseModel):
    full_name: str = None
    email: EmailStr = None
    password: str = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str = None
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


