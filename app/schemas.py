
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional,Literal


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    user_type: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    user_type: str
    created_at: datetime
    class Config():
        orm_mode= True

class LoginIn(BaseModel):
    email: EmailStr
    password: str
    user_type: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class AddStaff(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_no: str
    salary: str
     
    
class StaffOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    start_date: datetime
    phone_no: str
    salary: str
    class Config():
        orm_mode= True   

class StaffDpOut(BaseModel):
    staff: StaffOut
    photo: str   

class token_data(BaseModel):
    id: Optional[int] = None
