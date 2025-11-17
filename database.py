from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base

# Caminho do banco (ajuste se necessário)
DATABASE_URL = "sqlite:///./meubanco.db"

# Cria o engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Garante que o schema esteja atualizado mesmo em bancos antigos sem rodar Alembic
def ensure_preco_column(engine) -> None:
    """Adiciona a coluna `preco` em bancos SQLite existentes, se necessário."""
    with engine.connect() as conn:
        columns = conn.execute(text("PRAGMA table_info(pedidos);"))
        if not any(col[1] == "preco" for col in columns):
            conn.execute(text("ALTER TABLE pedidos ADD COLUMN preco FLOAT NOT NULL DEFAULT 0"))
            conn.execute(text("UPDATE pedidos SET preco = 0 WHERE preco IS NULL"))
            conn.commit()

# Fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria as tabelas (opcional se estiver usando Alembic)
Base.metadata.create_all(bind=engine)
ensure_preco_column(engine)