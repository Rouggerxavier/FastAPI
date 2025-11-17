# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# chave secreta do JWT
SECRET_KEY = os.getenv("SECRET_KEY", "chave-super-secreta")

# algoritmo usado pelo jose.jwt
ALGORITHM = "HS256"

# tempo de expiração do token em minutos
ACCESS_TOKEN_EXPIRE_MINUTES = 30
