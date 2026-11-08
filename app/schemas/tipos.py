"""Tipos anotados reutilizáveis nos schemas."""
from datetime import datetime
from typing import Annotated

from bson import ObjectId
from pydantic import AfterValidator, StringConstraints

from app.core.validadores import como_utc, cpf_valido, somente_digitos


def _validar_objectid(valor: str) -> str:
    if not ObjectId.is_valid(valor):
        raise ValueError("Identificador inválido (esperado ObjectId de 24 caracteres hexadecimais)")
    return valor


def _normalizar_cpf(valor: str) -> str:
    digitos = somente_digitos(valor)
    if not cpf_valido(digitos):
        raise ValueError("CPF inválido")
    return digitos


IdObjeto = Annotated[str, AfterValidator(_validar_objectid)]
Cpf = Annotated[str, AfterValidator(_normalizar_cpf)]
Uf = Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, pattern=r"^[A-Za-z]{2}$")]
DataHora = Annotated[datetime, AfterValidator(como_utc)]
