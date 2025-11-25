
from typing import Optional
from urllib import request
from fastapi import APIRouter,Depends,status,HTTPException,Form,UploadFile,File
from app import models,schemas,utils,oauth2
from app import config
from app.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, time
import shutil
import uuid
import os
import razorpay
from app.config import settings
from fastapi.requests import Request
from fastapi import Request

import json
from app.routers.admin import room_price



router=APIRouter(prefix="/customer",tags=['Customer'])
client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))


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
@router.post("/booking/advance_payment", status_code=201)
def book_room_with_advance_payment(
    category: str = Form(...),
    people_count: int = Form(...),
    start_date: datetime = Form(...),
    end_date: datetime = Form(...),
    identity_type: str = Form(...),
    aadhar_front: Optional[UploadFile] = File(None),
    aadhar_back: Optional[UploadFile] = File(None),
    identity_image: Optional[UploadFile] = File(None),
    current_customer=Depends(oauth2.get_current_customer),
    db: Session = Depends(get_db)
):
    if not current_customer:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ---------------- ROOM SELECTION ----------------
    room = None
    if category.lower() in ["singleroom", "single room"]:
        if people_count != 1:
            raise HTTPException(status_code=400, detail="Single room allows only 1 person")
        room = db.query(models.SingleRoom).filter_by(occupied="False").first()

    elif category.lower() in ["deluxeroom", "deluxe room"]:
        if people_count not in [2, 3]:
            raise HTTPException(status_code=400, detail="Deluxe room allows 2 to 3 people")
        room = db.query(models.DeluxeRoom).filter_by(occupied="False").first()

    elif category.lower() in ["cottageroom", "cottage room"]:
        if not (4 <= people_count <= 8):
            raise HTTPException(status_code=400, detail="Cottage allows 4 to 8 people")
        room = db.query(models.CottageRoom).filter_by(occupied="False").first()

    else:
        raise HTTPException(status_code=400, detail="Invalid room category")

    if not room:
        raise HTTPException(status_code=404, detail="No room available in this category")

    # ---------------- PRICE + PAYMENT ----------------
    total_amount = room_price(category, start_date, end_date)
    advance_amount = int(total_amount * 0.20)
    due_amount = total_amount - advance_amount

    # ---------------- FILE UPLOAD ----------------
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
            raise HTTPException(status_code=400, detail="Aadhaar requires both sides")
        front_path = save_file(aadhar_front)
        back_path = save_file(aadhar_back)
    elif identity_type.lower() in ["passport", "license", "licence"]:
        if not identity_image:
            raise HTTPException(status_code=400, detail="Passport / License needs 1 image")
        identity_path = save_file(identity_image)
    else:
        raise HTTPException(status_code=400, detail="Invalid identity type")

    # ---------------- CREATE BOOKING ----------------
    booking = models.Booking(
        customer_id=current_customer.id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        people_count=people_count,
        identity_type=identity_type,
        aadhar_front_image=front_path,
        aadhar_back_image=back_path,
        identity_image=identity_path,
        total_amount=total_amount,
        advance_payment=advance_amount,
        due_amount=due_amount,
        payment_status="PENDING",
        STATUS="pending",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # ---------------- PAYMENT LINK CREATION ----------------
    payment_link = client.payment_link.create({
        "amount": advance_amount * 100,
        "currency": "INR",
        "description": f"Advance payment for booking {booking.booking_id}",
        "reference_id": str(booking.booking_id),
        "notify": {"sms": True, "email": True},
        "notes": {"booking_id": booking.booking_id},
    })

    booking.razorpay_payment_link = payment_link["id"]
    db.commit()

    return {
        "message": "Booking created — complete advance payment using link",
        "booking_id": booking.booking_id,
        "payment_link": payment_link["short_url"],
        "total_amount": total_amount,
        "advance_amount": advance_amount,
        "due_at_checkin": due_amount,
    }


# verify advance payment!!!!!!!!!!!!!!!!!!!!!!!!!!!
@router.post("/payment/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")
    print(">>>>>>>>>> WEBHOOK RECEIVED <<<<<<<<<<")
    print("Headers:", request.headers)
    print("Raw Body:", await request.body())

    print("Webhook raw body:", body)
    print("X-Razorpay-Signature:", signature)

    # Verify webhook signature from Razorpay
    try:
        client.utility.verify_webhook_signature(
            body, signature, settings.razorpay_webhook_secret
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    payload = json.loads(body)
    payment = payload["payload"]["payment"]["entity"]

    booking_id = payment.get("notes", {}).get("booking_id")
    booking = db.query(models.Booking).filter(models.Booking.booking_id == int(booking_id)).first()

    if not booking:
        return {"status": "ignored"}

    # idempotency → don't process twice
    if booking.razorpay_payment_id == payment["id"]:
        return {"status": "already_processed"}

    amount_paid = payment["amount"] / 100

    # Advance payment (20%)
    if booking.payment_status == "PENDING" and amount_paid >= booking.advance_payment:
        booking.payment_status = "PARTIALLY_PAID"
        booking.STATUS = "confirmed"
        total_revenue=total_revenue+ amount_paid
        booking.razorpay_payment_id = payment["id"]
        db.commit()
        return {"status": "advance_payment_success"}

    # Final payment during check-in
    if booking.payment_status == "PARTIALLY_PAID" and amount_paid >= booking.due_amount:
        booking.payment_status = "FULLY_PAID"
        total_revenue= total_revenue + amount_paid
        booking.checked_in = True
        booking.checked_in_date = datetime.utcnow()
        booking.razorpay_payment_id = payment["id"]
        db.commit()
        return {"status": "final_payment_success"}

    return {"status": "ignored"}


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
#make payment due
@router.post("/checkin/{booking_id}", status_code=200)
def customer_check_in(booking_id: int, current_staff=Depends(oauth2.get_current_staff), db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter_by(booking_id=booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.payment_status != "PARTIALLY_PAID":
        raise HTTPException(status_code=400, detail="Advance 20% payment not paid")

    remaining = booking.due_amount

    payment_link = client.payment_link.create({
        "amount": remaining * 100,
        "currency": "INR",
        "description": f"Final payment for booking {booking.booking_id}",
        "reference_id": str(booking.booking_id),
        "notify": {"sms": True, "email": True},
        "notes": {"booking_id": booking.booking_id},
    })

    booking.razorpay_payment_link = payment_link["id"]
    db.commit()

    return {
        "message": "Complete remaining payment using link",
        "payment_link": payment_link["short_url"],
        "remaining_due": remaining
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




@router.api_route("/get_my_status/{booking_id}", methods=["GET", "POST"], status_code=status.HTTP_200_OK)
async def booking_status(
    booking_id: int,
    request: Request,
    current_customer = Depends(oauth2.get_current_customer),
    db: Session = Depends(get_db)
):
    customer_id = current_customer.id

    booking = db.query(models.Booking).filter(
        models.Booking.booking_id == booking_id,
        models.Booking.customer_id == customer_id,
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="No booking found for this customer")

    # ---------- GET METHOD ----------
    if request.method == "GET":
        return {
            "message": "Booking status fetched successfully",
            "checked_out": booking.checked_out,
            "booking_details": booking
        }

    # ---------- POST METHOD ----------
    if request.method == "POST":
        # Parse feedback only for POST
        data = await request.json()   # feedback from body
        feedback = data.get("comments")

        if not booking.checked_out:
            raise HTTPException(status_code=400, detail="Cannot submit feedback before checkout")

        if not feedback:
            raise HTTPException(status_code=400, detail="Feedback comment is required")

        booking.feedback = feedback
        db.commit()
        db.refresh(booking)

        return {
            "message": "Feedback submitted successfully",
            "feedback": booking.feedback
        }

        



