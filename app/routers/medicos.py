from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.models.medico import Medico as MedicoModel
from app.schemas.medico_schema import MedicoResponse, MedicoCreate
from app.db.database import get_db

router = APIRouter(prefix="/medicos", tags=["Médicos"])

@router.get("/count")
async def contar_medicos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count()).select_from(MedicoModel))
    total = result.scalar()
    return {"total": total}

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MedicoResponse)
async def criar_medico(medico_in: MedicoCreate, db: AsyncSession = Depends(get_db)):
    # Verificação de CRM duplicado
    query_crm = await db.execute(select(MedicoModel).where(MedicoModel.crm == medico_in.crm))
    if query_crm.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Já existe um médico com o CRM {medico_in.crm}")
    
    novo_medico = MedicoModel(**medico_in.model_dump())
    db.add(novo_medico)
    await db.commit()
    await db.refresh(novo_medico)
    return novo_medico

@router.get("/{id}", response_model=MedicoResponse)
async def buscar_por_id(id: int, db: AsyncSession = Depends(get_db)):
    medico = await db.get(MedicoModel, id)
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    return medico

@router.get("/busca/avancada", response_model=Page[MedicoResponse])
async def buscar_medicos_avancado(
    especialidade: str | None = Query(None),
    cidade: str | None = Query(None),
    uf: str | None = Query(None),
    ativo: bool | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(MedicoModel)
    if especialidade:
        query = query.where(MedicoModel.especialidade.ilike(f"%{especialidade}%"))
    if cidade:
        query = query.where(MedicoModel.cidade.ilike(f"%{cidade}%"))
    if uf:
        query = query.where(MedicoModel.uf.ilike(uf))
    if ativo is not None:
        query = query.where(MedicoModel.ativo == ativo)
        
    return await paginate(db, query)

@router.put("/{id}", response_model=MedicoResponse)
async def atualizar_medico(id: int, dados: MedicoCreate, db: AsyncSession = Depends(get_db)):
    medico = await db.get(MedicoModel, id)
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    for key, value in dados.model_dump().items():
        setattr(medico, key, value)
        
    await db.commit()
    await db.refresh(medico)
    return medico

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_medico(id: int, db: AsyncSession = Depends(get_db)):
    medico = await db.get(MedicoModel, id)
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    await db.delete(medico)
    await db.commit()