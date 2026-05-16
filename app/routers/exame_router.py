from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db

from app.models.exame import Exame
from app.models.consulta import Consulta

from app.schemas.exame_schema import (
    ExameCreate,
    ExameUpdate,
    ExameResponse
)

router = APIRouter(
    prefix="/exames",
    tags=["Exames"]
)

#create
@router.post("/", response_model=ExameResponse)
async def criar_exame(
    exame: ExameCreate,
    db: AsyncSession = Depends(get_db)
):

    consulta = await db.get(
        Consulta,
        exame.consulta_id
    )

    if not consulta:
        raise HTTPException(
            status_code=404,
            detail="Consulta não encontrado"
        )

    novo = Exame(**exame.model_dump())

    db.add(novo)

    await db.commit()
    await db.refresh(novo)

    return novo

#read all
@router.get("/", response_model=list[ExameResponse])
async def listar_exames(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Exame)
    )

    return result.scalars().all()

#read by id
@router.get("/{exame_id}",
    response_model=ExameResponse
)
async def buscar_exame(
    exame_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Exame).where(
            Exame.id == exame_id
        )
    )

    exame = result.scalar_one_or_none()

    if not exame:
        raise HTTPException(
            status_code=404,
            detail="Exame não encontrado"
        )

    return exame

#update
@router.put("/{exame_id}",
    response_model=ExameResponse
)
async def atualizar_exame(
    exame_id: int,
    dados: ExameUpdate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Exame).where(
            Exame.id == exame_id
        )
    )

    exame = result.scalar_one_or_none()

    if not exame:
        raise HTTPException(
            status_code=404,
            detail="Exame não encontrado"
        )

    for campo, valor in dados.model_dump(
        exclude_unset=True
    ).items():
        setattr(exame, campo, valor)

    await db.commit()
    await db.refresh(exame)

    return exame

#delete
@router.delete("/{exame_id}")
async def deletar_exame(
    exame_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Exame).where(
            Exame.id == exame_id
        )
    )

    exame = result.scalar_one_or_none()

    if not exame:
        raise HTTPException(
            status_code=404,
            detail="Exame não encontrado"
        )

    await db.delete(exame)

    await db.commit()

    return {
        "message": "Exame removido com sucesso"
    }