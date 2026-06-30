import os
import io
from beanie import PydanticObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse

from app.models.documento import Documento
from app.models.paciente import Paciente
from app.core.config import minio_client, settings
from app.core.exceptions import (
    EntidadeNaoEncontradaException,
    IdInvalidoException,
    RegraNegocioException,
)

router = APIRouter(tags=["Documentos"])

TIPOS_PERMITIDOS = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
]

def _converter_object_id(valor: str, campo: str = "id") -> PydanticObjectId:
    try:
        return PydanticObjectId(valor)
    except InvalidId:
        raise IdInvalidoException(valor, campo)

@router.post("/pacientes/{paciente_id}/documents")
async def upload_documento(paciente_id: str, file: UploadFile = File(...)):
    if file.content_type not in TIPOS_PERMITIDOS:
        raise RegraNegocioException("Tipo de arquivo não permitido")

    paciente = await Paciente.get(_converter_object_id(paciente_id, "paciente_id"))
    if not paciente:
        raise EntidadeNaoEncontradaException("Paciente", paciente_id)

    content = await file.read()
    file_size = len(content)

    doc = Documento(
        original_filename=file.filename,
        content_type=file.content_type,
        extension=os.path.splitext(file.filename)[1],
        size_bytes=file_size,
        paciente=paciente,
    )
    await doc.insert()

    # Upload para o MinIO usando o ID do documento como nome do objeto
    object_name = f"{doc.id}{doc.extension}"
    minio_client.put_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=object_name,
        data=io.BytesIO(content),
        length=file_size,
        content_type=file.content_type
    )

    return {"id": str(doc.id), "arquivo": doc.original_filename}

@router.put("/documents/{document_id}")
async def atualizar_documento(document_id: str, file: UploadFile = File(...)):
    """Atualiza o arquivo físico de um documento existente."""
    if file.content_type not in TIPOS_PERMITIDOS:
        raise RegraNegocioException("Tipo de arquivo não permitido")

    doc = await Documento.get(_converter_object_id(document_id, "document_id"))
    if not doc:
        raise EntidadeNaoEncontradaException("Documento", document_id)

    # Remove o arquivo antigo do MinIO
    old_object_name = f"{doc.id}{doc.extension}"
    minio_client.remove_object(settings.MINIO_BUCKET, old_object_name)

    content = await file.read()
    file_size = len(content)
    new_extension = os.path.splitext(file.filename)[1]

    # Atualiza metadados
    doc.original_filename = file.filename
    doc.content_type = file.content_type
    doc.extension = new_extension
    doc.size_bytes = file_size
    await doc.save()

    # Upload novo arquivo
    new_object_name = f"{doc.id}{doc.extension}"
    minio_client.put_object(
        bucket_name=settings.MINIO_BUCKET,
        object_name=new_object_name,
        data=io.BytesIO(content),
        length=file_size,
        content_type=file.content_type
    )

    return {"message": "Documento atualizado com sucesso", "id": str(doc.id)}

@router.get("/documents/{document_id}/download")
async def download_documento(document_id: str):
    doc = await Documento.get(_converter_object_id(document_id, "document_id"))
    if not doc:
        raise EntidadeNaoEncontradaException("Documento", document_id)

    object_name = f"{doc.id}{doc.extension}"
    
    try:
        response = minio_client.get_object(settings.MINIO_BUCKET, object_name)
    except Exception as e:
        raise EntidadeNaoEncontradaException("Arquivo no Storage", document_id)

    return StreamingResponse(
        response.stream(32 * 1024), 
        media_type=doc.content_type,
        headers={"Content-Disposition": f"attachment; filename={doc.original_filename}"}
    )

@router.delete("/documents/{document_id}")
async def deletar_documento(document_id: str):
    doc = await Documento.get(_converter_object_id(document_id, "document_id"))
    if not doc:
        raise EntidadeNaoEncontradaException("Documento", document_id)

    object_name = f"{doc.id}{doc.extension}"
    
    # Remove do MinIO e do Banco
    try:
        minio_client.remove_object(settings.MINIO_BUCKET, object_name)
    except Exception:
        pass # Ignora erro se o arquivo já não existir fisicamente

    await doc.delete()
    return {"message": "Documento removido com sucesso"}