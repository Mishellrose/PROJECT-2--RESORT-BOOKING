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




