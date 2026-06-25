from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException

from app.models.consulta import Consulta
from app.models.exame import Exame

from app.schemas.exame_schema import (
    ExameCreate,
    ExameUpdate,
    ExameResponse,
)

router = APIRouter(
    prefix="/exames",
    tags=["Exames"]
)


@router.post("/", response_model=ExameResponse)
async def criar_exame(
    exame: ExameCreate
):

    consulta = await Consulta.get(
        PydanticObjectId(exame.consulta_id)
    )

    if not consulta:
        raise HTTPException(
            status_code=404,
            detail="Consulta não encontrada"
        )

    novo = Exame(
        tipo=exame.tipo,
        resultado=exame.resultado,
        consulta=consulta,
    )

    await novo.insert()

    return ExameResponse(
        id=str(novo.id),
        tipo=novo.tipo,
        resultado=novo.resultado,
        consulta_id=str(consulta.id),
    )


@router.get("/", response_model=list[ExameResponse])
async def listar_exames():

    exames = await Exame.find_all(
        fetch_links=True
    ).to_list()

    resposta = []

    for exame in exames:

        resposta.append(
            ExameResponse(
                id=str(exame.id),
                tipo=exame.tipo,
                resultado=exame.resultado,
                consulta_id=str(exame.consulta.id),
            )
        )

    return resposta


@router.get("/{exame_id}", response_model=ExameResponse)
async def buscar_exame(
    exame_id: str
):

    exame = await Exame.get(
        PydanticObjectId(exame_id),
        fetch_links=True
    )

    if not exame:
        raise HTTPException(
            status_code=404,
            detail="Exame não encontrado"
        )

    return ExameResponse(
        id=str(exame.id),
        tipo=exame.tipo,
        resultado=exame.resultado,
        consulta_id=str(exame.consulta.id),
    )


@router.put("/{exame_id}", response_model=ExameResponse)
async def atualizar_exame(
    exame_id: str,
    dados: ExameUpdate
):

    exame = await Exame.get(
        PydanticObjectId(exame_id),
        fetch_links=True
    )

    if not exame:
        raise HTTPException(
            status_code=404,
            detail="Exame não encontrado"
        )

    update_data = dados.model_dump(
        exclude_unset=True
    )

    for campo, valor in update_data.items():
        setattr(exame, campo, valor)

    await exame.save()

    return ExameResponse(
        id=str(exame.id),
        tipo=exame.tipo,
        resultado=exame.resultado,
        consulta_id=str(exame.consulta.id),
    )


@router.delete("/{exame_id}")
async def deletar_exame(
    exame_id: str
):

    exame = await Exame.get(
        PydanticObjectId(exame_id)
    )

    if not exame:
        raise HTTPException(
            status_code=404,
            detail="Exame não encontrado"
        )

    await exame.delete()

    return {
        "message": "Exame removido com sucesso"
    }