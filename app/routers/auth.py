
from fastapi import APIRouter,status,HTTPException,Depends
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import models,schemas,utils,oauth2
from app.database import get_db
from sqlalchemy import text


router=APIRouter(tags=['Authentication'])




@router.post("/login",response_model=schemas.Token)
def Login_user(user_credentials:schemas.LoginIn,db:Session=Depends(get_db)):
    type=user_credentials.user_type
    check_stmt=text(f"SELECT * FROM {type} WHERE email =: eid ;")
    match = db.execute(check_stmt, {"eid": user_credentials.email}).fetchone()
    if not match:
        raise HTTPException(status_code=403,detail=f'Invalid Credentials')
    if not utils.verify(user_credentials.password, check_stmt.password):
        raise HTTPException(status_code=403,detail=f'Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={"user_id":check_stmt.id})
    return {"access_token":access_token, "token_type":"bearer"}
