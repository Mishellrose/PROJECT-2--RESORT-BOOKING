
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
    print("single rooms are available", available_single_rooms)
    available_deluxe_rooms=db.query(models.DeluxeRoom).filter(models.DeluxeRoom.occupied == "False" ).first()
    print("deluxe rooms are available", available_deluxe_rooms)
    available_cottage_rooms=db.query(models.CottageRoom).filter(models.CottageRoom.occupied == "False").first()
    print("cottage rooms are available", available_cottage_rooms)

    return {"message":"Check console for available room categories",
            "single": schemas.SingleOut.from_orm(available_single_rooms),
            "deluxe": schemas.DeluxeOut.from_orm(available_deluxe_rooms),
            "cottage": schemas.CottageOut.from_orm(available_cottage_rooms)}
