from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException

from app.models.medico import Medico
from app.models.especialidade import Especialidade

from app.schemas.medico_schema import (
    MedicoCreate,
    MedicoResponse,
)

router = APIRouter(
    prefix="/medicos",
    tags=["Médicos"]
)


@router.get("/estatisticas/count")
async def contar_medicos():

    total = await Medico.count()

    return {
        "total_medicos": total
    }


@router.get("/")
async def listar_medicos():

    medicos = await Medico.find_all(
        fetch_links=True
    ).to_list()

    resposta = []

    for medico in medicos:

        resposta.append(
            {
                "id": str(medico.id),
                "nome": medico.nome,
                "crm": medico.crm,
                "telefone": medico.telefone,
                "email": medico.email,
                "cidade": medico.cidade,
                "uf": medico.uf,
                "ativo": medico.ativo,
                "especialidades": [
                    e.nome
                    for e in medico.especialidades
                ]
            }
        )

    return resposta


@router.get("/{medico_id}")
async def obter_medico(
    medico_id: str
):

    medico = await Medico.get(
        PydanticObjectId(medico_id),
        fetch_links=True
    )

    if not medico:
        raise HTTPException(
            status_code=404,
            detail="Médico não encontrado"
        )

    return {
        "id": str(medico.id),
        "nome": medico.nome,
        "crm": medico.crm,
        "telefone": medico.telefone,
        "email": medico.email,
        "cidade": medico.cidade,
        "uf": medico.uf,
        "ativo": medico.ativo,
        "especialidades": [
            str(e.id)
            for e in medico.especialidades
        ]
    }


@router.post("/")
async def criar_medico(
    medico_input: MedicoCreate
):

    especialidades = []

    for esp_id in medico_input.especialidades:

        esp = await Especialidade.get(
            PydanticObjectId(esp_id)
        )

        if esp:
            especialidades.append(esp)

    novo_medico = Medico(
        nome=medico_input.nome,
        crm=medico_input.crm,
        telefone=medico_input.telefone,
        email=medico_input.email,
        cidade=medico_input.cidade,
        uf=medico_input.uf,
        ativo=medico_input.ativo,
        especialidades=especialidades,
    )

    await novo_medico.insert()

    return {
        "id": str(novo_medico.id),
        "nome": novo_medico.nome,
        "crm": novo_medico.crm,
        "telefone": novo_medico.telefone,
        "email": novo_medico.email,
        "cidade": novo_medico.cidade,
        "uf": novo_medico.uf,
        "ativo": novo_medico.ativo,
        "especialidades": [
            str(e.id)
            for e in especialidades
        ]
    }


@router.put("/{medico_id}")
async def atualizar_medico(
    medico_id: str,
    medico_input: MedicoCreate
):

    medico = await Medico.get(
        PydanticObjectId(medico_id)
    )

    if not medico:
        raise HTTPException(
            status_code=404,
            detail="Médico não encontrado"
        )

    especialidades = []

    for esp_id in medico_input.especialidades:

        esp = await Especialidade.get(
            PydanticObjectId(esp_id)
        )

        if esp:
            especialidades.append(esp)

    medico.nome = medico_input.nome
    medico.crm = medico_input.crm
    medico.telefone = medico_input.telefone
    medico.email = medico_input.email
    medico.cidade = medico_input.cidade
    medico.uf = medico_input.uf
    medico.ativo = medico_input.ativo
    medico.especialidades = especialidades

    await medico.save()

    return {
        "message": "Médico atualizado com sucesso"
    }


@router.delete("/{medico_id}")
async def deletar_medico(
    medico_id: str
):

    medico = await Medico.get(
        PydanticObjectId(medico_id)
    )

    if not medico:
        raise HTTPException(
            status_code=404,
            detail="Médico não encontrado"
        )

    await medico.delete()

    return {
        "message": "Médico removido com sucesso"
    }