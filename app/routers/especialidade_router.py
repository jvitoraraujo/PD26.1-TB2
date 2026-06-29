from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate

from app.models.especialidade import Especialidade
from app.schemas.especialidade_schema import (
    EspecialidadeCreate,
    EspecialidadeResponse,
)
from app.core.exceptions import EntidadeNaoEncontradaException

router = APIRouter(
    prefix="/especialidades",
    tags=["Especialidades"]
)

#O crud básico

@router.post("/", response_model=EspecialidadeResponse)
async def criar_especialidade(dados: EspecialidadeCreate) -> EspecialidadeResponse:
    """Cria uma nova especialidade médica."""
    nova = Especialidade(nome=dados.nome)
    await nova.insert()
    return EspecialidadeResponse(id=str(nova.id), nome=nova.nome)


@router.get("/", response_model=Page[Especialidade])
async def listar_especialidades() -> Page[Especialidade]:
    """Lista todas as especialidades com paginação."""
    return await apaginate(Especialidade.find_all())


@router.get("/{especialidade_id}", response_model=EspecialidadeResponse)
async def buscar_especialidade(especialidade_id: PydanticObjectId) -> EspecialidadeResponse:
    """Busca uma especialidade pelo ID."""
    especialidade = await Especialidade.get(especialidade_id)
    if not especialidade:
        raise EntidadeNaoEncontradaException("Especialidade", str(especialidade_id))
    return EspecialidadeResponse(id=str(especialidade.id), nome=especialidade.nome)


@router.put("/{especialidade_id}", response_model=EspecialidadeResponse)
async def atualizar_especialidade(
    especialidade_id: PydanticObjectId,
    dados: EspecialidadeCreate
) -> EspecialidadeResponse:
    """Atualiza o nome de uma especialidade."""
    especialidade = await Especialidade.get(especialidade_id)
    if not especialidade:
        raise EntidadeNaoEncontradaException("Especialidade", str(especialidade_id))

    especialidade.nome = dados.nome
    await especialidade.save()

    return EspecialidadeResponse(id=str(especialidade.id), nome=especialidade.nome)


@router.delete("/{especialidade_id}")
async def deletar_especialidade(especialidade_id: PydanticObjectId) -> dict:
    """Remove uma especialidade pelo ID."""
    especialidade = await Especialidade.get(especialidade_id)
    if not especialidade:
        raise EntidadeNaoEncontradaException("Especialidade", str(especialidade_id))

    await especialidade.delete()
    return {"message": "Especialidade removida com sucesso"}


#Consultas obrigátorias

@router.get("/busca/nome", response_model=List[Especialidade])
async def buscar_especialidade_por_nome(
    termo: str = Query(..., description="Trecho do nome da especialidade")
):
    """Busca especialidades por texto parcial no nome (Regex - Case Insensitive)."""
    return await Especialidade.find(
        {"nome": {"$regex": termo, "$options": "i"}}
    ).to_list()