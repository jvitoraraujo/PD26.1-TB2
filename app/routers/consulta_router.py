from datetime import datetime
from typing import Any, List

from beanie import PydanticObjectId
from fastapi import APIRouter, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate

from app.models.consulta import Consulta
from app.models.medico import Medico
from app.models.paciente import Paciente

from app.schemas.consulta_schema import (
    ConsultaCreate,
    ConsultaUpdate,
    ConsultaResponse,
)
from app.core.exceptions import EntidadeNaoEncontradaException

router = APIRouter(
    prefix="/consultas",
    tags=["Consultas"]
)

#O crud básico:

@router.post("/", response_model=ConsultaResponse)
async def criar_consulta(dados: ConsultaCreate) -> ConsultaResponse:
    """Cria uma nova consulta, vinculando paciente e médico existentes."""
    paciente = await Paciente.get(PydanticObjectId(dados.paciente_id))
    if not paciente:
        raise EntidadeNaoEncontradaException("Paciente", dados.paciente_id)

    medico = await Medico.get(PydanticObjectId(dados.medico_id))
    if not medico:
        raise EntidadeNaoEncontradaException("Médico", dados.medico_id)

    consulta = Consulta(
        data_consulta=datetime.now(),
        diagnostico=dados.diagnostico,
        paciente=paciente,
        medico=medico,
    )
    await consulta.insert()

    return ConsultaResponse(
        id=str(consulta.id),
        data_consulta=consulta.data_consulta,
        diagnostico=consulta.diagnostico,
        paciente_id=str(paciente.id),
        medico_id=str(medico.id),
    )


@router.get("/", response_model=Page[Consulta])
async def listar_consultas() -> Page[Consulta]:
    """Lista todas as consultas com paginação, ordenadas pela mais recente."""
    return await apaginate(Consulta.find_all(fetch_links=True).sort("-data_consulta"))


@router.get("/{consulta_id}", response_model=ConsultaResponse)
async def buscar_consulta(consulta_id: PydanticObjectId) -> ConsultaResponse:
    """Busca uma consulta pelo ID."""
    consulta = await Consulta.get(consulta_id, fetch_links=True)
    if not consulta:
        raise EntidadeNaoEncontradaException("Consulta", str(consulta_id))

    return ConsultaResponse(
        id=str(consulta.id),
        data_consulta=consulta.data_consulta,
        diagnostico=consulta.diagnostico,
        paciente_id=str(consulta.paciente.id),
        medico_id=str(consulta.medico.id),
    )


@router.put("/{consulta_id}", response_model=ConsultaResponse)
async def atualizar_consulta(
    consulta_id: PydanticObjectId,
    dados: ConsultaUpdate
) -> ConsultaResponse:
    """Atualiza parcialmente os dados de uma consulta."""
    consulta = await Consulta.get(consulta_id, fetch_links=True)
    if not consulta:
        raise EntidadeNaoEncontradaException("Consulta", str(consulta_id))

    update_data = dados.model_dump(exclude_unset=True)

 
    if "paciente_id" in update_data:
        novo_paciente_id = update_data.pop("paciente_id")
        paciente = await Paciente.get(PydanticObjectId(novo_paciente_id))
        if not paciente:
            raise EntidadeNaoEncontradaException("Paciente", novo_paciente_id)
        consulta.paciente = paciente

    if "medico_id" in update_data:
        novo_medico_id = update_data.pop("medico_id")
        medico = await Medico.get(PydanticObjectId(novo_medico_id))
        if not medico:
            raise EntidadeNaoEncontradaException("Médico", novo_medico_id)
        consulta.medico = medico

    for campo, valor in update_data.items():
        setattr(consulta, campo, valor)

    await consulta.save()

    return ConsultaResponse(
        id=str(consulta.id),
        data_consulta=consulta.data_consulta,
        diagnostico=consulta.diagnostico,
        paciente_id=str(consulta.paciente.id) if consulta.paciente else None,
        medico_id=str(consulta.medico.id) if consulta.medico else None,
    )


@router.delete("/{consulta_id}")
async def deletar_consulta(consulta_id: PydanticObjectId) -> dict:
    """Remove uma consulta pelo ID."""
    consulta = await Consulta.get(consulta_id)
    if not consulta:
        raise EntidadeNaoEncontradaException("Consulta", str(consulta_id))

    await consulta.delete()
    return {"message": "Consulta removida com sucesso"}


#Consultas obrigátorias

@router.get("/busca/diagnostico", response_model=List[Consulta])
async def buscar_por_texto_regex(termo: str = Query(..., description="Trecho do diagnóstico")):
    """Busca consultas por texto parcial no diagnóstico (Regex - Case Insensitive)."""
    consultas = await Consulta.find(
        {"diagnostico": {"$regex": termo, "$options": "i"}},
        fetch_links=True
    ).to_list()
    return consultas


@router.get("/filtro/data", response_model=List[Consulta])
async def filtrar_por_data(
    data_inicio: datetime = Query(...),
    data_fim: datetime = Query(...)
):
    """Filtra consultas em um intervalo de datas."""
    consultas = await Consulta.find(
        Consulta.data_consulta >= data_inicio,
        Consulta.data_consulta <= data_fim,
        fetch_links=True
    ).to_list()
    return consultas


@router.get("/relatorio/agrupamento")
async def relatorio_aggregation() -> List[Any]:
    """
    Aggregation Pipeline: Agrupa as consultas pelo ID do Médico
    e conta quantas consultas cada um realizou.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$medico.$id",
                "total_consultas": {"$sum": 1}
            }
        },
        {
            "$sort": {"total_consultas": -1}
        }
    ]

    resultado = await Consulta.aggregate(pipeline).to_list()
    return resultado


@router.get("/medico/{medico_id}", response_model=List[ConsultaResponse])
async def listar_consultas_do_medico(medico_id: PydanticObjectId):
    """
    Consulta envolvendo múltiplas coleções: lista todas as consultas
    realizadas por um médico específico, já com os dados do paciente vinculado.
    """
    medico = await Medico.get(medico_id)
    if not medico:
        raise EntidadeNaoEncontradaException("Médico", str(medico_id))

    consultas = await Consulta.find(
        {"medico.$id": medico_id},
        fetch_links=True
    ).sort("-data_consulta").to_list()

    return [
        ConsultaResponse(
            id=str(c.id),
            data_consulta=c.data_consulta,
            diagnostico=c.diagnostico,
            paciente_id=str(c.paciente.id),
            medico_id=str(c.medico.id),
        )
        for c in consultas
    ]