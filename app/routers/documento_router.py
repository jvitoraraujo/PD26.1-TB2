from pathlib import Path

from beanie import PydanticObjectId
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse
from fastapi_pagination import Page

from app.core.arquivos import TIPOS_PERMITIDOS
from app.core.armazenamento import caminho_documento, remover_arquivo, salvar_upload
from app.core.crud import obter_ou_404, paginar
from app.core.exceptions import EntidadeNaoEncontradaException, RegraNegocioException
from app.models.documento import Documento
from app.models.paciente import Paciente
from app.schemas.documento_schema import DocumentResponse
from app.schemas.tipos import IdObjeto

router = APIRouter(tags=["Documentos"])


async def remover_documentos_do_paciente(paciente_id: PydanticObjectId) -> None:
    """Remove documentos (registros e arquivos) de um paciente."""
    for doc in await Documento.find(Documento.paciente.id == paciente_id).to_list():
        await doc.delete()
        remover_arquivo(caminho_documento(doc.id, doc.extension))


@router.post("/pacientes/{paciente_id}/documents", response_model=DocumentResponse, status_code=201)
async def upload_documento(paciente_id: IdObjeto, file: UploadFile = File(...)):
    if file.content_type not in TIPOS_PERMITIDOS:
        raise RegraNegocioException(
            f"Tipo de arquivo não permitido. Aceitos: {', '.join(TIPOS_PERMITIDOS)}."
        )
    paciente = await obter_ou_404(Paciente, paciente_id, "Paciente")

    temporario, tamanho = await salvar_upload(file, tipo_esperado=file.content_type)
    extensao = TIPOS_PERMITIDOS[file.content_type]  # nunca derivada do nome enviado pelo cliente
    doc = Documento(
        original_filename=(Path(file.filename or "arquivo").name or "arquivo")[:255],
        content_type=file.content_type,
        extension=extensao,
        size_bytes=tamanho,
        paciente=paciente,
    )
    try:
        await doc.insert()
        temporario.replace(caminho_documento(doc.id, extensao))
    except BaseException:
        remover_arquivo(temporario)
        if doc.id is not None:
            await doc.delete()
        raise
    return DocumentResponse.de_documento(doc)


@router.get("/pacientes/{paciente_id}/documents", response_model=Page[DocumentResponse])
async def listar_documentos(paciente_id: IdObjeto):
    paciente = await obter_ou_404(Paciente, paciente_id, "Paciente")
    return await paginar(Documento.find(Documento.paciente.id == paciente.id), DocumentResponse.de_documento)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def obter_documento(document_id: IdObjeto):
    return DocumentResponse.de_documento(await obter_ou_404(Documento, document_id, "Documento"))


@router.get("/documents/{document_id}/download")
async def download_documento(document_id: IdObjeto):
    doc = await obter_ou_404(Documento, document_id, "Documento")
    caminho = caminho_documento(doc.id, doc.extension)
    if not caminho.exists():
        raise EntidadeNaoEncontradaException("Arquivo do documento", document_id)
    return FileResponse(
        caminho,
        media_type=doc.content_type,
        filename=doc.original_filename,
        headers={"X-Content-Type-Options": "nosniff"},
    )


@router.delete("/documents/{document_id}")
async def deletar_documento(document_id: IdObjeto):
    doc = await obter_ou_404(Documento, document_id, "Documento")
    await doc.delete()
    remover_arquivo(caminho_documento(doc.id, doc.extension))
    return {"message": "Documento removido com sucesso"}
