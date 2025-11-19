from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario
from dependencies import get_db, bcrypt_context, verificar_token
from schemas import UsuarioSchema, LoginSchema
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(id_usuario: int, duracao_token: timedelta | None = None) -> str:
    if duracao_token is None:
        duracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    data_expiracao = datetime.now(timezone.utc) + duracao_token

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

    access_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
    refresh_token = criar_token(usuario.id)

    return {
        "mensagem": "Login realizado com sucesso",
        "usuario": usuario.email,
        "token": access_token,
        "refresh_token": refresh_token,
    }


@auth_router.post("/login-form")
async def login_form(
    dados_formulario: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2PasswordRequestForm usa "username", mas você está autenticando por email
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, db)

    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    access_token = criar_token(usuario.id, duracao_token=timedelta(days=7))

    # 🔴 IMPORTANTE: resposta no formato que o OAuth2PasswordBearer espera
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }   


@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
