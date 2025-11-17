
from typing import Optional
from fastapi import APIRouter,Depends,status,HTTPException,Form,UploadFile,File
from app import models,schemas,utils,oauth2
from app.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, time
import shutil
import uuid
import os




router=APIRouter(prefix="/customer",tags=['Customer'])


#get rooms category that are not occupied
@router.get("/availablecategory/{customer_id}",status_code=status.HTTP_200_OK)
def get_available_category(customer_id: int, current_customer= Depends(oauth2.get_current_customer), db:Session= Depends(get_db)):
    print(current_customer)
    print(customer_id)
    if  current_customer.id != customer_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    available_single_rooms=db.query(models.SingleRoom).filter(models.SingleRoom.occupied == "False").first()
    available_deluxe_rooms=db.query(models.DeluxeRoom).filter(models.DeluxeRoom.occupied == "False" ).first()  
    available_cottage_rooms=db.query(models.CottageRoom).filter(models.CottageRoom.occupied == "False").first()
    rooms = {
        "single": schemas.SingleOut.from_orm(available_single_rooms) if available_single_rooms else None,
        "deluxe": schemas.DeluxeOut.from_orm(available_deluxe_rooms) if available_deluxe_rooms else None,
        "cottage": schemas.CottageOut.from_orm(available_cottage_rooms) if available_cottage_rooms else None,
    }

    available_rooms = {key: value for key, value in rooms.items() if value is not None}

    if not available_rooms:
        raise HTTPException(status_code=404, detail="No rooms available")

    return {
        "message": "Available room categories",
        "available_rooms": available_rooms
    }
    

    

#booking
@router.post("/booking",status_code=status.HTTP_201_CREATED)
def book_room(category: str = Form(...),
              people_count: int = Form(...),
               start_date: datetime = Form(...),
               end_date: datetime = Form(...),
                identity_type: str = Form(...),
              aadhar_front: Optional[UploadFile] = File(None),
              aadhar_back: Optional[UploadFile] = File(None),
              identity_image: Optional[UploadFile] = File(None),
               current_customer= Depends(oauth2.get_current_customer), db:Session= Depends(get_db)):
    if not current_customer:
        raise HTTPException(status_code=401, detail="Invalid credentials")   
    if category.lower() in ["singleroom", "single room"] :
        if people_count <1 or people_count >1:
            raise HTTPException(status_code=401, detail="Single room can accomodate only 1 person")      
        room = db.query(models.SingleRoom).filter(models.SingleRoom.occupied == "False").first()     
        if room is None:
            raise HTTPException(status_code=404, detail="No available single rooms")         
    elif category.lower() in ["deluxeroom", "deluxe room"] :
        if people_count < 2 or people_count >=4:
            raise HTTPException(status_code=401, detail="Deluxe room can accomodate only 2 to 3 people")
        room = db.query(models.DeluxeRoom).filter(models.DeluxeRoom.occupied == "False").first()   
        if room is None:
            raise HTTPException(status_code=404, detail="No available deluxe rooms")         
    elif category.lower() in ["cottageroom", "cottage room"]:
        if people_count <4 or people_count >=9:
            raise HTTPException(status_code=401, detail="Cottage room can accomodate only 4 to 8 people")
        room = db.query(models.CottageRoom).filter(models.CottageRoom.occupied == "False").first()
        if people_count <5 or people_count >=11:
            raise HTTPException(status_code=401, detail="Cottage room can accomodate only 5 to 10 people") 
        if room is None:
            raise HTTPException(status_code=404, detail="No available cottage rooms") 
    else:
        raise HTTPException(status_code=400, detail="Invalid room category")       
    #function for identity_card and uploading images using Upload file
    upload_dir = "uploads/identity"
    os.makedirs(upload_dir, exist_ok=True)
    def save_file(file):
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = f"{upload_dir}/{filename}"
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return filepath   
    front_path = back_path = identity_path = None
    if identity_type.lower() == "aadhaar":
        if not aadhar_front or not aadhar_back:
            raise HTTPException(status_code=400, detail="Aadhaar requires front & back images")
        if identity_image:
             raise HTTPException(status_code=400, detail="Do NOT upload single identity image for Aadhaar")
        front_path = save_file(aadhar_front)
        back_path = save_file(aadhar_back)
    elif identity_type.lower() in ["passport", "license", "licence"]:
        if not identity_image:
            raise HTTPException(status_code=400, detail="Passport / Licence requires only one image")
        if aadhar_front or aadhar_back:
            raise HTTPException(status_code=400, detail="Do NOT upload Aadhaar front/back for Passport/Licence")
        identity_path = save_file(identity_image)
    else:
        raise HTTPException(status_code=400, detail="Invalid identity proof type")  
    db_booking = models.Booking(
        customer_id=current_customer.id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        people_count=people_count,
        identity_type=identity_type,
        aadhar_front_image=front_path,
        aadhar_back_image=back_path,
        identity_image=identity_path
    )
    print(db_booking)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return {
        "message": f"{category} booking successful",
        "customer_id": current_customer.id,
        "booking_details": db_booking
    }



#staff should get all bookings
@router.get("/getbook/{staff_id}", status_code=status.HTTP_200_OK)
def get_all_bookings(staff_id: int, current_staff= Depends(oauth2.get_current_staff), db:Session= Depends(get_db)):
    if staff_id != current_staff.id:
        raise HTTPException(status_code=403, detail="Not authorized to view bookings")
    db_bookings= db.query(models.Booking).all()
    bookings =db_bookings
    return bookings

