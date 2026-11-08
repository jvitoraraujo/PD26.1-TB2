from beanie import PydanticObjectId
from fastapi import APIRouter
from fastapi_pagination import Page

from app.core.crud import obter_ou_404, paginar
from app.core.exceptions import RegraNegocioException
from app.models.internacao import Internacao
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.schemas.internacao_schema import InternacaoCreate, InternacaoResponse, InternacaoUpdate
from app.schemas.tipos import IdObjeto

router = APIRouter(prefix="/internacoes", tags=["Internações"])


@router.post("/", response_model=InternacaoResponse, status_code=201)
async def criar_internacao(dados: InternacaoCreate):
    paciente = await obter_ou_404(Paciente, dados.paciente_id, "Paciente")
    medico = await obter_ou_404(Medico, dados.medico_id, "Médico")

    internacao = Internacao(
        **dados.model_dump(exclude={"paciente_id", "medico_id"}),
        paciente=paciente,
        medico=medico,
    )
    await internacao.insert()
    return InternacaoResponse.de_documento(internacao)


# Rotas literais ANTES de "/{internacao_id}", senão "/count" seria interpretado como um id
@router.get("/count")
async def contar_internacoes():
    return {"total": await Internacao.count()}


@router.get("/", response_model=Page[InternacaoResponse])
async def listar_internacoes(paciente_id: IdObjeto | None = None):
    filtros = [Internacao.paciente.id == PydanticObjectId(paciente_id)] if paciente_id else []
    return await paginar(Internacao.find(*filtros), InternacaoResponse.de_documento)


@router.get("/{internacao_id}", response_model=InternacaoResponse)
async def buscar_internacao(internacao_id: IdObjeto):
    return InternacaoResponse.de_documento(await obter_ou_404(Internacao, internacao_id, "Internação"))


@router.put("/{internacao_id}", response_model=InternacaoResponse)
async def atualizar_internacao(internacao_id: IdObjeto, dados: InternacaoUpdate):
    internacao = await obter_ou_404(Internacao, internacao_id, "Internação")
    campos = dados.model_dump(exclude_unset=True)

    # data_saida pode ser enviada como null para reabrir a internação; os demais campos são obrigatórios
    if "data_saida" in campos:
        internacao.data_saida = campos.pop("data_saida")
    for campo, valor in campos.items():
        if valor is not None:
            setattr(internacao, campo, valor)

    if internacao.data_saida and internacao.data_saida < internacao.data_entrada:
        raise RegraNegocioException("data_saida não pode ser anterior a data_entrada.")

    await internacao.save()
    return InternacaoResponse.de_documento(internacao)


@router.delete("/{internacao_id}")
async def deletar_internacao(internacao_id: IdObjeto):
    internacao = await obter_ou_404(Internacao, internacao_id, "Internação")
    await internacao.delete()
    return {"message": "Internação removida com sucesso"}
