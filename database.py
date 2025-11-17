from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "sqlite:///./meubanco.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

def ensure_preco_column(engine) -> None:
    with engine.connect() as conn:
        columns = conn.execute(text("PRAGMA table_info(pedidos);"))
        if not any(col[1] == "preco" for col in columns):
            conn.execute(text("ALTER TABLE pedidos ADD COLUMN preco FLOAT NOT NULL DEFAULT 0"))
            conn.execute(text("UPDATE pedidos SET preco = 0 WHERE preco IS NULL"))
            conn.commit()


def ensure_senha_column(engine) -> None:
    with engine.connect() as conn:
        columns = conn.execute(text("PRAGMA table_info(usuarios);"))
        if not any(col[1] == "senha" for col in columns):
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN senha VARCHAR NOT NULL DEFAULT ''"))
            conn.commit()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
ensure_preco_column(engine)
ensure_senha_column(engine)