from sqlalchemy import Column, Float,Integer,String,TIMESTAMP,ForeignKey,Boolean,DateTime,Date
from app.database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime


class Admin(Base):
    __tablename__="admins"

    id=Column(Integer,primary_key=True,nullable=False)
    name=Column(String,nullable=False)
    email=Column(String,unique=True,nullable=False)
    password=Column(String,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    user_type=Column(String,nullable=False)

class Staff(Base):
    __tablename__="staffs"
    id=Column(Integer,primary_key=True,nullable=False)
    name=Column(String,nullable=False)
    email=Column(String,unique=True,nullable=False)
    password=Column(String,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    start_date= Column(DateTime, nullable=False, default=datetime.utcnow)
    phone_no= Column(String,nullable=False)
    photo= Column(String,nullable=True)
    salary= Column(String, nullable=False)



class Customer(Base):
    __tablename__="customers"
    id=Column(Integer,primary_key=True,nullable=False)
    name=Column(String,nullable=False)
    email=Column(String,unique=True,nullable=False)
    password=Column(String,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    user_type=Column(String,nullable=False)



class SingleRoom(Base):
    __tablename__="singleroom"
    id=Column(Integer,primary_key=True,nullable=False)
    admin_id=Column(Integer,ForeignKey("admins.id", ondelete="CASCADE"),nullable=False)
    room_no=Column(Integer,unique=True,nullable=False)
    category=Column(String,nullable=False)
    occupied=Column(Boolean,default=False)
    price=Column(Integer, default=2000)
    wifi=Column(Boolean,default=True, nullable=True)
    breakfast=Column(Boolean,default=True, nullable=True)
    AC=Column(Boolean,default=True, nullable=True)
    TV=Column(Boolean,default=True, nullable=True)

class DeluxeRoom(Base):
    __tablename__="deluxeroom"
    id=Column(Integer,primary_key=True,nullable=False)
    admin_id=Column(Integer,ForeignKey("admins.id", ondelete="CASCADE"),nullable=False)
    room_no=Column(Integer,unique=True,nullable=False)
    category=Column(String,nullable=False)
    occupied=Column(Boolean,default=False)
    price=Column(Integer, default=3000)
    wifi=Column(Boolean,default=True,nullable=False)
    breakfast=Column(Boolean,default=True,nullable=False)
    AC=Column(Boolean,default=True,nullable=False)
    TV=Column(Boolean,default=True, nullable=False)
    Car_parking=Column(Boolean,default=True, nullable=False) #extra
    Bath_tub=Column(Boolean,default=True, nullable=False)    #extra
    Open_kitchen=Column(Boolean,default=True, nullable=False) #extra

class CottageRoom(Base):
    __tablename__="cottageroom"
    id=Column(Integer,primary_key=True,nullable=False)
    admin_id=Column(Integer,ForeignKey("admins.id", ondelete="CASCADE"),nullable=False)
    room_no=Column(Integer,unique=True,nullable=False)
    category=Column(String,nullable=False)
    occupied=Column(Boolean,default=False)
    price=Column(Integer, default=6000)
    wifi=Column(Boolean,default=True,nullable=False)
    breakfast=Column(Boolean,default=True,nullable=False)
    AC=Column(Boolean,default=True,nullable=False)
    TV=Column(Boolean,default=True, nullable=False)
    Car_parking=Column(Boolean,default=True, nullable=False) 
    Bath_tub=Column(Boolean,default=True, nullable=False)    
    Open_kitchen=Column(Boolean,default=True, nullable=False)
    Private_pool=Column(Boolean,default=True, nullable=False) #extra
    Mini_fridge=Column(Boolean,default=True, nullable=False)  #extra
    Lake_access=Column(Boolean,default=True, nullable=False)  #extra


class Booking(Base):
    __tablename__= "bookings"
    booking_id  = Column(Integer, primary_key= True, nullable=False)
    customer_id=Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    category=Column(String, nullable=False)
    start_date=Column(Date, nullable=False)
    end_date=Column(Date, nullable=False)
    people_count=Column(Integer, nullable=False)
    booked_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    identity_type=Column(String, nullable=False)
    aadhar_front_image=Column(String, nullable=True)
    aadhar_back_image=Column(String, nullable=True)
    identity_image=Column(String, nullable=True)
    STATUS=Column(String, nullable=False, default="pending")  #pending, confirmed, cancelled
    room_no=Column(Integer, nullable=True)  #room assigned upon confirmation
    checked_in=Column(Boolean, nullable=True, default=False)
    checked_in_date=Column(DateTime, nullable=True)
    checked_out=Column(Boolean, nullable=True, default=False)
    checked_out_date=Column(DateTime, nullable=True)
    pool_used_by=Column(Integer, nullable=True)
    pool_used__start_date=Column(DateTime, nullable=True)

    total_amount=Column(Integer, nullable=True)
    advance_payment=Column(Integer, nullable=True)
    paid_amount = Column(Float, nullable=True, default=0.0)        # running total of payments made
    due_amount = Column(Float, nullable=True)
    payment_status=Column(String, nullable=True, default="PENDING")  #pen
    
    razorpay_payment_link=Column(String, nullable=True)
    feedback= Column(String, nullable=True) 
    Received_amount= Column(Float, nullable=True, default=0.0)


class Transaction(Base):
    __tablename__="transactions"

    transaction_id= Column(Integer,primary_key= True, nullable= False)
    event= Column(String, nullable= False)
    amount= Column(Float, nullable= False)
    mode_of_transaction= Column(String, nullable= False)
    transaction_date= Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    
    



