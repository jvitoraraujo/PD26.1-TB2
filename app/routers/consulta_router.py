from datetime import datetime

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException

from app.models.consulta import Consulta
from app.models.medico import Medico
from app.models.paciente import Paciente

from app.schemas.consulta_schema import (
    ConsultaCreate,
    ConsultaResponse,
)

router = APIRouter(
    prefix="/consultas",
    tags=["Consultas"]
)


@router.post("/", response_model=ConsultaResponse)
async def criar_consulta(
    dados: ConsultaCreate
):

    paciente = await Paciente.get(
        PydanticObjectId(dados.paciente_id)
    )

    if not paciente:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado"
        )

    medico = await Medico.get(
        PydanticObjectId(dados.medico_id)
    )

    if not medico:
        raise HTTPException(
            status_code=404,
            detail="Médico não encontrado"
        )

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


@router.get("/", response_model=list[ConsultaResponse])
async def listar_consultas():

    consultas = await Consulta.find_all(
        fetch_links=True
    ).to_list()

    resposta = []

    for consulta in consultas:

        resposta.append(
            ConsultaResponse(
                id=str(consulta.id),
                data_consulta=consulta.data_consulta,
                diagnostico=consulta.diagnostico,
                paciente_id=str(consulta.paciente.id),
                medico_id=str(consulta.medico.id),
            )
        )

    return resposta


@router.get("/{consulta_id}", response_model=ConsultaResponse)
async def buscar_consulta(
    consulta_id: str
):

    consulta = await Consulta.get(
        PydanticObjectId(consulta_id),
        fetch_links=True
    )

    if not consulta:
        raise HTTPException(
            status_code=404,
            detail="Consulta não encontrada"
        )

    return ConsultaResponse(
        id=str(consulta.id),
        data_consulta=consulta.data_consulta,
        diagnostico=consulta.diagnostico,
        paciente_id=str(consulta.paciente.id),
        medico_id=str(consulta.medico.id),
    )


@router.put("/{consulta_id}", response_model=ConsultaResponse)
async def atualizar_consulta(
    consulta_id: str,
    dados: ConsultaCreate
):

    consulta = await Consulta.get(
        PydanticObjectId(consulta_id),
        fetch_links=True
    )

    if not consulta:
        raise HTTPException(
            status_code=404,
            detail="Consulta não encontrada"
        )

    paciente = await Paciente.get(
        PydanticObjectId(dados.paciente_id)
    )

    medico = await Medico.get(
        PydanticObjectId(dados.medico_id)
    )

    consulta.diagnostico = dados.diagnostico
    consulta.paciente = paciente
    consulta.medico = medico

    await consulta.save()

    return ConsultaResponse(
        id=str(consulta.id),
        data_consulta=consulta.data_consulta,
        diagnostico=consulta.diagnostico,
        paciente_id=str(paciente.id),
        medico_id=str(medico.id),
    )


@router.delete("/{consulta_id}")
async def deletar_consulta(
    consulta_id: str
):

    consulta = await Consulta.get(
        PydanticObjectId(consulta_id)
    )

    if not consulta:
        raise HTTPException(
            status_code=404,
            detail="Consulta não encontrada"
        )

    await consulta.delete()

    return {
        "message": "Consulta removida com sucesso"
    }


@router.get("/count")
async def contar_consultas():

    total = await Consulta.count()

    return {
        "total": total
    }