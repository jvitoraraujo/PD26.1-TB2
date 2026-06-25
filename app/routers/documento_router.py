import os

from beanie import PydanticObjectId
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)
from fastapi.responses import FileResponse

from app.models.documento import Documento
from app.models.paciente import Paciente

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


@router.post("/pacientes/{paciente_id}/documents")
async def upload_documento(
    paciente_id: str,
    file: UploadFile = File(...)
):

    if file.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail="Tipo de arquivo não permitido"
        )

    paciente = await Paciente.get(
        PydanticObjectId(paciente_id)
    )

    if not paciente:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado"
        )

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

    documentos = await Documento.find(
        Documento.paciente.id ==
        PydanticObjectId(paciente_id)
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

    doc = await Documento.get(
        PydanticObjectId(document_id),
        fetch_links=True
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

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

    doc = await Documento.get(
        PydanticObjectId(document_id)
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    caminho = os.path.join(
        UPLOAD_DIR,
        f"{doc.id}{doc.extension}"
    )

    if not os.path.exists(caminho):
        raise HTTPException(
            status_code=404,
            detail="Arquivo não encontrado"
        )

    return FileResponse(
        caminho,
        filename=doc.original_filename
    )


@router.delete("/documents/{document_id}")
async def deletar_documento(
    document_id: str
):

    doc = await Documento.get(
        PydanticObjectId(document_id)
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

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