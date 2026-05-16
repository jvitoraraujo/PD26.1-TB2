from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.paciente import Paciente
from app.schemas.paciente_schema import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse
)

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)

#create
@router.post("/", response_model=PacienteResponse)
async def criar_paciente(
    paciente: PacienteCreate,
    db: AsyncSession = Depends(get_db)
):
    novo = Paciente(**paciente.model_dump())

    db.add(novo)

    await db.commit()
    await db.refresh(novo)

    return novo

#read all
@router.get("/", response_model=list[PacienteResponse])
async def listar_pacientes(db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(Paciente).options(
            selectinload(Paciente.consultas)
        )
    )

    return result.scalars().all()

#busca por id
@router.get("/{paciente_id}", response_model=PacienteResponse)
async def buscar_paciente(paciente_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(Paciente).options(
            selectinload(Paciente.consultas)
        ).where(Paciente.id == paciente_id)
    )

    paciente = result.scalar_one_or_none()

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    return paciente

#update
#update
@router.put("/{paciente_id}",
    response_model=PacienteResponse
)
async def atualizar_paciente(
    paciente_id: int,
    dados: PacienteUpdate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Paciente).where(
            Paciente.id == paciente_id
        )
    )

    paciente = result.scalar_one_or_none()

    if not paciente:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado"
        )

    for campo, valor in dados.model_dump(
        exclude_unset=True
    ).items():
        setattr(paciente, campo, valor)

    await db.commit()

    await db.refresh(paciente)

    return paciente

#delete
@router.delete("/{paciente_id}")
async def deletar_paciente(
    paciente_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Paciente).where(
            Paciente.id == paciente_id
        )
    )

    paciente = result.scalar_one_or_none()

    if not paciente:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado"
        )

    await db.delete(paciente)
    await db.commit()

    return {
        "message": "Paciente removido com sucesso"
    }