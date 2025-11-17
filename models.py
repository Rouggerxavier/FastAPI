from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils import ChoiceType

Base = declarative_base()

STATUS_CHOICES = [
    ("aberto", "Aberto"),
    ("fechado", "Fechado"),
    ("cancelado", "Cancelado"),
]


class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)  # 👈 agora tem o campo de senha
    pedidos = relationship("Pedido", back_populates="usuario")


class Pedido(Base):
    __tablename__ = "pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    status = Column(ChoiceType(STATUS_CHOICES), nullable=True)

    usuario = relationship("Usuario", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido")


class ItemPedido(Base):
    __tablename__ = "itens_pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    nome_item = Column(String, nullable=False)
    quantidade = Column(Integer, nullable=False)

    pedido = relationship("Pedido", back_populates="itens")
