from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.database import get_db
from app.models.consulta import Consulta
from app.models.medico import Medico
from app.models.paciente import Paciente

router = APIRouter(prefix="/consultas", tags=["Consultas"])


# ------------------------------------------------------------------ #
# Schemas                                                             #
# ------------------------------------------------------------------ #

class ConsultaCreate(BaseModel):
    """Dados para criar uma consulta."""
    paciente_id: int
    medico_id: int | None = None
    diagnostico: str | None = None


class ConsultaResponse(BaseModel):
    """Dados retornados ao consultar uma consulta."""
    id: int
    data_consulta: datetime
    diagnostico: str | None
    paciente_id: int
    medico_id: int | None

    model_config = {"from_attributes": True}


# ------------------------------------------------------------------ #
# Endpoints CRUD                                                      #
# ------------------------------------------------------------------ #

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ConsultaResponse,
    summary="Criar uma nova consulta",
)
async def criar_consulta(
    dados: ConsultaCreate,
    db: AsyncSession = Depends(get_db),
) -> Consulta:
    """Cria uma nova consulta vinculada a um paciente e opcionalmente a um médico."""
    paciente = await db.get(Paciente, dados.paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    if dados.medico_id:
        medico = await db.get(Medico, dados.medico_id)
        if not medico:
            raise HTTPException(status_code=404, detail="Médico não encontrado")

    consulta = Consulta(
        data_consulta=datetime.now(),
        diagnostico=dados.diagnostico,
        paciente_id=dados.paciente_id,
        medico_id=dados.medico_id,
    )
    db.add(consulta)
    await db.commit()
    await db.refresh(consulta)
    return consulta


@router.get(
    "/",
    response_model=Page[ConsultaResponse],
    summary="Listar consultas com paginação",
)
async def listar_consultas(
    db: AsyncSession = Depends(get_db),
) -> Page[ConsultaResponse]:
    """Retorna uma página de consultas."""
    query = select(Consulta).options(
        joinedload(Consulta.paciente),
        joinedload(Consulta.medico),
    )
    return await paginate(db, query)


@router.get(
    "/busca",
    response_model=Page[ConsultaResponse],
    summary="Buscar consultas por filtros",
)
async def buscar_consultas(
    paciente_id: int | None = Query(None, description="Filtrar por paciente"),
    medico_id: int | None = Query(None, description="Filtrar por médico"),
    diagnostico: str | None = Query(None, description="Busca parcial por diagnóstico"),
    data_inicio: datetime | None = Query(None, description="Data inicial"),
    data_fim: datetime | None = Query(None, description="Data final"),
    ano: int | None = Query(None, description="Filtrar pelo ano da consulta"),
    db: AsyncSession = Depends(get_db),
) -> Page[ConsultaResponse]:
    """Busca consultas com múltiplos filtros opcionais."""
    query = select(Consulta).options(
        joinedload(Consulta.paciente),
        joinedload(Consulta.medico),
    )

    if paciente_id:
        query = query.where(Consulta.paciente_id == paciente_id)
    if medico_id:
        query = query.where(Consulta.medico_id == medico_id)
    if diagnostico:
        query = query.where(Consulta.diagnostico.ilike(f"%{diagnostico}%"))
    if data_inicio:
        query = query.where(Consulta.data_consulta >= data_inicio)
    if data_fim:
        query = query.where(Consulta.data_consulta <= data_fim)
    if ano:
        query = query.where(func.strftime("%Y", Consulta.data_consulta) == str(ano))

    return await paginate(db, query)


@router.get(
    "/count",
    summary="Contar total de consultas",
)
async def contar_consultas(db: AsyncSession = Depends(get_db)) -> dict:
    """Retorna o total de consultas cadastradas."""
    result = await db.execute(select(func.count()).select_from(Consulta))
    return {"total": result.scalar()}


@router.get(
    "/{id}",
    response_model=ConsultaResponse,
    summary="Buscar consulta por ID",
)
async def buscar_por_id(
    id: int,
    db: AsyncSession = Depends(get_db),
) -> Consulta:
    """Retorna uma consulta específica pelo ID."""
    result = await db.execute(
        select(Consulta)
        .options(joinedload(Consulta.paciente), joinedload(Consulta.medico))
        .where(Consulta.id == id)
    )
    consulta = result.scalar_one_or_none()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    return consulta


@router.put(
    "/{id}",
    response_model=ConsultaResponse,
    summary="Atualizar consulta",
)
async def atualizar_consulta(
    id: int,
    dados: ConsultaCreate,
    db: AsyncSession = Depends(get_db),
) -> Consulta:
    """Atualiza os dados de uma consulta existente."""
    consulta = await db.get(Consulta, id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    for key, value in dados.model_dump().items():
        setattr(consulta, key, value)

    await db.commit()
    await db.refresh(consulta)
    return consulta


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar consulta",
)
async def deletar_consulta(
    id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove uma consulta pelo ID."""
    consulta = await db.get(Consulta, id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    await db.delete(consulta)
    await db.commit()