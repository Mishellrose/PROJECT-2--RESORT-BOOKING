
from fastapi import APIRouter,Depends,status,HTTPException
from app import models,schemas,utils,oauth2
from app.database import get_db
from sqlalchemy.orm import Session

#REGISTRATIONN

router=APIRouter(prefix="/user",tags=['Register'])

@router.post("/",status_code=status.HTTP_201_CREATED)
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

    print(new_user)
     
    access_token = oauth2.create_access_token(
        data={"user_id": new_user.id, "user_type": user.user_type}
    )

    return {"access_token": access_token, "token_type": "bearer"}


    



