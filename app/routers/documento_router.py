import os

from beanie import PydanticObjectId
from bson.errors import InvalidId
from fastapi import (
    APIRouter,
    UploadFile,
    File,
)
from fastapi.responses import FileResponse

from app.models.documento import Documento
from app.models.paciente import Paciente
from app.core.exceptions import (
    EntidadeNaoEncontradaException,
    IdInvalidoException,
    RegraNegocioException,
)

UPLOAD_DIR = "uploads_documentos"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

router = APIRouter(
    tags=["Documentos"]
)

TIPOS_PERMITIDOS = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
]


def _converter_object_id(valor: str, campo: str = "id") -> PydanticObjectId:
    """Converte uma string em PydanticObjectId, levantando exceção tratada se inválida."""
    try:
        return PydanticObjectId(valor)
    except InvalidId:
        raise IdInvalidoException(valor, campo)


@router.post("/pacientes/{paciente_id}/documents")
async def upload_documento(
    paciente_id: str,
    file: UploadFile = File(...)
):
    """Envia um novo documento (PDF ou imagem) para um paciente."""
    if file.content_type not in TIPOS_PERMITIDOS:
        raise RegraNegocioException("Tipo de arquivo não permitido")

    paciente = await Paciente.get(
        _converter_object_id(paciente_id, "paciente_id")
    )

    if not paciente:
        raise EntidadeNaoEncontradaException("Paciente", paciente_id)

    content = await file.read()

    doc = Documento(
        original_filename=file.filename,
        content_type=file.content_type,
        extension=os.path.splitext(file.filename)[1],
        size_bytes=len(content),
        paciente=paciente,
    )

    await doc.insert()

    caminho = os.path.join(
        UPLOAD_DIR,
        f"{doc.id}{doc.extension}"
    )

    with open(caminho, "wb") as f:
        f.write(content)

    return {
        "id": str(doc.id),
        "arquivo": doc.original_filename
    }


@router.get("/pacientes/{paciente_id}/documents")
async def listar_documentos(
    paciente_id: str
):
    """Lista os documentos vinculados a um paciente."""
    paciente_oid = _converter_object_id(paciente_id, "paciente_id")

    paciente = await Paciente.get(paciente_oid)
    if not paciente:
        raise EntidadeNaoEncontradaException("Paciente", paciente_id)

    documentos = await Documento.find(
        Documento.paciente.id == paciente_oid
    ).to_list()

    return [
        {
            "id": str(doc.id),
            "arquivo": doc.original_filename
        }
        for doc in documentos
    ]


@router.get("/documents/{document_id}")
async def obter_documento(
    document_id: str
):
    """Retorna os metadados de um documento."""
    doc = await Documento.get(
        _converter_object_id(document_id, "document_id"),
        fetch_links=True
    )

    if not doc:
        raise EntidadeNaoEncontradaException("Documento", document_id)

    return {
        "id": str(doc.id),
        "original_filename": doc.original_filename,
        "content_type": doc.content_type,
        "extension": doc.extension,
        "size_bytes": doc.size_bytes,
        "paciente_id": str(doc.paciente.id),
    }


@router.get("/documents/{document_id}/download")
async def download_documento(
    document_id: str
):
    """Baixa o arquivo físico associado ao documento."""
    doc = await Documento.get(
        _converter_object_id(document_id, "document_id")
    )

    if not doc:
        raise EntidadeNaoEncontradaException("Documento", document_id)

    caminho = os.path.join(
        UPLOAD_DIR,
        f"{doc.id}{doc.extension}"
    )

    if not os.path.exists(caminho):
        raise EntidadeNaoEncontradaException("Arquivo físico do documento", document_id)

    return FileResponse(
        caminho,
        filename=doc.original_filename
    )


@router.delete("/documents/{document_id}")
async def deletar_documento(
    document_id: str
):
    """Remove um documento e seu arquivo físico."""
    doc = await Documento.get(
        _converter_object_id(document_id, "document_id")
    )

    if not doc:
        raise EntidadeNaoEncontradaException("Documento", document_id)

    caminho = os.path.join(
        UPLOAD_DIR,
        f"{doc.id}{doc.extension}"
    )

    if os.path.exists(caminho):
        os.remove(caminho)

    await doc.delete()

    return {
        "message": "Documento removido com sucesso"
    }