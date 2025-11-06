
from fastapi import Depends,HTTPException,status
from app.config import settings
from datetime import datetime,timedelta
from sqlalchemy.orm import Session
from jose import JWTError,jwt
from app.database import get_db
from app import schemas,models
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/login')
oauth2_scheme2=OAuth2PasswordBearer(tokenUrl='/admin/StaffLogin')



SECRET_KEY= settings.secret_key
ALGORITHM= settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=settings.access_token_expire_minutes

def create_access_token(data:dict):
    to_encode=data.copy()
    expire= datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp" : expire})
    encoded_jwt= jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str,credentials_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        id: str=payload.get("user_id")
        if not id:
            raise credentials_exception
        token_data=schemas.token_data(id=id)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_staff(
    token: str = Depends(oauth2_scheme2),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exception)

    staff = db.query(models.Staff).filter(models.Staff.id == token.id).first()
    if not staff:
        raise credentials_exception

    return staff
