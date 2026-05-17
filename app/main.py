from fastapi import FastAPI
from fastapi_pagination import add_pagination
from contextlib import asynccontextmanager

from app.routers import medicos
from app.routers import paciente_router
from app.routers import exame_router
from app.routers import consulta_router
from app.routers import internacao_router as internacoes

from app.db.database import Base, engine
from app.models.paciente import Paciente
from app.models.exame import Exame
from app.models.consulta import Consulta
from app.models.internacao import Internacao

# 1. Importação para o tratamento de exceções global
from app.core.exceptions import configurar_excecoes

# função async de tabelas
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Gestão Hospitalar", version="1.0.0", lifespan=lifespan)

# 2. Configuração do tratamento robusto de exceções global na instância da aplicação
configurar_excecoes(app)

app.include_router(medicos.router)
app.include_router(paciente_router.router)
app.include_router(exame_router.router)
app.include_router(consulta_router.router)
app.include_router(internacoes.router)

# Inicializa a paginação globalmente na aplicação
add_pagination(app)

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "API de Gestão Hospitalar Operacional"}