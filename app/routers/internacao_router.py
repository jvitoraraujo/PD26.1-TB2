from datetime import datetime
from typing import Any, List

from beanie import PydanticObjectId
from fastapi import APIRouter, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate

from app.models.internacao import Internacao
from app.models.medico import Medico
from app.models.paciente import Paciente

from app.schemas.internacao_schema import (
    InternacaoCreate,
    InternacaoUpdate,
    InternacaoResponse,
)
from app.core.exceptions import EntidadeNaoEncontradaException

router = APIRouter(
    prefix="/internacoes",
    tags=["Internações"]
)

#O crud básico:

@router.post("/", response_model=InternacaoResponse)
async def criar_internacao(dados: InternacaoCreate) -> InternacaoResponse:
    """Cria uma nova internação, vinculando paciente e médico existentes."""
    paciente = await Paciente.get(PydanticObjectId(dados.paciente_id))
    if not paciente:
        raise EntidadeNaoEncontradaException("Paciente", dados.paciente_id)

    medico = await Medico.get(PydanticObjectId(dados.medico_id))
    if not medico:
        raise EntidadeNaoEncontradaException("Médico", dados.medico_id)

    internacao = Internacao(
        data_entrada=dados.data_entrada,
        data_saida=dados.data_saida,
        quarto=dados.quarto,
        motivo=dados.motivo,
        observacoes=dados.observacoes,
        valor_diaria=dados.valor_diaria,
        paciente=paciente,
        medico=medico,
    )
    await internacao.insert()

    return InternacaoResponse(
        id=str(internacao.id),
        data_entrada=internacao.data_entrada,
        data_saida=internacao.data_saida,
        quarto=internacao.quarto,
        motivo=internacao.motivo,
        observacoes=internacao.observacoes,
        valor_diaria=internacao.valor_diaria,
        paciente_id=str(paciente.id),
        medico_id=str(medico.id),
    )


@router.get("/", response_model=Page[Internacao])
async def listar_internacoes() -> Page[Internacao]:
    """Lista todas as internações com paginação, ordenadas pela data de entrada."""
    return await apaginate(Internacao.find_all(fetch_links=True).sort("-data_entrada"))


@router.get("/{internacao_id}", response_model=InternacaoResponse)
async def buscar_internacao(internacao_id: PydanticObjectId) -> InternacaoResponse:
    """Busca uma internação pelo ID."""
    internacao = await Internacao.get(internacao_id, fetch_links=True)

    if not internacao:
        raise EntidadeNaoEncontradaException("Internação", str(internacao_id))

    return InternacaoResponse(
        id=str(internacao.id),
        data_entrada=internacao.data_entrada,
        data_saida=internacao.data_saida,
        quarto=internacao.quarto,
        motivo=internacao.motivo,
        observacoes=internacao.observacoes,
        valor_diaria=internacao.valor_diaria,
        paciente_id=str(internacao.paciente.id),
        medico_id=str(internacao.medico.id),
    )


@router.put("/{internacao_id}", response_model=InternacaoResponse)
async def atualizar_internacao(
    internacao_id: PydanticObjectId,
    dados: InternacaoUpdate
) -> InternacaoResponse:
    """Atualiza parcialmente os dados de uma internação."""
    internacao = await Internacao.get(internacao_id, fetch_links=True)

    if not internacao:
        raise EntidadeNaoEncontradaException("Internação", str(internacao_id))

    update_data = dados.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(internacao, campo, valor)

    await internacao.save()

    return InternacaoResponse(
        id=str(internacao.id),
        data_entrada=internacao.data_entrada,
        data_saida=internacao.data_saida,
        quarto=internacao.quarto,
        motivo=internacao.motivo,
        observacoes=internacao.observacoes,
        valor_diaria=internacao.valor_diaria,
        paciente_id=str(internacao.paciente.id) if internacao.paciente else None,
        medico_id=str(internacao.medico.id) if internacao.medico else None,
    )


@router.delete("/{internacao_id}")
async def deletar_internacao(internacao_id: PydanticObjectId) -> dict:
    """Remove uma internação pelo ID."""
    internacao = await Internacao.get(internacao_id)

    if not internacao:
        raise EntidadeNaoEncontradaException("Internação", str(internacao_id))

    await internacao.delete()
    return {"message": "Internação removida com sucesso"}


#Consultas obrigátorias

@router.get("/busca/ativas", response_model=List[Internacao])
async def buscar_internacoes_ativas():
    """Filtro: Traz apenas os pacientes que ainda estão internados (data_saida nula)."""
    internacoes = await Internacao.find(
        Internacao.data_saida == None,
        fetch_links=True
    ).to_list()
    return internacoes


@router.get("/busca/motivo", response_model=List[Internacao])
async def buscar_por_motivo(termo: str = Query(..., description="Trecho do motivo da internação")):
    """Busca internações por texto parcial no motivo (Regex - Case Insensitive)."""
    internacoes = await Internacao.find(
        {"motivo": {"$regex": termo, "$options": "i"}},
        fetch_links=True
    ).to_list()
    return internacoes


@router.get("/filtro/ano", response_model=List[Internacao])
async def filtrar_internacoes_por_ano(
    ano: int = Query(..., description="Ano de entrada da internação, ex: 2025")
):
    """Filtro por data/ano: lista internações cuja data_entrada está dentro do ano informado."""
    inicio = datetime(ano, 1, 1)
    fim = datetime(ano, 12, 31, 23, 59, 59)

    internacoes = await Internacao.find(
        Internacao.data_entrada >= inicio,
        Internacao.data_entrada <= fim,
        fetch_links=True
    ).sort("-data_entrada").to_list()
    return internacoes


@router.get("/relatorio/faturamento-quarto")
async def relatorio_faturamento_por_quarto() -> List[Any]:
    """
    Aggregation Pipeline: Agrupa as internações por quarto,
    conta quantas ocorreram e soma o valor total projetado das diárias.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$quarto",
                "total_internacoes": {"$sum": 1},
                "valor_total_diarias": {"$sum": "$valor_diaria"}
            }
        },
        {
            "$sort": {"valor_total_diarias": -1}
        }
    ]

    resultado = await Internacao.aggregate(pipeline).to_list()
    return resultado


@router.get("/medico/{medico_id}", response_model=List[InternacaoResponse])
async def listar_internacoes_do_medico(medico_id: PydanticObjectId):
    """
    Consulta envolvendo múltiplas coleções: lista todas as internações
    conduzidas por um médico específico.
    """
    medico = await Medico.get(medico_id)
    if not medico:
        raise EntidadeNaoEncontradaException("Médico", str(medico_id))

    internacoes = await Internacao.find(
        {"medico.$id": medico_id},
        fetch_links=True
    ).sort("-data_entrada").to_list()

    return [
        InternacaoResponse(
            id=str(i.id),
            data_entrada=i.data_entrada,
            data_saida=i.data_saida,
            quarto=i.quarto,
            motivo=i.motivo,
            observacoes=i.observacoes,
            valor_diaria=i.valor_diaria,
            paciente_id=str(i.paciente.id),
            medico_id=str(i.medico.id),
        )
        for i in internacoes
    ]