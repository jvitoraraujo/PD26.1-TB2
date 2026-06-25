from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from beanie import init_beanie

from app.db.db import db

from app.models import (
    Paciente,
    Medico,
    Consulta,
    Internacao,
    Exame,
    Documento,
    Especialidade,
)

from app.routers import (
    medicos,
    paciente_router,
    exame_router,
    consulta_router,
    internacao_router as internacoes,
    documento_router,
)

from app.core.exceptions import configurar_excecoes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔴 SEMPRE inicializa o Beanie primeiro
    await init_beanie(
        database=db,
        document_models=[
            Paciente,
            Medico,
            Consulta,
            Internacao,
            Exame,
            Documento,
            Especialidade,
        ],
    )

    yield


app = FastAPI(
    title="Gestão Hospitalar",
    version="1.0.0",
    lifespan=lifespan,
)

configurar_excecoes(app)

app.include_router(medicos.router)
app.include_router(paciente_router.router)
app.include_router(exame_router.router)
app.include_router(consulta_router.router)
app.include_router(internacoes.router)
app.include_router(documento_router.router)

add_pagination(app)


@app.get("/")
async def root():
    return {"message": "API de Gestão Hospitalar Operacional"}