from typing import Any, List

from beanie import PydanticObjectId
from fastapi import APIRouter, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate

from app.models.consulta import Consulta
from app.models.exame import Exame

from app.schemas.exame_schema import (
    ExameCreate,
    ExameUpdate,
    ExameResponse,
)
from app.core.exceptions import EntidadeNaoEncontradaException

router = APIRouter(
    prefix="/exames",
    tags=["Exames"]
)

#O crud básico:

@router.post("/", response_model=ExameResponse)
async def criar_exame(exame: ExameCreate) -> ExameResponse:
    """Cria um novo exame, vinculado a uma consulta existente."""
    consulta = await Consulta.get(PydanticObjectId(exame.consulta_id))

    if not consulta:
        raise EntidadeNaoEncontradaException("Consulta", exame.consulta_id)

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


@router.get("/", response_model=Page[Exame])
async def listar_exames() -> Page[Exame]:
    """Lista todos os exames com paginação."""
    return await apaginate(Exame.find_all(fetch_links=True))


@router.get("/{exame_id}", response_model=ExameResponse)
async def buscar_exame(exame_id: PydanticObjectId) -> ExameResponse:
    """Busca um exame pelo ID."""
    exame = await Exame.get(exame_id, fetch_links=True)

    if not exame:
        raise EntidadeNaoEncontradaException("Exame", str(exame_id))

    return ExameResponse(
        id=str(exame.id),
        tipo=exame.tipo,
        resultado=exame.resultado,
        consulta_id=str(exame.consulta.id),
    )


@router.put("/{exame_id}", response_model=ExameResponse)
async def atualizar_exame(
    exame_id: PydanticObjectId,
    dados: ExameUpdate
) -> ExameResponse:
    """Atualiza parcialmente os dados de um exame."""
    exame = await Exame.get(exame_id, fetch_links=True)

    if not exame:
        raise EntidadeNaoEncontradaException("Exame", str(exame_id))

    update_data = dados.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(exame, campo, valor)

    await exame.save()

    return ExameResponse(
        id=str(exame.id),
        tipo=exame.tipo,
        resultado=exame.resultado,
        consulta_id=str(exame.consulta.id) if exame.consulta else None,
    )


@router.delete("/{exame_id}")
async def deletar_exame(exame_id: PydanticObjectId) -> dict:
    """Remove um exame pelo ID."""
    exame = await Exame.get(exame_id)

    if not exame:
        raise EntidadeNaoEncontradaException("Exame", str(exame_id))

    await exame.delete()
    return {"message": "Exame removido com sucesso"}


#Consultas obrigátorias

@router.get("/busca/tipo", response_model=List[Exame])
async def buscar_exame_por_tipo(termo: str = Query(..., description="Trecho do tipo de exame")):
    """Busca exames por texto parcial no tipo (Regex - Case Insensitive)."""
    exames = await Exame.find(
        {"tipo": {"$regex": termo, "$options": "i"}},
        fetch_links=True
    ).to_list()
    return exames


@router.get("/consulta/{consulta_id}", response_model=List[Exame])
async def buscar_exames_da_consulta(consulta_id: PydanticObjectId):
    """Busca por relacionamento: Traz todos os exames atrelados a uma consulta específica."""
    consulta = await Consulta.get(consulta_id)
    if not consulta:
        raise EntidadeNaoEncontradaException("Consulta", str(consulta_id))

    exames = await Exame.find(
        {"consulta.$id": consulta_id},
        fetch_links=True
    ).to_list()
    return exames


@router.get("/relatorio/agrupamento")
async def agrupar_exames_por_tipo() -> List[Any]:
    """
    Aggregation Pipeline: Agrupa os exames pelo campo 'tipo'
    e conta quantos exames de cada tipo foram realizados.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$tipo",
                "total_realizados": {"$sum": 1}
            }
        },
        {
            "$sort": {"total_realizados": -1}
        }
    ]

    resultado = await Exame.aggregate(pipeline).to_list()
    return resultado


@router.get("/paciente/{paciente_id}", response_model=List[dict])
async def listar_exames_do_paciente(paciente_id: PydanticObjectId):
    """
    Consulta envolvendo múltiplas coleções: lista todos os exames realizados
    por um paciente, cruzando Exame -> Consulta -> Paciente.
    """
    pipeline = [
        {
            "$lookup": {
                "from": "consultas",
                "localField": "consulta.$id",
                "foreignField": "_id",
                "as": "consulta_info",
            }
        },
        {"$unwind": "$consulta_info"},
        {"$match": {"consulta_info.paciente.$id": paciente_id}},
        {
            "$project": {
                "_id": 1,
                "tipo": 1,
                "resultado": 1,
                "data_consulta": "$consulta_info.data_consulta",
            }
        },
        {"$sort": {"data_consulta": -1}},
    ]

    resultado = await Exame.aggregate(pipeline).to_list()
    return resultado