from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException

from app.models.internacao import Internacao
from app.models.medico import Medico
from app.models.paciente import Paciente

router = APIRouter(
    prefix="/internacoes",
    tags=["Internações"]
)


@router.post("/")
async def criar_internacao(
    dados: dict
):

    paciente = await Paciente.get(
        PydanticObjectId(dados["paciente_id"])
    )

    if not paciente:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado"
        )

    medico = await Medico.get(
        PydanticObjectId(dados["medico_id"])
    )

    if not medico:
        raise HTTPException(
            status_code=404,
            detail="Médico não encontrado"
        )

    internacao = Internacao(
        data_entrada=dados["data_entrada"],
        data_saida=dados.get("data_saida"),
        quarto=dados["quarto"],
        motivo=dados["motivo"],
        observacoes=dados.get("observacoes"),
        valor_diaria=dados["valor_diaria"],
        paciente=paciente,
        medico=medico,
    )

    await internacao.insert()

    return {
        "id": str(internacao.id),
        "message": "Internação criada com sucesso"
    }


@router.get("/")
async def listar_internacoes():

    internacoes = await Internacao.find_all(
        fetch_links=True
    ).to_list()

    resultado = []

    for item in internacoes:

        resultado.append(
            {
                "id": str(item.id),
                "data_entrada": item.data_entrada,
                "data_saida": item.data_saida,
                "quarto": item.quarto,
                "motivo": item.motivo,
                "observacoes": item.observacoes,
                "valor_diaria": item.valor_diaria,
                "paciente_id": str(item.paciente.id),
                "medico_id": str(item.medico.id),
            }
        )

    return resultado


@router.get("/{internacao_id}")
async def buscar_internacao(
    internacao_id: str
):

    internacao = await Internacao.get(
        PydanticObjectId(internacao_id),
        fetch_links=True
    )

    if not internacao:
        raise HTTPException(
            status_code=404,
            detail="Internação não encontrada"
        )

    return {
        "id": str(internacao.id),
        "data_entrada": internacao.data_entrada,
        "data_saida": internacao.data_saida,
        "quarto": internacao.quarto,
        "motivo": internacao.motivo,
        "observacoes": internacao.observacoes,
        "valor_diaria": internacao.valor_diaria,
        "paciente_id": str(internacao.paciente.id),
        "medico_id": str(internacao.medico.id),
    }


@router.put("/{internacao_id}")
async def atualizar_internacao(
    internacao_id: str,
    dados: dict
):

    internacao = await Internacao.get(
        PydanticObjectId(internacao_id),
        fetch_links=True
    )

    if not internacao:
        raise HTTPException(
            status_code=404,
            detail="Internação não encontrada"
        )

    if "quarto" in dados:
        internacao.quarto = dados["quarto"]

    if "motivo" in dados:
        internacao.motivo = dados["motivo"]

    if "observacoes" in dados:
        internacao.observacoes = dados["observacoes"]

    if "valor_diaria" in dados:
        internacao.valor_diaria = dados["valor_diaria"]

    await internacao.save()

    return {
        "message": "Internação atualizada com sucesso"
    }


@router.delete("/{internacao_id}")
async def deletar_internacao(
    internacao_id: str
):

    internacao = await Internacao.get(
        PydanticObjectId(internacao_id)
    )

    if not internacao:
        raise HTTPException(
            status_code=404,
            detail="Internação não encontrada"
        )

    await internacao.delete()

    return {
        "message": "Internação removida com sucesso"
    }


@router.get("/count")
async def contar_internacoes():

    total = await Internacao.count()

    return {
        "total": total
    }