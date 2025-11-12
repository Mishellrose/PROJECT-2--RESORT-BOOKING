
from typing import Optional
from fastapi import APIRouter,Depends,status,HTTPException
from app import models,schemas,utils,oauth2
from app.database import get_db
from sqlalchemy.orm import Session



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
@router.post("/book",status_code=status.HTTP_201_CREATED)
def book_room(book_dets: schemas.BookingDets, current_customer= Depends(oauth2.get_current_customer), db:Session= Depends(get_db)):
    if not current_customer:
        raise HTTPException(status_code=401, detail="Invalid credntials")
    
    if book_dets.category.lower() in ["singleroom", "single room"] and book_dets.people_count < 2:
        room = db.query(models.SingleRoom).filter(models.SingleRoom.occupied == "False").first()
    elif book_dets.category.lower() in ["deluxeroom", "deluxe room"] and book_dets.people_count < 5 and book_dets.people_count >= 2:
        room = db.query(models.DeluxeRoom).filter(models.DeluxeRoom.occupied == "False").first()
    elif book_dets.category.lower() in ["cottageroom", "cottage room"] and book_dets.people_count < 11 and book_dets.people_count >= 5:
        room = db.query(models.CottageRoom).filter(models.CottageRoom.occupied == "False").first()
    else :
        raise HTTPException(status_code=401, detail="No rooms available")

    new_booking = models.Booking(customer_id=current_customer.id, room_id=room.id, category=book_dets.category, start_date=book_dets.start_date,
                              end_date=book_dets.end_date, people_count=book_dets.people_count)
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return {
        "message": f"{book_dets.category} booking made by customer",
        "customer_id": current_customer.id,
        "room_details": new_booking
    }