from fastapi import APIRouter,status,HTTPException,Depends,File,UploadFile
from app import schemas,models,utils,oauth2
from app.database import get_db
from sqlalchemy.orm import Session
import shutil
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder



#admin routre..where admin can add staff that can do the work

router=APIRouter(prefix="/admin",tags=['ADMIN'])
#adding staff or staff registration

@router.post("/addstaff",status_code=status.HTTP_201_CREATED)
def add_new_staff(staff: schemas.AddStaff,current_admin =Depends(oauth2.get_current_admin), db:Session= Depends(get_db)):
    admin=db.query(models.Admin).filter(models.Admin.id==current_admin.id).first()
    if not admin:
        raise HTTPException(status_code=403,detail=f'Invalid Credentials')
        
    hashed_password=utils.hash(staff.password)
    staff.password=hashed_password

    new_staff=models.Staff(**staff.dict())
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    new_staff= schemas.StaffOut(id=new_staff.id,
                                name=new_staff.name,
                                email=new_staff.email,
                                created_at=new_staff.created_at,
                                start_date=new_staff.start_date,
                                phone_no=new_staff.phone_no,
                                salary=new_staff.salary)
                      
    print(new_staff)
                                
    access_token = oauth2.create_access_token(
        data={"user_id": new_staff.id, "user_type": "staff"}
    )

    return {"access_token": access_token, "token_type": "bearer"}
    

#STAFF LOGIN
@router.post("/StaffLogin")
def staff_Login(staff_credens: OAuth2PasswordRequestForm=Depends(),db:Session = Depends(get_db)):
    staff=db.query(models.Staff).filter(models.Staff.email==staff_credens.username).first()
    if not staff:
        raise HTTPException(status_code=403,detail=f'Invalid Credentials')
    if not utils.verify(staff_credens.password, staff.password):
        raise HTTPException(status_code=403,detail=f'Invalid Credentials')
    
    access_token = oauth2.create_access_token(
        data={"user_id": staff.id, "user_type": "staff"}
                                                            )    
    return {"access_token":access_token, "token_type":"bearer"}
    

#upload staffs profile pic

@router.post("/staff_dp/{staff_id}")
def upload_dp(file: UploadFile,staff_id: int, current_staff= Depends(oauth2.get_current_staff), db:Session = Depends(get_db)):
    db_staff= db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    if db_staff.id != current_staff.id:
        raise HTTPException(status_code=404, detail="Not allowed to update this profile")
    
    file_location = f"uploads/images/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_staff.photo = file_location
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)

    return db_staff


#admins can create room
@router.post("/CreateRoom/{admin_id}",status_code=status.HTTP_201_CREATED)
def admin_create_room(room: schemas.CreateRoom, admin_id: int, current_admin= Depends(oauth2.get_current_admin), db: Session=Depends(get_db)):
    
    if current_admin.id != admin_id:
        raise HTTPException(status_code=403, detail="Not allowed to create rooms for another admin")
    room_exists = db.query(models.SingleRoom).filter(models.SingleRoom.room_no == room.room_no).first() or \
                  db.query(models.DeluxeRoom).filter(models.DeluxeRoom.room_no == room.room_no).first() or \
                  db.query(models.CottageRoom).filter(models.CottageRoom.room_no == room.room_no).first()
    if room_exists:
        raise HTTPException(status_code=400, detail="Room with this room number already exists")

    if room.category in ["singleroom", "single room"]:
        new_room = models.SingleRoom(**room.dict(), admin_id=admin_id)
    elif room.category in ["deluxeroom", "deluxe room"]:
        new_room = models.DeluxeRoom(**room.dict(), admin_id=admin_id)
    elif room.category in ["cottageroom", "cottage room"]:
        new_room = models.CottageRoom(**room.dict(),admin_id=admin_id)
    else:
        raise HTTPException(status_code=404, detail="Category of room not available")
    
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    print(new_room)
    return new_room
    


