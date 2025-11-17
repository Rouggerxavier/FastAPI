from passlib.context import CryptContext
from database import SessionLocal
from sqlalchemy.orm import Session

# 🔐 Contexto de criptografia usando Argon2 (moderno e compatível com Windows)
bcrypt_context = CryptContext(schemes=["argon2"], deprecated="auto")

# 🧠 Função de dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
