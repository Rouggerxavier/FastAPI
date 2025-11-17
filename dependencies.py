from passlib.context import CryptContext
from database import SessionLocal
from sqlalchemy.orm import Session, sessionmaker
from models import Usuario
from fastapi import Depends


bcrypt_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verificar_token(token, session : Session = Depends(get_db)):
    usuario = session.query(Usuario).filter(usuario.id==1).first()
    return usuario