@router.get("/AllRooms/{user_id}",status_code=status.HTTP_200_OK)
def get_all_rooms(user_id : int ,staff0radmin= Depends(oauth2.get_current_stafforadmin), db:Session = Depends(get_db)):
        if staff0radmin.id != user_id:
            raise HTTPException(status_code=403, detail="Invalid credentials")
           
        single_rooms=db.query(models.SingleRoom).all()
        print(single_rooms)
        deluxe_rooms=db.query(models.DeluxeRoom).all()
        print(deluxe_rooms)
        cottage_rooms=db.query(models.CottageRoom).all() 
        print(cottage_rooms)

        all_rooms= single_rooms + deluxe_rooms + cottage_rooms
        return all_rooms

@router.get("/RoomsNotOccupied/{user_id}", status_code= status.HTTP_200_OK)
def get_rooms_not_occupied(user_id: int, stafforadmin= Depends(oauth2.get_current_stafforadmin), db:Session= Depends(get_db)):
    if stafforadmin.id != user_id:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    single_unoccupied = db.query(models.SingleRoom).filter(models.SingleRoom.occupied == False).all()
    if single_unoccupied is None:
        raise HTTPException(status_code=404, detail="No unoccupied single rooms available")
    deluxe_unoccupied = db.query(models.DeluxeRoom).filter(models.DeluxeRoom.occupied == False).all()
    if deluxe_unoccupied is None:
        raise HTTPException(status_code=403, detail="No unoccupied deluxe rooms available")
    cottage_unoccupied = db.query(models.CottageRoom).filter(models.CottageRoom.occupied == False).all()
    if cottage_unoccupied is None:
        raise HTTPException(status_code=404, detail="No unoccupied cottage rooms available")
    all_unoccupied_rooms = single_unoccupied + deluxe_unoccupied + cottage_unoccupied
    return all_unoccupied_rooms
    



#get room by id
@router.get("/byId/{user_id}/{room_id}",status_code=status.HTTP_200_OK)
def get_room_by_id(room_id: int ,user_id: int,  stafforadmin= Depends(oauth2.get_current_stafforadmin),db:Session = Depends(get_db)):
    if stafforadmin.id != user_id:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    if room_id is None:
        raise HTTPException(status_code=403, detail="Room no not available")  

    room=db.query(models.SingleRoom).filter(models.SingleRoom.room_no == room_id).first()
    if room:
        return room
    room=db.query(models.DeluxeRoom).filter(models.DeluxeRoom.room_no == room_id).first()
    if room:
        return room
    room=db.query(models.CottageRoom).filter(models.CottageRoom.room_no == room_id).first()
    if room:
        return room

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

 #function to find room of the price based on category and dates   
def room_price(category: str, start_date, end_date):
    difference= (end_date - start_date).days
    if category in ["singleroom", "single room"]:
        price= 1000 * difference
    elif category in ["deluxeroom", "deluxe room"]:
        price= 2000 * difference
    elif category in ["cottageroom", "cottage room"]:
        price= 5000 * difference
    else:
        raise HTTPException(status_code=404, detail="Category of room not available")
    return price



#reduce staffs salary from revenue to get profit
@router.post("/reduce_salary", status_code=status.HTTP_200_OK)
def reduce_staff_salary(dets: schemas.StaffSalaryReduce, current_admin= Depends(oauth2.get_current_admin), db:Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.id == current_admin.id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Invalid Credentials")
    staff = db.query(models.Staff).filter(models.Staff.id == dets.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    finance= db.query(models.Finance).first()
    if not finance:
        raise HTTPException(status_code=404, detail="Finance record not found")
    
    finance.total_revenue = finance.total_revenue - int(staff.salary)
    db.commit()
    db.refresh(finance)
    return {"message": f"Staff salary of {staff.salary} reduced from total revenue."}

    
    





