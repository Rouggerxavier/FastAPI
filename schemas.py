from typing import Literal, Optional, List
from pydantic import BaseModel, EmailStr

__all__ = (
    "UsuarioSchema",
    "LoginSchema",
    "PedidoSchema",
    "PedidoCreateSchema",
    "ItemPedidoSchema",
    "ItemPedidoCreateSchema",
    "RemoverItemSchema",
)


class UsuarioSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    admin: bool = False
    ativo: bool = True

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "nome": "João da Silva",
                "email": "joao@email.com",
                "senha": "minhaSenha123",
                "admin": False,
                "ativo": True,
            }
        }


class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "joao@email.com",
                "senha": "minhaSenha123",
            }
        }


class ItemPedidoCreateSchema(BaseModel):
    sabor: str
    tamanho: str
    quantidade: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "sabor": "calabresa",
                "tamanho": "grande",
                "quantidade": 2
            }
        }


class ItemPedidoSchema(BaseModel):
    id: int
    pedido_id: int
    sabor: str
    tamanho: str
    quantidade: int
    preco_unitario: float
    subtotal: float

    class Config:
        from_attributes = True


class PedidoCreateSchema(BaseModel):
    usuario_id: int
    status: Optional[Literal["pendente", "aberto", "fechado", "cancelado"]] = "aberto"
    sabor: str
    tamanho: str
    quantidade: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "usuario_id": 1,
                "status": "aberto",
                "sabor": "calabresa",
                "tamanho": "grande",
                "quantidade": 2
            }
        }


class PedidoSchema(BaseModel):
    id: int
    usuario_id: int
    preco_total: float
    status: str
    itens: List[ItemPedidoSchema]

    class Config:
        from_attributes = True


class RemoverItemSchema(BaseModel):
    sabor: str
    tamanho: str
    quantidade: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "sabor": "calabresa",
                "tamanho": "grande",
                "quantidade": 1,
            }
        }
