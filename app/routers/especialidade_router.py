from fastapi import APIRouter
from fastapi_pagination import Page

from app.core.crud import obter_ou_404, paginar
from app.core.exceptions import RegraNegocioException
from app.models.especialidade import Especialidade
from app.models.medico import Medico
from app.schemas.especialidade_schema import EspecialidadeCreate, EspecialidadeResponse
from app.schemas.tipos import IdObjeto

router = APIRouter(prefix="/especialidades", tags=["Especialidades"])


@router.post("/", response_model=EspecialidadeResponse, status_code=201)
async def criar_especialidade(dados: EspecialidadeCreate):
    nova = Especialidade(nome=dados.nome)
    await nova.insert()
    return EspecialidadeResponse.de_documento(nova)


@router.get("/", response_model=Page[EspecialidadeResponse])
async def listar_especialidades():
    return await paginar(Especialidade.find(), EspecialidadeResponse.de_documento)


@router.get("/{especialidade_id}", response_model=EspecialidadeResponse)
async def buscar_especialidade(especialidade_id: IdObjeto):
    return EspecialidadeResponse.de_documento(
        await obter_ou_404(Especialidade, especialidade_id, "Especialidade")
    )


@router.put("/{especialidade_id}", response_model=EspecialidadeResponse)
async def atualizar_especialidade(especialidade_id: IdObjeto, dados: EspecialidadeCreate):
    esp = await obter_ou_404(Especialidade, especialidade_id, "Especialidade")
    esp.nome = dados.nome
    await esp.save()
    return EspecialidadeResponse.de_documento(esp)


@router.delete("/{especialidade_id}")
async def deletar_especialidade(especialidade_id: IdObjeto):
    esp = await obter_ou_404(Especialidade, especialidade_id, "Especialidade")
    if await Medico.find(Medico.especialidades.id == esp.id).count():
        raise RegraNegocioException("Especialidade está vinculada a médicos.")
    await esp.delete()
    return {"message": "Especialidade removida com sucesso"}
