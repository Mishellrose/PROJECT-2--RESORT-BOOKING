
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional,Literal


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    user_type: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime
    class Config():
        orm_mode= True

class LoginIn(BaseModel):
    email: EmailStr
    password: str
    user_type: str
    
    