from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

SECRET_KEY = "chave-secreta-super-simples-para-atividade-faculdade"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

FAKE_USERS_DB = {
    "user": {
        "username": "user",
        "password": "user123",
        "role": "USER",
    },
    "admin": {
        "username": "admin",
        "password": "admin123",
        "role": "ADMIN",
    },
}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    sub: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str

app = FastAPI(
    title="API JWT - Autenticacao e Autorizacao",
    description=(
        "API simples com autenticacao via JWT e autorizacao baseada em "
        "perfil de usuario (USER e ADMIN)."
    ),
    version="1.0.0",
)

bearer_scheme = HTTPBearer(
    description="Cole aqui apenas o token JWT obtido em /login (sem o prefixo 'Bearer')."
)

def create_access_token(username: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserInfo:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido ou ausente",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return UserInfo(sub=username, role=role)


def require_admin(current_user: UserInfo = Depends(get_current_user)) -> UserInfo:
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para perfil ADMIN",
        )
    return current_user

@app.post("/login", response_model=Token, tags=["Autenticacao"])
def login(data: LoginRequest):
    """Recebe credenciais (username e password) em JSON e retorna um JWT."""
    user = FAKE_USERS_DB.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario ou senha invalidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user["username"], user["role"])
    return Token(access_token=token)


@app.get("/perfil", tags=["Usuario"])
def perfil(current_user: UserInfo = Depends(get_current_user)):
    """Acessivel para qualquer usuario autenticado."""
    return {
        "mensagem": f"Bem-vindo, {current_user.sub}!",
        "sub": current_user.sub,
        "role": current_user.role,
    }


@app.get("/admin", tags=["Admin"])
def admin(current_user: UserInfo = Depends(require_admin)):
    """Acessivel apenas para usuarios com perfil ADMIN."""
    return {
        "mensagem": f"Area administrativa - acesso concedido a {current_user.sub}",
        "sub": current_user.sub,
        "role": current_user.role,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
