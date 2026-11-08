import re

from beanie import PydanticObjectId
from beanie.operators import RegEx
from fastapi import APIRouter
from fastapi_pagination import Page

from app.core.crud import obter_ou_404, paginar
from app.core.exceptions import EntidadeNaoEncontradaException, RegraNegocioException
from app.models.consulta import Consulta
from app.models.especialidade import Especialidade
from app.models.internacao import Internacao
from app.models.medico import Medico
from app.schemas.medico_schema import MedicoCreate, MedicoResponse
from app.schemas.tipos import IdObjeto, Uf

router = APIRouter(prefix="/medicos", tags=["Médicos"])


async def _resolver_especialidades(ids: list[str]) -> list[Especialidade]:
    """Busca todas as especialidades em uma única consulta; 404 se alguma não existir."""
    oids = [PydanticObjectId(i) for i in dict.fromkeys(ids)]
    encontradas = {e.id: e for e in await Especialidade.find({"_id": {"$in": oids}}).to_list()}
    ausentes = [str(o) for o in oids if o not in encontradas]
    if ausentes:
        raise EntidadeNaoEncontradaException("Especialidade", ", ".join(ausentes))
    return [encontradas[o] for o in oids]


@router.get("/count")
async def contar_medicos():
    return {"total_medicos": await Medico.count()}


@router.get("/estatisticas/count", deprecated=True)
async def contar_medicos_legado():
    """Rota antiga; use GET /medicos/count."""
    return await contar_medicos()


@router.get("/", response_model=Page[MedicoResponse])
async def listar_medicos(
    cidade: str | None = None,
    uf: Uf | None = None,
    especialidade_id: IdObjeto | None = None,
    ativo: bool | None = None,
):
    filtros = []
    if cidade:
        filtros.append(RegEx(Medico.cidade, f"^{re.escape(cidade)}$", "i"))
    if uf:
        filtros.append(Medico.uf == uf)
    if especialidade_id:
        filtros.append(Medico.especialidades.id == PydanticObjectId(especialidade_id))
    if ativo is not None:
        filtros.append(Medico.ativo == ativo)

    # fetch_links é necessário aqui apenas para devolver os nomes das especialidades
    return await paginar(Medico.find(*filtros, fetch_links=True), MedicoResponse.de_documento)


@router.get("/{medico_id}", response_model=MedicoResponse)
async def obter_medico(medico_id: IdObjeto):
    medico = await Medico.get(PydanticObjectId(medico_id), fetch_links=True)
    if medico is None:
        raise EntidadeNaoEncontradaException("Médico", medico_id)
    return MedicoResponse.de_documento(medico)


@router.post("/", response_model=MedicoResponse, status_code=201)
async def criar_medico(dados: MedicoCreate):
    campos = dados.model_dump(exclude={"especialidades"})
    novo = Medico(**campos, especialidades=await _resolver_especialidades(dados.especialidades))
    await novo.insert()
    return MedicoResponse.de_documento(novo)


@router.put("/{medico_id}", response_model=MedicoResponse)
async def atualizar_medico(medico_id: IdObjeto, dados: MedicoCreate):
    medico = await obter_ou_404(Medico, medico_id, "Médico")
    for campo, valor in dados.model_dump(exclude={"especialidades"}).items():
        setattr(medico, campo, valor)
    medico.especialidades = await _resolver_especialidades(dados.especialidades)
    await medico.save()
    return MedicoResponse.de_documento(medico)


@router.delete("/{medico_id}")
async def deletar_medico(medico_id: IdObjeto):
    medico = await obter_ou_404(Medico, medico_id, "Médico")
    if await Consulta.find(Consulta.medico.id == medico.id).count() or await Internacao.find(
        Internacao.medico.id == medico.id
    ).count():
        raise RegraNegocioException("Médico possui consultas ou internações vinculadas.")
    await medico.delete()
    return {"message": "Médico removido com sucesso"}
