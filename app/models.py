from sqlalchemy import Column,Integer,String,TIMESTAMP,ForeignKey,Boolean,DateTime,Date
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



