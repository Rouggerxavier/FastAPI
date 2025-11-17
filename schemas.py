from pydantic import BaseModel, EmailStr

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
