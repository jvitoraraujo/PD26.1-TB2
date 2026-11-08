import re
from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import RegEx
from fastapi import APIRouter
from fastapi_pagination import Page

from app.core.crud import obter_ou_404, paginar
from app.core.exceptions import RegraNegocioException
from app.core.validadores import como_utc
from app.models.consulta import Consulta
from app.models.exame import Exame
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.schemas.consulta_schema import ConsultaCreate, ConsultaResponse, ConsultaUpdate
from app.schemas.tipos import IdObjeto

router = APIRouter(prefix="/consultas", tags=["Consultas"])


@router.post("/", response_model=ConsultaResponse, status_code=201)
async def criar_consulta(dados: ConsultaCreate):
    paciente = await obter_ou_404(Paciente, dados.paciente_id, "Paciente")
    medico = await obter_ou_404(Medico, dados.medico_id, "Médico")

    extras = {"data_consulta": dados.data_consulta} if dados.data_consulta else {}
    consulta = Consulta(diagnostico=dados.diagnostico, paciente=paciente, medico=medico, **extras)
    await consulta.insert()
    return ConsultaResponse.de_documento(consulta)


# Rotas literais ANTES de "/{consulta_id}", senão "/count" seria interpretado como um id
@router.get("/count")
async def contar_consultas():
    return {"total": await Consulta.count()}


@router.get("/", response_model=Page[ConsultaResponse])
async def listar_consultas(
    paciente_id: IdObjeto | None = None,
    medico_id: IdObjeto | None = None,
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
    diagnostico: str | None = None,
):
    filtros = []
    if paciente_id:
        filtros.append(Consulta.paciente.id == PydanticObjectId(paciente_id))
    if medico_id:
        filtros.append(Consulta.medico.id == PydanticObjectId(medico_id))
    if data_inicio:
        filtros.append(Consulta.data_consulta >= como_utc(data_inicio))
    if data_fim:
        filtros.append(Consulta.data_consulta <= como_utc(data_fim))
    if diagnostico:
        filtros.append(RegEx(Consulta.diagnostico, re.escape(diagnostico), "i"))

    return await paginar(Consulta.find(*filtros), ConsultaResponse.de_documento)


@router.get("/{consulta_id}", response_model=ConsultaResponse)
async def buscar_consulta(consulta_id: IdObjeto):
    return ConsultaResponse.de_documento(await obter_ou_404(Consulta, consulta_id, "Consulta"))


@router.put("/{consulta_id}", response_model=ConsultaResponse)
async def atualizar_consulta(consulta_id: IdObjeto, dados: ConsultaUpdate):
    consulta = await obter_ou_404(Consulta, consulta_id, "Consulta")
    campos = dados.model_dump(exclude_unset=True)

    if campos.get("paciente_id"):
        consulta.paciente = await obter_ou_404(Paciente, campos["paciente_id"], "Paciente")
    if campos.get("medico_id"):
        consulta.medico = await obter_ou_404(Medico, campos["medico_id"], "Médico")
    if campos.get("data_consulta"):
        consulta.data_consulta = campos["data_consulta"]
    if "diagnostico" in campos:  # permite limpar o diagnóstico enviando null
        consulta.diagnostico = campos["diagnostico"]

    await consulta.save()
    return ConsultaResponse.de_documento(consulta)


@router.delete("/{consulta_id}")
async def deletar_consulta(consulta_id: IdObjeto):
    consulta = await obter_ou_404(Consulta, consulta_id, "Consulta")
    if await Exame.find(Exame.consulta.id == consulta.id).count():
        raise RegraNegocioException("Consulta possui exames vinculados.")
    await consulta.delete()
    return {"message": "Consulta removida com sucesso"}
