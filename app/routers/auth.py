
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

class OAuth2PasswordRequestFormWithUserType(OAuth2PasswordRequestForm):
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        user_type: str = Form(...),  # 👈 only new field you need
    ):
        super().__init__(username=username, password=password, scope="")
        self.user_type = user_type



@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestFormWithUserType = Depends(),
    db: Session = Depends(get_db),
):
    # Pick the correct table based on user_type
    if form_data.user_type == "admin":
        user = db.query(models.Admin).filter(models.Admin.email == form_data.username).first()
    elif form_data.user_type == "customer":
        user = db.query(models.Customer).filter(models.Customer.email == form_data.username).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")

    # Verify user existence and password
    if not user or not utils.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )

    # Create JWT token (with user_type for later verification)
    access_token = oauth2.create_access_token(
        data={"user_id": user.id, "user_type": form_data.user_type}
    )

    return {"access_token": access_token, "token_type": "bearer"}
