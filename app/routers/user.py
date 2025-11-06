
from fastapi import APIRouter,Depends,status,HTTPException
from app import models,schemas,utils
from app.database import get_db
from sqlalchemy.orm import Session

#REGISTRATIONN

router=APIRouter(prefix="/user",tags=['Register'])

@router.post("/",response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate,status_code=status.HTTP_201_CREATED,db:Session=Depends(get_db)):
    hashed_password=utils.hash(user.password)
    user.password=hashed_password

    if user.user_type == "admin" :
        new_user=models.Admin(name=user.name,email=user.email,password=hashed_password,user_type=user.user_type)
    elif user.user_type == "customer":
        new_user=models.Customer(name=user.name,email=user.email,password=hashed_password,user_type=user.user_type)
    else:
        raise HTTPException(status_code=404, detail="Unable to Register")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



