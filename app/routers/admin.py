from fastapi import APIRouter,status,HTTPException,Depends,File,UploadFile
from app import schemas,models,utils,oauth2
from app.database import get_db
from sqlalchemy.orm import Session
import shutil
from fastapi.security.oauth2 import OAuth2PasswordRequestForm




#admin routre..where admin can add staff that can do the work

router=APIRouter(prefix="/admin",tags=['ADMIN'])
#adding staff or staff registration

@router.post("/addstaff",status_code=status.HTTP_201_CREATED,response_model=schemas.StaffOut)
def add_new_staff(staff: schemas.AddStaff,db:Session= Depends(get_db)):
    hashed_password=utils.hash(staff.password)
    staff.password=hashed_password

    new_staff=models.Staff(**staff.dict())
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)

    return new_staff

#STAFF LOGIN
@router.post("/StaffLogin")
def staff_Login(staff_credens: OAuth2PasswordRequestForm=Depends(),db:Session = Depends(get_db)):
    staff=db.query(models.Staff).filter(models.Staff.email==staff_credens.username).first()
    if not staff:
        raise HTTPException(status_code=403,detail=f'Invalid Credentials')
    if not utils.verify(staff_credens.password, staff.password):
        raise HTTPException(status_code=403,detail=f'Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={"user_id":staff.id})
    return {"access_token":access_token, "token_type":"bearer"}
    



@router.post("/staff_dp/{staff_id}")
def upload_dp(file: UploadFile,staff_id: int, current_staff= Depends(oauth2.get_current_staff), db:Session = Depends(get_db)):
    db_staff= db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    if db_staff.id != current_staff.id:
        raise HTTPException(status_code=404, detail="Not allowed to update this profile")
    
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_staff.photo = file_location
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)

    return db_staff






