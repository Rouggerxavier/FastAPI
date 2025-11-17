from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario
from dependencies import get_db, bcrypt_context, verificar_token
from schemas import UsuarioSchema, LoginSchema
from jose import jwt
from datetime import datetime, timedelta, timezone

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(id_usuario: int, duracao_token = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    data_expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    dic_info = {
        "sub": str(id_usuario),
        "exp": data_expiracao,
    }
    token_jwt = jwt.encode(dic_info, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt


def autenticar_usuario(email: str, senha: str, db: Session):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        return None

    if not bcrypt_context.verify(senha, usuario.senha):
        return None

    return usuario


@auth_router.get("/")
async def home():
    return {"mensagem": "Você acessou a rota de autenticação!"}


@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, db: Session = Depends(get_db)):
    nome = usuario_schema.nome
    email = usuario_schema.email
    senha = usuario_schema.senha

    usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Já existe um usuário com esse email")

    senha_criptografada = bcrypt_context.hash(senha)

    novo_usuario = Usuario(nome=nome, email=email, senha=senha_criptografada)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {
        "mensagem": "Usuário cadastrado com sucesso",
        "usuario": novo_usuario.email,
    }


@auth_router.post("/login")
async def login(login_schema: LoginSchema, db: Session = Depends(get_db)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, db)

    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    else:
        acess_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        refresh_token = criar_token(usuario.id)

    return {
        "mensagem": "Login realizado com sucesso",
        "usuario": usuario.email,
        "token": acess_token,
        "refresh_token" : refresh_token
    }

@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    acess_token = criar_token(usuario.id)
    return {
        "acess_token": acess_token,
        "token_type": "bearer"
    }
