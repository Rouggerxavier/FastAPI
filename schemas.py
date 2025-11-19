from typing import Literal, Optional
from pydantic import BaseModel, EmailStr

__all__ = ("UsuarioSchema", "LoginSchema", "PedidoSchema", "ItemPedidoSchema")


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
                "ativo": True
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
                "senha": "minhaSenha123"
            }
        }


class PedidoSchema(BaseModel):
    usuario_id: int
    preco: float = 0.0
    status: Optional[Literal["pendente", "aberto", "fechado", "cancelado"]] = "pendente"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "usuario_id": 1,
                "preco": 99.9,
                "status": "pendente"
            }
        }


class ItemPedidoSchema(BaseModel):
    nome_item: str
    quantidade: int
    tamanho: Optional[str] = None
    preco_unitario: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "nome_item": "Pizza Calabresa",
                "quantidade": 2,
                "tamanho": "Grande",
                "preco_unitario": 39.9
            }
        }
