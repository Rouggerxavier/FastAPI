from typing import Literal, Optional, List
from pydantic import BaseModel, EmailStr

__all__ = (
    "UsuarioSchema",
    "LoginSchema",
    "PedidoSchema",
    "ItemPedidoSchema",
    "RemoverItemSchema",
    "PedidoCreateSchema",
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


class PedidoSchema(BaseModel):
    usuario_id: int
    preco: float
    status: Optional[Literal["pendente", "aberto", "fechado", "cancelado"]] = "pendente"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "usuario_id": 1,
                "preco": 99.9,
                "status": "pendente",
            }
        }


class ItemPedidoSchema(BaseModel):
    quantidade: int
    sabor: str
    tamanho: str
    preco_unitario: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "quantidade": 2,
                "sabor": "Calabresa",
                "tamanho": "Grande",
                "preco_unitario": 45.5,
            }
        }


class RemoverItemSchema(BaseModel):
    sabor: str
    tamanho: str
    quantidade: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "sabor": "Calabresa",
                "tamanho": "Grande",
                "quantidade": 1,
            }
        }


class PedidoCreateSchema(BaseModel):
    usuario_id: int
    status: Optional[Literal["pendente", "aberto", "fechado", "cancelado"]] = "pendente"
    itens: List[ItemPedidoSchema]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "usuario_id": 1,
                "status": "aberto",
                "itens": [
                    {
                        "quantidade": 3,
                        "sabor": "Calabresa",
                        "tamanho": "Grande",
                        "preco_unitario": 50.0,
                    }
                ],
            }
        }
