from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.db.database import get_db

from app.models.consulta import Consulta
from app.models.paciente import Paciente

from app.schemas.consulta_schema import (
    ConsultaCreate,
    ConsultaResponse
)

from datetime import datetime

router = APIRouter(
    prefix="/consultas",
    tags=["Consultas"]
)

#create
@router.post("/",
    response_model=ConsultaResponse
)
async def criar_consulta(
    consulta: ConsultaCreate,
    db: AsyncSession = Depends(get_db)
):

    paciente = await db.get(
        Paciente,
        consulta.paciente_id
    )

    if not paciente:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado"
        )

    nova = Consulta(**consulta.model_dump(), data_consulta=datetime.now())

    db.add(nova)

    await db.commit()

    await db.refresh(nova)

    return nova

#listar
@router.get("/",
    response_model=list[ConsultaResponse]
)
async def listar_consultas(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Consulta)
    )

    return result.scalars().all()

#buscar por id
@router.get("/{consulta_id}",
    response_model=ConsultaResponse
)
async def buscar_consulta(
    consulta_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Consulta).where(
            Consulta.id == consulta_id
        )
    )

    consulta = result.scalar_one_or_none()

    if not consulta:
        raise HTTPException(
            status_code=404,
            detail="Consulta não encontrada"
        )

    return consulta

#update
@router.put("/{consulta_id}",
    response_model=ConsultaResponse
)
async def atualizar_consulta(
    consulta_id: int,
    dados: ConsultaCreate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Consulta).where(
            Consulta.id == consulta_id
        )
    )

    consulta = result.scalar_one_or_none()

    if not consulta:
        raise HTTPException(
            status_code=404,
            detail="Consulta não encontrada"
        )

    for campo, valor in dados.model_dump().items():
        setattr(consulta, campo, valor)

    await db.commit()

    await db.refresh(consulta)

    return consulta

#delete
@router.delete("/{consulta_id}")
async def deletar_consulta(
    consulta_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Consulta).where(
            Consulta.id == consulta_id
        )
    )

    consulta = result.scalar_one_or_none()

    if not consulta:
        raise HTTPException(
            status_code=404,
            detail="Consulta não encontrada"
        )

    await db.delete(consulta)

    await db.commit()

    return {
        "message": "Consulta removida com sucesso"
    }