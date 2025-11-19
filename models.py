from sqlalchemy import Column, Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils import ChoiceType

Base = declarative_base()

STATUS_CHOICES = [
    ("aberto", "Aberto"),
    ("fechado", "Fechado"),
    ("cancelado", "Cancelado"),
    ("pendente", "Pendente"),
]
STATUS_VALUES = {choice[0] for choice in STATUS_CHOICES}


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    admin = Column(Boolean, nullable=False, default=False)

    pedidos = relationship("Pedido", back_populates="usuario")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    preco = Column(Float, nullable=False, default=0.0)
    status = Column(ChoiceType(STATUS_CHOICES), nullable=True, default="pendente")

    usuario = relationship("Usuario", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete")

    def calcular_preco(self):
        """Recalcula o preço total com base nos itens"""
        self.preco = sum(
            item.quantidade * item.preco_unitario for item in self.itens
        )


class ItemPedido(Base):
    __tablename__ = "itens_pedidos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    nome_item = Column(String, nullable=False)
    quantidade = Column(Integer, nullable=False)
    tamanho = Column(String, nullable=True)
    preco_unitario = Column(Float, nullable=False, default=0.0)

    pedido = relationship("Pedido", back_populates="itens")
