from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from app.core.config import settings
from app.core.exceptions import configurar_excecoes
from app.db.db import client, close_db, init_db
from app.routers import (
    consulta_router,
    documento_router,
    especialidade_router,
    exame_router,
    internacao_router,
    medico_router,
    paciente_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    await init_db()  # sempre antes de atender requisições
    yield
    await close_db()


app = FastAPI(title="Gestão Hospitalar", version="1.1.0", lifespan=lifespan)

configurar_excecoes(app)

for modulo in (
    especialidade_router,
    medico_router,
    paciente_router,
    exame_router,
    consulta_router,
    internacao_router,
    documento_router,
):
    app.include_router(modulo.router)

add_pagination(app)  # após incluir os routers: habilita page/size nas rotas com response_model=Page[...]


@app.get("/")
async def root():
    return {"message": "API de Gestão Hospitalar Operacional"}


@app.get("/health")
async def health():
    try:
        await client.admin.command("ping")
    except Exception:
        return JSONResponse(status_code=503, content={"status": "indisponivel"})
    return {"status": "ok"}
