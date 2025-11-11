
from fastapi import Depends,HTTPException,status
from app.config import settings
from datetime import datetime,timedelta
from sqlalchemy.orm import Session
from jose import JWTError,jwt
from app.database import get_db
from app import schemas,models
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/customer/login")



SECRET_KEY= settings.secret_key
ALGORITHM= settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=settings.access_token_expire_minutes

def create_access_token(data:dict):
    to_encode=data.copy()
    expire= datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp" : expire})
    encoded_jwt= jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        user_type: str = payload.get("user_type")

        if not user_id:
            raise credentials_exception

        token_data = schemas.token_data(id=user_id, user_type=user_type)
    except JWTError:
        raise credentials_exception

    return token_data



def get_current_staff(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    if token_data.user_type != "staff":
        raise HTTPException(status_code=403, detail="Not authorized as staff")

    staff = db.query(models.Staff).filter(models.Staff.id == token_data.id).first()
    if not staff:
        raise credentials_exception

    return staff

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)

    
    return token_data

def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)

    # Ensure token belongs to admin
    if token_data.user_type != "admin":
        raise HTTPException(status_code=403, detail="Not authorized as admin")

    admin = db.query(models.Admin).filter(models.Admin.id == token_data.id).first()
    if not admin:
        raise credentials_exception

    return admin



def get_current_customer(user_id : int , db:Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    current_customer= db.query(models.Customer).filter(models.Customer.id == user_id).first()
    return current_customer


#function to find ehther token is admin or staff
def get_crnt_stafforadmin(token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    if token_data.user_type == "admin" :
        user = db.query(models.Admin).filter(models.Admin.id == token_data.id).first()
    elif token_data.user_type == "staff":
        user = db.query(models.Staff).filter(models.Staff.id == token_data.id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
    return user



