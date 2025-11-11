
from fastapi import APIRouter,status,HTTPException,Depends
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import models,utils,oauth2
from app.database import get_db
from sqlalchemy import text
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import Token  # if you have a Token schema

router=APIRouter(tags=['Authentication'])


#Admin or customer login
@router.post("/admin/login")
def admin_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == form_data.username).first()
    if not admin or not utils.verify(form_data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = oauth2.create_access_token({"user_id": admin.id, "user_type": "admin"})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/customer/login")
def customer_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.email == form_data.username).first()
    if not customer or not utils.verify(form_data.password, customer.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = oauth2.create_access_token({"user_id": customer.id, "user_type": "customer"})
    return {"access_token": token, "token_type": "bearer"}
