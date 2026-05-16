from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.internacao import Internacao
from app.models.medico import Medico
from app.models.paciente import Paciente

router = APIRouter(prefix="/internacoes", tags=["Internações"])


# ------------------------------------------------------------------ #
# Schemas                                                             #
# ------------------------------------------------------------------ #

class InternacaoCreate(BaseModel):
    """Dados necessários para criar uma internação."""
    data_entrada: datetime
    data_saida: datetime | None = None
    quarto: str
    motivo: str
    observacoes: str | None = None
    valor_diaria: float = 0.0
    paciente_id: int
    medico_id: int


class InternacaoResponse(BaseModel):
    """Dados retornados ao consultar uma internação."""
    id: int
    data_entrada: datetime
    data_saida: datetime | None
    quarto: str
    motivo: str
    observacoes: str | None
    valor_diaria: float
    paciente_id: int
    medico_id: int

    model_config = {"from_attributes": True}


# ------------------------------------------------------------------ #
# Endpoints                                                           #
# ------------------------------------------------------------------ #

@router.get("/count", summary="Contar total de internações")
async def contar_internacoes(db: AsyncSession = Depends(get_db)) -> dict:
    """Retorna o total de internações cadastradas."""
    result = await db.execute(select(func.count()).select_from(Internacao))
    return {"total": result.scalar()}


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=InternacaoResponse,
    summary="Criar uma nova internação",
)
async def criar_internacao(
    dados: InternacaoCreate,
    db: AsyncSession = Depends(get_db),
) -> Internacao:
    """Cria uma nova internação vinculada a um paciente e um médico."""
    paciente = await db.get(Paciente, dados.paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    medico = await db.get(Medico, dados.medico_id)
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")

    if dados.data_saida and dados.data_saida <= dados.data_entrada:
        raise HTTPException(
            status_code=400,
            detail="data_saida deve ser posterior a data_entrada",
        )

    internacao = Internacao(**dados.model_dump())
    db.add(internacao)
    await db.commit()
    await db.refresh(internacao)
    return internacao


@router.get(
    "/",
    response_model=Page[InternacaoResponse],
    summary="Listar internações com paginação",
)
async def listar_internacoes(
    db: AsyncSession = Depends(get_db),
) -> Page[InternacaoResponse]:
    """Retorna uma página de internações."""
    query = select(Internacao)
    return await paginate(db, query)


@router.get(
    "/busca",
    response_model=Page[InternacaoResponse],
    summary="Buscar internações por filtros",
)
async def buscar_internacoes(
    paciente_id: int | None = Query(None, description="Filtrar por paciente"),
    medico_id: int | None = Query(None, description="Filtrar por médico"),
    quarto: str | None = Query(None, description="Filtrar por quarto"),
    ativas: bool | None = Query(None, description="True = sem data de saída"),
    ano: int | None = Query(None, description="Filtrar pelo ano de entrada"),
    db: AsyncSession = Depends(get_db),
) -> Page[InternacaoResponse]:
    """Busca internações com múltiplos filtros opcionais."""
    query = select(Internacao)

    if paciente_id:
        query = query.where(Internacao.paciente_id == paciente_id)
    if medico_id:
        query = query.where(Internacao.medico_id == medico_id)
    if quarto:
        query = query.where(Internacao.quarto.ilike(f"%{quarto}%"))
    if ativas is True:
        query = query.where(Internacao.data_saida == None)
    if ativas is False:
        query = query.where(Internacao.data_saida != None)
    if ano:
        query = query.where(func.strftime("%Y", Internacao.data_entrada) == str(ano))

    return await paginate(db, query)


@router.get(
    "/contagem-por-quarto",
    summary="Contar internações por quarto",
)
async def contar_por_quarto(db: AsyncSession = Depends(get_db)) -> list[dict]:
    """Retorna a quantidade de internações agrupadas por quarto."""
    result = await db.execute(
        select(Internacao.quarto, func.count().label("total"))
        .group_by(Internacao.quarto)
        .order_by(func.count().desc())
    )
    return [{"quarto": row.quarto, "total": row.total} for row in result]


@router.get(
    "/{id}",
    response_model=InternacaoResponse,
    summary="Buscar internação por ID",
)
async def buscar_por_id(
    id: int,
    db: AsyncSession = Depends(get_db),
) -> Internacao:
    """Retorna uma internação específica pelo ID."""
    internacao = await db.get(Internacao, id)
    if not internacao:
        raise HTTPException(status_code=404, detail="Internação não encontrada")
    return internacao


@router.put(
    "/{id}",
    response_model=InternacaoResponse,
    summary="Atualizar internação",
)
async def atualizar_internacao(
    id: int,
    dados: InternacaoCreate,
    db: AsyncSession = Depends(get_db),
) -> Internacao:
    """Atualiza os dados de uma internação existente."""
    internacao = await db.get(Internacao, id)
    if not internacao:
        raise HTTPException(status_code=404, detail="Internação não encontrada")

    if dados.data_saida and dados.data_saida <= dados.data_entrada:
        raise HTTPException(
            status_code=400,
            detail="data_saida deve ser posterior a data_entrada",
        )

    for key, value in dados.model_dump().items():
        setattr(internacao, key, value)

    await db.commit()
    await db.refresh(internacao)
    return internacao


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar internação",
)
async def deletar_internacao(
    id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove uma internação pelo ID."""
    internacao = await db.get(Internacao, id)
    if not internacao:
        raise HTTPException(status_code=404, detail="Internação não encontrada")

    await db.delete(internacao)
    await db.commit()