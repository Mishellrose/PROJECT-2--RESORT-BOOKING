
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
    user_type: Optional[str] = None

class CreateRoom(BaseModel):
    room_no: int
    category: str
    occupied: Optional[bool] = False

class AllRoomsOut(BaseModel):
    rooms:str

class RoomOut(BaseModel):
    room_dets: AllRoomsOut


class SingleOut(BaseModel):
    category: str
    wifi: bool
    breakfast: bool
    AC: bool
    TV: bool
    class Config():
        from_attributes = True

class DeluxeOut(BaseModel):
    category: str
    wifi: bool
    breakfast: bool
    AC: bool
    TV: bool
    Car_parking: bool
    Bath_tub: bool
    Open_kitchen: bool
    class Config():
        from_attributes= True

class CottageOut(BaseModel):
    category: str
    wifi: bool
    breakfast: bool
    AC: bool
    TV: bool
    Car_parking: bool
    Bath_tub: bool
    Open_kitchen: bool
    Private_pool: bool
    Mini_fridge: bool
    Lake_access: bool
    class Config():
        from_attributes = True

class BookingDetsOut(BaseModel):
    customer_id: int
    
    
    
class GetBook(BaseModel):
    staff_id: int

class PoolCount(BaseModel):
    pool_used_by: int
    
class Feedback(BaseModel):
    comments: str

class StaffSalaryReduce(BaseModel):
    staff_id: int
    salary: int
    mode_of_transaction: Literal['cash', 'card', 'online']

class GetBookingfilters(BaseModel):
    filter_by: Optional[Literal["date_range", "customer_id", "category"]]= None
    start_date: Optional[datetime]= None
    end_date: Optional[datetime]= None
    customer_id: Optional[int]= None
    category: Optional[Literal["single room", "deluxe room", "cottage room"]]= None

class GetBookingfiltersOut(BaseModel):
    booking_id: int
    customer_id: int
    people_count: int
    room_no: Optional[int]= None

