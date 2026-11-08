import logging

from beanie import init_beanie
from pymongo import ASCENDING, AsyncMongoClient
from pymongo.errors import PyMongoError

from app.core.config import settings
from app.models import MODELOS

client = AsyncMongoClient(
    settings.MONGODB_URL,
    tz_aware=True,
    serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT_MS,
)
db = client[settings.DATABASE_NAME]

logger = logging.getLogger(__name__)

# Índices nas referências (DBRef) usadas nos filtros e nas checagens de integridade
INDICES_RELACIONAMENTO = {
    "consultas": ["paciente.$id", "medico.$id"],
    "exames": ["consulta.$id"],
    "internacoes": ["paciente.$id", "medico.$id"],
    "documents": ["paciente.$id"],
    "medicos": ["especialidades.$id"],
}


async def init_db() -> None:
    """Inicializa o Beanie (cria os índices declarados nos modelos)."""
    await init_beanie(database=db, document_models=MODELOS)
    await _criar_indices_relacionamento()


async def _criar_indices_relacionamento() -> None:
    """Otimização opcional: se o servidor recusar o índice, apenas avisa (não impede a subida)."""
    for colecao, campos in INDICES_RELACIONAMENTO.items():
        for campo in campos:
            try:
                await db[colecao].create_index([(campo, ASCENDING)])
            except PyMongoError as exc:
                logger.warning("Índice %s.%s não criado: %s", colecao, campo, exc)


async def close_db() -> None:
    await client.close()
