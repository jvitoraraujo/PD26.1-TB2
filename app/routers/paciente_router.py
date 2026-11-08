from fastapi import APIRouter
from fastapi_pagination import Page

from app.core.crud import obter_ou_404, paginar
from app.core.exceptions import RegraNegocioException
from app.models.consulta import Consulta
from app.models.internacao import Internacao
from app.models.paciente import Paciente
from app.routers.documento_router import remover_documentos_do_paciente
from app.schemas.paciente_schema import PacienteCreate, PacienteResponse, PacienteUpdate
from app.schemas.tipos import IdObjeto

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.post("/", response_model=PacienteResponse, status_code=201)
async def criar_paciente(dados: PacienteCreate):
    novo = Paciente(**dados.model_dump())
    await novo.insert()
    return PacienteResponse.de_documento(novo)


@router.get("/count")
async def contar_pacientes():
    return {"total": await Paciente.count()}


@router.get("/", response_model=Page[PacienteResponse])
async def listar_pacientes():
    return await paginar(Paciente.find(), PacienteResponse.de_documento)


@router.get("/{paciente_id}", response_model=PacienteResponse)
async def buscar_paciente(paciente_id: IdObjeto):
    return PacienteResponse.de_documento(await obter_ou_404(Paciente, paciente_id, "Paciente"))


@router.put("/{paciente_id}", response_model=PacienteResponse)
async def atualizar_paciente(paciente_id: IdObjeto, dados: PacienteUpdate):
    paciente = await obter_ou_404(Paciente, paciente_id, "Paciente")
    # campos nulos são ignorados: os campos do paciente são obrigatórios
    for campo, valor in dados.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(paciente, campo, valor)
    await paciente.save()
    return PacienteResponse.de_documento(paciente)


@router.delete("/{paciente_id}")
async def deletar_paciente(paciente_id: IdObjeto):
    paciente = await obter_ou_404(Paciente, paciente_id, "Paciente")
    if await Consulta.find(Consulta.paciente.id == paciente.id).count() or await Internacao.find(
        Internacao.paciente.id == paciente.id
    ).count():
        raise RegraNegocioException("Paciente possui consultas ou internações vinculadas.")
    await remover_documentos_do_paciente(paciente.id)
    await paciente.delete()
    return {"message": "Paciente removido com sucesso"}
