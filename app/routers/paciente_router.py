from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException

from app.models.paciente import Paciente
from app.schemas.paciente_schema import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
)

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)


@router.post("/", response_model=PacienteResponse)
async def criar_paciente(
    paciente: PacienteCreate
):
    novo = Paciente(**paciente.model_dump())

    await novo.insert()

    return PacienteResponse(
        id=str(novo.id),
        nome=novo.nome,
        cpf=novo.cpf,
        telefone=novo.telefone,
        email=novo.email,
        cidade=novo.cidade,
        uf=novo.uf,
    )


@router.get("/", response_model=list[PacienteResponse])
async def listar_pacientes():

    pacientes = await Paciente.find_all().to_list()

    return [
        PacienteResponse(
            id=str(p.id),
            nome=p.nome,
            cpf=p.cpf,
            telefone=p.telefone,
            email=p.email,
            cidade=p.cidade,
            uf=p.uf,
        )
        for p in pacientes
    ]


@router.get("/{paciente_id}", response_model=PacienteResponse)
async def buscar_paciente(
    paciente_id: str
):

    paciente = await Paciente.get(
        PydanticObjectId(paciente_id)
    )

    if not paciente:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado"
        )

    return PacienteResponse(
        id=str(paciente.id),
        nome=paciente.nome,
        cpf=paciente.cpf,
        telefone=paciente.telefone,
        email=paciente.email,
        cidade=paciente.cidade,
        uf=paciente.uf,
    )


@router.put(
    "/{paciente_id}",
    response_model=PacienteResponse
)
async def atualizar_paciente(
    paciente_id: str,
    dados: PacienteUpdate
):

    paciente = await Paciente.get(
        PydanticObjectId(paciente_id)
    )

    if not paciente:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado"
        )

    update_data = dados.model_dump(
        exclude_unset=True
    )

    for campo, valor in update_data.items():
        setattr(paciente, campo, valor)

    await paciente.save()

    return PacienteResponse(
        id=str(paciente.id),
        nome=paciente.nome,
        cpf=paciente.cpf,
        telefone=paciente.telefone,
        email=paciente.email,
        cidade=paciente.cidade,
        uf=paciente.uf,
    )


@router.delete("/{paciente_id}")
async def deletar_paciente(
    paciente_id: str
):

    paciente = await Paciente.get(
        PydanticObjectId(paciente_id)
    )

    if not paciente:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado"
        )

    await paciente.delete()

    return {
        "message": "Paciente removido com sucesso"
    }