from beanie import PydanticObjectId
from fastapi import APIRouter
from fastapi_pagination import Page

from app.core.crud import obter_ou_404, paginar
from app.models.consulta import Consulta
from app.models.exame import Exame
from app.schemas.exame_schema import ExameCreate, ExameResponse, ExameUpdate
from app.schemas.tipos import IdObjeto

router = APIRouter(prefix="/exames", tags=["Exames"])


@router.post("/", response_model=ExameResponse, status_code=201)
async def criar_exame(dados: ExameCreate):
    consulta = await obter_ou_404(Consulta, dados.consulta_id, "Consulta")
    novo = Exame(tipo=dados.tipo, resultado=dados.resultado, consulta=consulta)
    await novo.insert()
    return ExameResponse.de_documento(novo)


@router.get("/count")
async def contar_exames():
    return {"total": await Exame.count()}


@router.get("/", response_model=Page[ExameResponse])
async def listar_exames(consulta_id: IdObjeto | None = None):
    filtros = [Exame.consulta.id == PydanticObjectId(consulta_id)] if consulta_id else []
    return await paginar(Exame.find(*filtros), ExameResponse.de_documento)


@router.get("/{exame_id}", response_model=ExameResponse)
async def buscar_exame(exame_id: IdObjeto):
    return ExameResponse.de_documento(await obter_ou_404(Exame, exame_id, "Exame"))


@router.put("/{exame_id}", response_model=ExameResponse)
async def atualizar_exame(exame_id: IdObjeto, dados: ExameUpdate):
    exame = await obter_ou_404(Exame, exame_id, "Exame")
    for campo, valor in dados.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(exame, campo, valor)
    await exame.save()
    return ExameResponse.de_documento(exame)


@router.delete("/{exame_id}")
async def deletar_exame(exame_id: IdObjeto):
    exame = await obter_ou_404(Exame, exame_id, "Exame")
    await exame.delete()
    return {"message": "Exame removido com sucesso"}
