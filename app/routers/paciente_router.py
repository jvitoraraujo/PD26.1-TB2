from typing import Any, List

from beanie import PydanticObjectId
from fastapi import APIRouter, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate

from app.models.paciente import Paciente
from app.schemas.paciente_schema import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
)
from app.core.exceptions import EntidadeNaoEncontradaException

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)

#O crud básico:

@router.post("/", response_model=PacienteResponse)
async def criar_paciente(paciente: PacienteCreate) -> PacienteResponse:
    """Cria um novo paciente."""
    novo = Paciente(**paciente.model_dump())
    await novo.insert()
    return PacienteResponse(**{**novo.model_dump(exclude={"id"}), "id": str(novo.id)})


@router.get("/", response_model=Page[Paciente])
async def listar_pacientes() -> Page[Paciente]:
    """Lista todos os pacientes com paginação."""
    return await apaginate(Paciente.find_all())


@router.get("/{paciente_id}", response_model=PacienteResponse)
async def buscar_paciente(paciente_id: PydanticObjectId) -> PacienteResponse:
    """Busca um paciente pelo ID."""
    paciente = await Paciente.get(paciente_id)
    if not paciente:
        raise EntidadeNaoEncontradaException("Paciente", str(paciente_id))
    return PacienteResponse(**{**paciente.model_dump(exclude={"id"}), "id": str(paciente.id)})


@router.put("/{paciente_id}", response_model=PacienteResponse)
async def atualizar_paciente(
    paciente_id: PydanticObjectId,
    dados: PacienteUpdate
) -> PacienteResponse:
    """Atualiza parcialmente os dados de um paciente."""
    paciente = await Paciente.get(paciente_id)
    if not paciente:
        raise EntidadeNaoEncontradaException("Paciente", str(paciente_id))

    update_data = dados.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(paciente, campo, valor)

    await paciente.save()
    return PacienteResponse(**{**paciente.model_dump(exclude={"id"}), "id": str(paciente.id)})


@router.delete("/{paciente_id}")
async def deletar_paciente(paciente_id: PydanticObjectId) -> dict:
    """Remove um paciente pelo ID."""
    paciente = await Paciente.get(paciente_id)
    if not paciente:
        raise EntidadeNaoEncontradaException("Paciente", str(paciente_id))

    await paciente.delete()
    return {"message": "Paciente removido com sucesso"}


#Consultas obrigátorias

@router.get("/busca/nome", response_model=List[Paciente])
async def buscar_por_nome(termo: str = Query(..., description="Trecho do nome do paciente")):
    """Busca pacientes por texto parcial no nome."""
    return await Paciente.find(
        {"nome": {"$regex": termo, "$options": "i"}}
    ).to_list()


@router.get("/busca/cpf/{cpf}", response_model=Paciente)
async def buscar_por_cpf(cpf: str):
    """Busca um paciente único pelo CPF."""
    paciente = await Paciente.find_one(Paciente.cpf == cpf)
    if not paciente:
        raise EntidadeNaoEncontradaException("Paciente", cpf)
    return paciente


@router.get("/relatorio/distribuicao-cidade")
async def relatorio_por_cidade() -> List[Any]:
    """
    Aggregation Pipeline: Agrupa pacientes por cidade e conta quantos
    pacientes residem em cada uma.
    """
    pipeline = [
        {"$group": {"_id": "$cidade", "total_pacientes": {"$sum": 1}}},
        {"$sort": {"total_pacientes": -1}}
    ]
    return await Paciente.aggregate(pipeline).to_list()