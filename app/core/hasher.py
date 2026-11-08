from __future__ import annotations

import hashlib
from enum import StrEnum


class AlgoritmoHash(StrEnum):
    MD5 = "MD5"
    SHA1 = "SHA-1"
    SHA256 = "SHA-256"


def gerar_hash(valor: str, algoritmo: AlgoritmoHash) -> str:
    mapa = {
        AlgoritmoHash.MD5: hashlib.md5,
        AlgoritmoHash.SHA1: hashlib.sha1,
        AlgoritmoHash.SHA256: hashlib.sha256,
    }
    funcao = mapa[algoritmo]
    return funcao(valor.encode("utf-8")).hexdigest()