from fastapi import APIRouter, HTTPException, status, Query, Depends
from app.schemas.medico_schema import MedicoResponse, MedicoCreate
from app.repositories.hospital_repository import HospitalRepository

router = APIRouter(prefix="/medicos", tags=["Médicos"])

# Dependência para instanciar e injetar o repositório
def get_medico_repo() -> HospitalRepository:
    # Utiliza o MedicoResponse pois o repositório espera um modelo que contenha 'id'
    return HospitalRepository(model=MedicoResponse, caminho="dados/delta_medicos")

@router.get("/count")
def contar_medicos(repo: HospitalRepository = Depends(get_medico_repo)):
    total = repo.count()
    return {"total": total}

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MedicoResponse)
def criar_medico(medico_in: MedicoCreate, repo: HospitalRepository = Depends(get_medico_repo)):
    # Verificação de CRM duplicado utilizando o método otimizado do repositório
    if repo.existe_por_crm(medico_in.crm):
        raise HTTPException(status_code=400, detail=f"Já existe um médico com o CRM {medico_in.crm}")
    
    # Prepara o objeto para o repositório (precisa de ser do tipo 'T' que inclui id)
    dados = medico_in.model_dump()
    dados["id"] = 0 # O ID real será gerado pelo autoincremento (_proximo_id) do repositório
    novo_medico = MedicoResponse(**dados)
    
    return repo.insert(novo_medico)

# NOVA ROTA: Criada para expor a listagem paginada explicitamente
@router.get("/", response_model=list[MedicoResponse])
def listar_medicos(
    pagina: int = Query(1, ge=1, description="Número da página"),
    tamanho: int = Query(10, ge=1, le=100, description="Quantidade de registos por página"),
    repo: HospitalRepository = Depends(get_medico_repo)
):
    return repo.listar(pagina=pagina, tamanho=tamanho)

@router.get("/{id}", response_model=MedicoResponse)
def buscar_por_id(id: int, repo: HospitalRepository = Depends(get_medico_repo)):
    medico = repo.get(id)
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    return medico

@router.get("/busca/avancada", response_model=list[MedicoResponse])
def buscar_medicos_avancado(
    especialidade: str | None = Query(None),
    cidade: str | None = Query(None),
    uf: str | None = Query(None),
    ativo: bool | None = Query(None),
    repo: HospitalRepository = Depends(get_medico_repo)
):
    return repo.buscar_por_filtros(
        especialidade=especialidade, 
        cidade=cidade, 
        uf=uf, 
        ativo=ativo
    )

@router.put("/{id}", response_model=MedicoResponse)
def atualizar_medico(id: int, dados: MedicoCreate, repo: HospitalRepository = Depends(get_medico_repo)):
    medico_existente = repo.get(id)
    if not medico_existente:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Junta os novos dados com o ID existente
    dados_atualizados = dados.model_dump()
    dados_atualizados["id"] = id
    medico_atualizado = MedicoResponse(**dados_atualizados)
    
    resultado = repo.update(id, medico_atualizado)
    if not resultado:
        raise HTTPException(status_code=400, detail="Erro ao atualizar médico")
        
    return resultado

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_medico(id: int, repo: HospitalRepository = Depends(get_medico_repo)):
    sucesso = repo.delete(id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Médico não encontrado")