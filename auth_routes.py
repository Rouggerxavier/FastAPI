from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario
from dependencies import get_db, bcrypt_context
from schemas import UsuarioSchema, LoginSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(email):
    token = f"sioadoansdonas(email)"
    return token

# 🧭 Rota simples para testar se o módulo está acessível
@auth_router.get("/")
async def home():
    return {"mensagem": "Você acessou a rota de autenticação!"}


# 🧩 Rota para criar um novo usuário com senha criptografada
@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, db: Session = Depends(get_db)):
    # Extrai dados do schema
    nome = usuario_schema.nome
    email = usuario_schema.email
    senha = usuario_schema.senha

    # Verifica se já existe um usuário com o mesmo e-mail
    usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Já existe um usuário com esse email")

    # Criptografa a senha usando Argon2
    senha_criptografada = bcrypt_context.hash(senha)
    print("🔑 Hash gerado:", senha_criptografada)  # (opcional, para debug no terminal)

    # Cria o novo usuário
    novo_usuario = Usuario(nome=nome, email=email, senha=senha_criptografada)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {
        "mensagem": "Usuário cadastrado com sucesso",
        "usuario": novo_usuario.email
    }

@auth_router.post("/login")
async def login(login_schema : LoginSchema, session: Session = Depends(get_db)):
    usuario = session.query(Usuario).filter(Usuario.email==login_schema.email).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="usuario nao enocontrado")
    else:
        acess_token = criar_token(usuario.id)
        return {"acess_token": acess_token,
                "token_type": "bearer"
        }
