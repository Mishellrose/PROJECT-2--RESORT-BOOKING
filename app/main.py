

from fastapi import FastAPI
from app import models
from .routers import customer, user,auth,admin

from app.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(user.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(customer.router)
