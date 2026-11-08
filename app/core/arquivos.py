"""Tipos de arquivo aceitos e detecção por assinatura (magic bytes)."""
from __future__ import annotations

# content-type aceito -> extensão canônica usada no armazenamento
TIPOS_PERMITIDOS: dict[str, str] = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def detectar_tipo(cabecalho: bytes) -> str | None:
    """Identifica o content-type real a partir dos primeiros bytes do arquivo."""
    if cabecalho.startswith(b"%PDF-"):
        return "application/pdf"
    if cabecalho.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if cabecalho.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if cabecalho[:4] == b"RIFF" and cabecalho[8:12] == b"WEBP":
        return "image/webp"
    return None
