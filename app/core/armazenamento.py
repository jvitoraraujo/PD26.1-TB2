"""Armazenamento em disco dos documentos enviados."""
from __future__ import annotations

import uuid
from pathlib import Path

import anyio

from app.core.arquivos import detectar_tipo
from app.core.config import settings
from app.core.exceptions import RegraNegocioException

TAMANHO_CHUNK = 1024 * 1024


def caminho_documento(doc_id, extensao: str) -> Path:
    return settings.UPLOAD_DIR / f"{doc_id}{extensao}"


async def salvar_upload(arquivo, tipo_esperado: str) -> tuple[Path, int]:
    """Grava o upload em um arquivo temporário, em blocos, sem carregá-lo inteiro na memória.

    Valida o limite de tamanho e a assinatura real do arquivo. Retorna (caminho_temporario, tamanho).
    """
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    temporario = settings.UPLOAD_DIR / f".{uuid.uuid4().hex}.tmp"
    total = 0
    try:
        async with await anyio.open_file(temporario, "wb") as saida:
            primeiro = True
            while bloco := await arquivo.read(TAMANHO_CHUNK):
                if primeiro:
                    if detectar_tipo(bloco) != tipo_esperado:
                        raise RegraNegocioException(
                            "O conteúdo do arquivo não corresponde ao tipo informado."
                        )
                    primeiro = False
                total += len(bloco)
                if total > settings.MAX_UPLOAD_BYTES:
                    raise RegraNegocioException(
                        f"Arquivo excede o limite de {settings.MAX_UPLOAD_BYTES} bytes.",
                        status_code=413,
                    )
                await saida.write(bloco)
        if total == 0:
            raise RegraNegocioException("Arquivo vazio.")
    except BaseException:
        temporario.unlink(missing_ok=True)
        raise
    return temporario, total


def remover_arquivo(caminho: Path) -> None:
    caminho.unlink(missing_ok=True)
