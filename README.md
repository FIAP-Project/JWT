# API JWT - Autenticação e Autorização

API simples em **FastAPI** com autenticação via **JWT** e autorização baseada em
perfil de usuário (`USER` e `ADMIN`). Projeto para atividade da faculdade.

## Integrantes

Felipe Cerboncini Cordeiro RM554909
Milena Codinhoto da Silva RM554682
Pedro Henrique Martins Alves dos Santos RM558107

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) como gerenciador de pacotes

## Instalação

```bash
uv sync
```

## Executando a API

```bash
uv run uvicorn main:app --reload
```

A API sobe em `http://127.0.0.1:8000`.

## Swagger (documentação interativa)

Com o servidor rodando, acesse:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

Para testar os endpoints protegidos pela interface:

1. Faça login no endpoint `POST /login` (enviando `username` e `password` em JSON) e copie o valor de `access_token` da resposta.
2. Clique no botão **Authorize** (cadeado) e cole **apenas o token JWT** (sem o prefixo `Bearer`).
3. Pronto: os endpoints `/perfil` e `/admin` já podem ser chamados autenticados.

## Usuários de teste

| Usuário | Senha      | Perfil (role) |
|---------|------------|---------------|
| `user`  | `user123`  | `USER`        |
| `admin` | `admin123` | `ADMIN`       |

## Endpoints

| Método | Rota      | Acesso                              |
|--------|-----------|-------------------------------------|
| POST   | `/login`  | Público. Recebe credenciais e retorna o JWT. |
| GET    | `/perfil` | Qualquer usuário autenticado.       |
| GET    | `/admin`  | Somente perfil `ADMIN`.             |

### Regras de resposta

- Requisição sem token ou com token inválido/expirado → **401 Unauthorized**.
- Usuário `USER` tentando acessar `/admin` → **403 Forbidden**.

## Estrutura do JWT

O token gerado contém as seguintes claims:

- `sub` – identificador do usuário (username)
- `role` – perfil do usuário (`USER` ou `ADMIN`)
- `iat` – data/hora de emissão
- `exp` – data/hora de expiração (60 minutos)

## Exemplos de uso (curl)

```bash
# 1. Login (obter o token)
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Acessar /perfil (autenticado)
curl http://127.0.0.1:8000/perfil \
  -H "Authorization: Bearer <TOKEN>"

# 3. Acessar /admin (apenas ADMIN)
curl http://127.0.0.1:8000/admin \
  -H "Authorization: Bearer <TOKEN>"
```

## Observações

- A chave secreta (`SECRET_KEY`) e os usuários estão fixos no código apenas por
  se tratar de um exercício acadêmico. Em produção, use variáveis de ambiente e
  um banco de dados com senhas devidamente hasheadas.
