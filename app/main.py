

from fastapi import FastAPI
from app import models
from .routers import user

from app.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(user.router)
