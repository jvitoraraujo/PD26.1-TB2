from typing import Any, List

from beanie import PydanticObjectId
from fastapi import APIRouter, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate

from app.models.medico import Medico
from app.models.especialidade import Especialidade

from app.schemas.medico_schema import (
    MedicoCreate,
    MedicoUpdate,
    MedicoResponse,
)
from app.core.exceptions import EntidadeNaoEncontradaException

router = APIRouter(
    prefix="/medicos",
    tags=["Médicos"]
)

#O crud básico:

@router.post("/", response_model=MedicoResponse)
async def criar_medico(medico_input: MedicoCreate) -> MedicoResponse:
    """Cria um novo médico, vinculando as especialidades informadas."""
    especialidades_db = []

    if medico_input.especialidades:
        for esp_id in medico_input.especialidades:
            esp = await Especialidade.get(PydanticObjectId(esp_id))
            if not esp:
                raise EntidadeNaoEncontradaException("Especialidade", esp_id)
            especialidades_db.append(esp)

    novo_medico = Medico(
        nome=medico_input.nome,
        crm=medico_input.crm,
        telefone=medico_input.telefone,
        email=medico_input.email,
        cidade=medico_input.cidade,
        uf=medico_input.uf,
        ativo=medico_input.ativo,
        especialidades=especialidades_db,
    )

    await novo_medico.insert()

    return MedicoResponse(
        id=str(novo_medico.id),
        nome=novo_medico.nome,
        crm=novo_medico.crm,
        telefone=novo_medico.telefone,
        email=novo_medico.email,
        cidade=novo_medico.cidade,
        uf=novo_medico.uf,
        ativo=novo_medico.ativo,
        especialidades=[str(e.id) for e in especialidades_db],
    )


@router.get("/", response_model=Page[Medico])
async def listar_medicos() -> Page[Medico]:
    """Lista todos os médicos com paginação."""
    return await apaginate(Medico.find_all(fetch_links=True))


@router.get("/{medico_id}", response_model=MedicoResponse)
async def obter_medico(medico_id: PydanticObjectId) -> MedicoResponse:
    """Busca um médico pelo ID."""
    medico = await Medico.get(medico_id, fetch_links=True)

    if not medico:
        raise EntidadeNaoEncontradaException("Médico", str(medico_id))

    return MedicoResponse(
        id=str(medico.id),
        nome=medico.nome,
        crm=medico.crm,
        telefone=medico.telefone,
        email=medico.email,
        cidade=medico.cidade,
        uf=medico.uf,
        ativo=medico.ativo,
        especialidades=[str(e.id) for e in medico.especialidades] if medico.especialidades else [],
    )


@router.put("/{medico_id}", response_model=MedicoResponse)
async def atualizar_medico(
    medico_id: PydanticObjectId,
    medico_input: MedicoUpdate
) -> MedicoResponse:
    """Atualiza parcialmente os dados de um médico, incluindo a lista de especialidades."""
    medico = await Medico.get(medico_id, fetch_links=True)

    if not medico:
        raise EntidadeNaoEncontradaException("Médico", str(medico_id))

    update_data = medico_input.model_dump(exclude_unset=True)

    if "especialidades" in update_data:
        especialidades_db = []
        for esp_id in update_data["especialidades"]:
            esp = await Especialidade.get(PydanticObjectId(esp_id))
            if not esp:
                raise EntidadeNaoEncontradaException("Especialidade", esp_id)
            especialidades_db.append(esp)
        medico.especialidades = especialidades_db
        del update_data["especialidades"]

    for campo, valor in update_data.items():
        setattr(medico, campo, valor)

    await medico.save()

    return MedicoResponse(
        id=str(medico.id),
        nome=medico.nome,
        crm=medico.crm,
        telefone=medico.telefone,
        email=medico.email,
        cidade=medico.cidade,
        uf=medico.uf,
        ativo=medico.ativo,
        especialidades=[str(e.id) for e in medico.especialidades] if medico.especialidades else [],
    )


@router.delete("/{medico_id}")
async def deletar_medico(medico_id: PydanticObjectId) -> dict:
    """Remove um médico pelo ID."""
    medico = await Medico.get(medico_id)

    if not medico:
        raise EntidadeNaoEncontradaException("Médico", str(medico_id))

    await medico.delete()
    return {"message": "Médico removido com sucesso"}


#Consultas obrigátorias

@router.get("/estatisticas/count")
async def contar_medicos() -> dict:
    """Retorna o total absoluto de médicos cadastrados."""
    total = await Medico.count()
    return {"total_medicos": total}


@router.get("/busca/ativos", response_model=List[Medico])
async def buscar_medicos_ativos(cidade: str = Query(None, description="Filtrar por cidade (Opcional)")):
    """Filtra médicos que estão com status ativo=True, podendo filtrar por cidade."""
    query = {"ativo": True}
    if cidade:
        query["cidade"] = cidade

    medicos = await Medico.find(query, fetch_links=True).to_list()
    return medicos


@router.get("/busca/nome", response_model=List[Medico])
async def buscar_medico_por_nome(termo: str = Query(..., description="Trecho do nome do médico")):
    """Busca médicos por texto parcial no nome (Regex - Case Insensitive)."""
    medicos = await Medico.find(
        {"nome": {"$regex": termo, "$options": "i"}},
        fetch_links=True
    ).to_list()
    return medicos


@router.get("/relatorio/agrupamento-uf")
async def agrupar_medicos_por_estado() -> List[Any]:
    """
    Aggregation Pipeline: Agrupa os médicos por UF (Estado)
    e conta quantos médicos existem em cada um.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$uf",
                "total_medicos": {"$sum": 1}
            }
        },
        {
            "$sort": {"total_medicos": -1}
        }
    ]

    resultado = await Medico.aggregate(pipeline).to_list()
    return resultado