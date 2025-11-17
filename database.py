from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Caminho do banco (ajuste se necessário)
DATABASE_URL = "sqlite:///./meubanco.db"

# Cria o engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria as tabelas (opcional se estiver usando Alembic)
Base.metadata.create_all(bind=engine)
