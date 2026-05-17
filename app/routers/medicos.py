from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.db.database import get_db
from app.models.medico import Medico
from app.schemas import medico_schema

router = APIRouter(prefix="/medicos", tags=["Médicos"])


# ---------------------------------------------------------
# ROTAS ESTÁTICAS (Devem vir antes do /{medico_id})
# ---------------------------------------------------------

@router.get("/estatisticas/count", response_model=dict)
async def contar_medicos(db: AsyncSession = Depends(get_db)):
    """
    Retorna o número total de médicos cadastrados no sistema.
    """
    # Utiliza a função count do SQLAlchemy de forma otimizada
    resultado = await db.execute(select(func.count(Medico.id)))
    total = resultado.scalar()
    
    return {"total_medicos": total}


@router.get("/buscar/filtros", response_model=Page[medico_schema.MedicoResponse])
async def buscar_medicos_por_filtro(
    especialidade: Optional[str] = None,
    cidade: Optional[str] = None,
    uf: Optional[str] = None,
    ativo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca avançada de médicos utilizando filtros opcionais.
    """
    query = select(Medico)
    
    # Adição condicional de filtros (cláusulas WHERE)
    if especialidade:
        query = query.where(Medico.especialidade.ilike(f"%{especialidade}%"))
    if cidade:
        query = query.where(Medico.cidade.ilike(f"%{cidade}%"))
    if uf:
        query = query.where(Medico.uf.ilike(f"%{uf}%"))
    if ativo is not None:
        query = query.where(Medico.ativo == ativo)
        
    query = query.order_by(Medico.nome)
    
    return await paginate(db, query)


@router.get("/", response_model=Page[medico_schema.MedicoResponse])
async def listar_medicos(db: AsyncSession = Depends(get_db)):
    """
    Lista todos os médicos cadastrados com paginação.
    """
    query = select(Medico).order_by(Medico.nome)
    return await paginate(db, query)


@router.post("/", response_model=medico_schema.MedicoResponse, status_code=status.HTTP_201_CREATED)
async def criar_medico(medico_input: medico_schema.MedicoCreate, db: AsyncSession = Depends(get_db)):
    """
    Cadastra um novo médico.
    """
    novo_medico = Medico(**medico_input.model_dump())
    db.add(novo_medico)
    await db.commit()
    await db.refresh(novo_medico)
    return novo_medico


# ---------------------------------------------------------
# ROTAS DINÂMICAS (Com /{medico_id} na URL)
# ---------------------------------------------------------

@router.get("/{medico_id}", response_model=medico_schema.MedicoResponse)
async def obter_medico(medico_id: int, db: AsyncSession = Depends(get_db)):
    """
    Busca um médico específico pelo seu ID.
    """
    result = await db.execute(select(Medico).where(Medico.id == medico_id))
    medico = result.scalar_one_or_none()
    
    if not medico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico não encontrado")
    return medico


@router.put("/{medico_id}", response_model=medico_schema.MedicoResponse)
async def atualizar_medico(
    medico_id: int, 
    medico_input: medico_schema.MedicoCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza integralmente os dados de um médico existente pelo ID.
    """
    result = await db.execute(select(Medico).where(Medico.id == medico_id))
    medico = result.scalar_one_or_none()
    
    if not medico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico não encontrado")
    
    # Atualiza os atributos do objeto SQLAlchemy com os novos dados
    for key, value in medico_input.model_dump().items():
        setattr(medico, key, value)
        
    await db.commit()
    await db.refresh(medico)
    return medico


@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_medico(medico_id: int, db: AsyncSession = Depends(get_db)):
    """
    Remove um médico do banco de dados pelo ID.
    """
    result = await db.execute(select(Medico).where(Medico.id == medico_id))
    medico = result.scalar_one_or_none()
    
    if not medico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Médico não encontrado")
        
    await db.delete(medico)
    await db.commit()
    return None