#get all pending bookings
@router.get("/pendingbook/{staff_id}", status_code=status.HTTP_200_OK)
def get_pending_bookings(staff_id: int, current_staff= Depends(oauth2.get_current_staff), db:Session = Depends(get_db)):
    print(current_staff)
    print(staff_id)
    if staff_id != current_staff.id:
        raise HTTPException(status_code=403, detail="Not authorized to view bookings")
    
    pending_bookings= db.query(models.Booking).filter(models.Booking.STATUS == "pending").all()
    return pending_bookings






#confirm booking and occupy room by staff
@router.put("/confirmbooking/{staff_id}/{booking_id}", status_code=status.HTTP_200_OK)
def confirm_booking(staff_id: int, booking_id: int, current_staff= Depends(oauth2.get_current_staff), db:Session= Depends(get_db)):
                    
    if staff_id != current_staff.id:
        raise HTTPException(status_code=403, detail="Not authorized to confirm bookings")
    booking= db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if booking.STATUS == "confirmed":
        raise HTTPException(status_code=400, detail="Booking already confirmed,look for other rooms")
    print(booking)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    #mark room as occupied
    if booking.category.lower() in ["singleroom", "single room"]:
        room = db.query(models.SingleRoom).filter(models.SingleRoom.occupied == False).first()
        room.occupied = True
    elif booking.category.lower() in ["deluxeroom", "deluxe room"]:
        room = db.query(models.DeluxeRoom).filter(models.DeluxeRoom.occupied == False).first()
        room.occupied = True
    elif booking.category.lower() in ["cottageroom", "cottage room"]:
        room = db.query(models.CottageRoom).filter(models.CottageRoom.occupied == False).first()
        room.occupied = True
    else:
        raise HTTPException(status_code=400, detail="Invalid room category in booking")
    booking.STATUS = "confirmed"
    booking.room_no = room.room_no
    
    db.commit()
    db.refresh(booking)
    return {
        "message": f"Booking {booking_id} confirmed and room {booking.room_no} marked as occupied",
        "booking_details": booking
    }



#check in route
@router.post("/checkin/{booking_id}", status_code=status.HTTP_200_OK)
def customer_checks_in( booking_id:  int, current_staff= Depends(oauth2.get_current_staff), db:Session= Depends(get_db)):
    booking= db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    staff=db.query(models.Staff).filter(models.Staff.id == current_staff.id).first()
    if not staff:
        raise HTTPException(status_code=403, detail="Only staff can check in customers")
    if booking.STATUS != "confirmed":
        raise HTTPException(status_code=400, detail="Booking not confirmed yet")
    booking.checked_in = True
    booking.checked_in_date = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return {
        "message": f"Booking {booking_id} CHECKED IN successfully and should checkout by end date {booking.end_date} 11.00 AM",
        "booking_details": booking
    }

#public pool usage
@router.post("/publicpooluse/{booking_id}", status_code=status.HTTP_200_OK)
def use_pool(count: schemas.PoolCount, booking_id: int, current_staff=Depends(oauth2.get_current_staff), db:Session= Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.category.lower() in ["singleroom", "single room"]:
        if count.pool_used_by >1:
            raise HTTPException(status_code=400, detail="Single room booking allows only 1 pool user")
    elif booking.category.lower() in ["deluxeroom", "deluxe room"]:
        if count.pool_used_by >3:
            raise HTTPException(status_code=400, detail="Deluxe room booking allows only 3 pool users")
    elif booking.category.lower() in ["cottageroom", "cottage room"]:
        if count.pool_used_by >5:
            raise HTTPException(status_code=400, detail="Cottage room booking allows only 5 pool users")
        
    staff=db.query(models.Staff).filter(models.Staff.id == current_staff.id).first()
    if not staff:
        raise HTTPException(status_code=403, detail="Only staff can record pool usage")
    if booking.STATUS != "confirmed":
        raise HTTPException(status_code=400, detail="Booking not confirmed yet")
    
    booking.pool_used_by = count.pool_used_by
    print(booking.pool_used_by)
    booking.pool_used__start_date = datetime.utcnow()
    print(booking.pool_used__start_date)
    start=time(6,0)
    end=time(21,0)
    if start <= booking.pool_used__start_date.time() <= end:
       print("Pool usage time is valid")
    else:
        raise HTTPException(status_code=400, detail="Pool can be used only between 6 AM to 9 PM")     
    db.commit()
    db.refresh(booking)
    return {
        "message": f"Pool usage recorded for booking {booking_id}",
        "booking_details": booking
    }

#checkout
@router.post("/checkout/{booking_id}", status_code=status.HTTP_200_OK)
def customer_checks_out( booking_id: int, current_staff= Depends(oauth2.get_current_staff), db:Session = Depends(get_db)):
    booking= db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    staff=db.query(models.Staff).filter(models.Staff.id == current_staff.id).first()
    if not staff:
        raise HTTPException(status_code=403, detail="Only staff can check out customers")
    if booking.STATUS != "confirmed":
        raise HTTPException(status_code=400, detail="Booking not confirmed yet")
    booking.checked_out = True
    booking.checked_out_date = datetime.utcnow()
    #mark room as unoccupied
    if booking.category.lower() in ["singleroom", "single room"]:
        room=db.query(models.SingleRoom).filter(models.SingleRoom.room_no == booking.room_no).first()
        room.occupied = False
    elif booking.category.lower() in ["deluxeroom", "deluxe room"]:
        room=db.query(models.DeluxeRoom).filter(models.DeluxeRoom.room_no == booking.room_no).first()
        room.occupied = False
    elif booking.category.lower() in ["cottageroom", "cottage room"]:
        room=db.query(models.CottageRoom).filter(models.CottageRoom.room_no == booking.room_no).first()
        room.occupied = False
    else:
        raise HTTPException(status_code=400, detail="Invalid room category in booking")
    
    db.commit()
    db.refresh(booking)
    return {
        "message": f"Customer checked out for booking {booking_id}",
        "booking_details": booking
    }





