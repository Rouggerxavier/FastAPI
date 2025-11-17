from fastapi import FastAPI
from auth_routes import auth_router
from order_routes import order_router
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.include_router(auth_router)
app.include_router(order_router)

@app.get("/")
async def root():
    return {"message": "API funcionando!"}


