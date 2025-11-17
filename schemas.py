from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class UsuarioSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "nome": "João da Silva",
                "email": "joao@email.com",
                "senha": "minhaSenha123"
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
                "status": "pendente"
            }
        }