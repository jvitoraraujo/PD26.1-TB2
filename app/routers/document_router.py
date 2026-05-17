import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models.document import Document
from app.models.paciente import Paciente
from app.schemas.document_schema import DocumentResponse
from app.core.exceptions import EntidadeNaoEncontradaException, RegraNegocioException

# Define a pasta base para uploads
UPLOAD_DIR = "uploads_documentos"

# Cria a pasta caso não exista
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(tags=["Documentos"])

# TIPOS PERMITIDOS (Imagens e PDF)
TIPOS_PERMITIDOS = ["application/pdf", "image/jpeg", "image/png", "image/webp"]

@router.post("/pacientes/{paciente_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_documento(paciente_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    # 1. Verifica extensão e mime type
    if file.content_type not in TIPOS_PERMITIDOS:
        raise RegraNegocioException(f"Tipo de arquivo não suportado. Apenas PDF e imagens são permitidos.")

    # 2. Verifica se o paciente existe
    result_paciente = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
    if not result_paciente.scalar_one_or_none():
        raise EntidadeNaoEncontradaException("Paciente", paciente_id)

    # 3. Lê o conteúdo e tamanho
    content = await file.read()
    size_bytes = len(content)
    
    # Extrai metadados
    original_filename = file.filename
    extension = os.path.splitext(original_filename)[1]

    # 4. Salva metadados no banco de dados primeiro para obter o ID
    doc = Document(
        original_filename=original_filename,
        content_type=file.content_type,
        extension=extension,
        size_bytes=size_bytes,
        paciente_id=paciente_id
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # 5. Salva arquivo fisicamente usando o ID gerado + extensão
    file_path = os.path.join(UPLOAD_DIR, f"{doc.id}{doc.extension}")
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    return doc

@router.get("/pacientes/{paciente_id}/documents", response_model=list[DocumentResponse])
async def listar_documentos_paciente(paciente_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.paciente_id == paciente_id))
    return result.scalars().all()

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def obter_metadados_documento(document_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise EntidadeNaoEncontradaException("Document", document_id)
    return doc

@router.get("/documents/{document_id}/download")
async def download_documento(document_id: int, db: AsyncSession = Depends(get_db)):
    # Busca metadados
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise EntidadeNaoEncontradaException("Document", document_id)
    
    # Caminho físico
    file_path = os.path.join(UPLOAD_DIR, f"{doc.id}{doc.extension}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="O arquivo físico não foi encontrado no servidor.")
    
    # Retorna como arquivo
    return FileResponse(path=file_path, media_type=doc.content_type, filename=doc.original_filename)

@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def substituir_documento(document_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if file.content_type not in TIPOS_PERMITIDOS:
        raise RegraNegocioException(f"Tipo de arquivo não suportado.")

    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise EntidadeNaoEncontradaException("Document", document_id)

    # Deleta arquivo físico antigo
    old_file_path = os.path.join(UPLOAD_DIR, f"{doc.id}{doc.extension}")
    if os.path.exists(old_file_path):
        os.remove(old_file_path)

    # Atualiza metadados
    content = await file.read()
    doc.original_filename = file.filename
    doc.extension = os.path.splitext(file.filename)[1]
    doc.content_type = file.content_type
    doc.size_bytes = len(content)

    await db.commit()
    await db.refresh(doc)

    # Salva o novo arquivo
    new_file_path = os.path.join(UPLOAD_DIR, f"{doc.id}{doc.extension}")
    with open(new_file_path, "wb") as buffer:
        buffer.write(content)

    return doc

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_documento(document_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise EntidadeNaoEncontradaException("Document", document_id)

    # Deleta arquivo físico
    file_path = os.path.join(UPLOAD_DIR, f"{doc.id}{doc.extension}")
    if os.path.exists(file_path):
        os.remove(file_path)

    # Deleta metadados
    await db.delete(doc)
    await db.commit()
    return None