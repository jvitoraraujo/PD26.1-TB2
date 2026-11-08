"""Funções puras de validação/normalização (somente biblioteca padrão)."""
from __future__ import annotations

import re
from datetime import datetime, timezone


def somente_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor)


def cpf_valido(cpf: str) -> bool:
    """Valida um CPF já reduzido a dígitos (11 dígitos + dígitos verificadores)."""
    if len(cpf) != 11 or not cpf.isdigit() or cpf == cpf[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(d) * peso for d, peso in zip(cpf[:tamanho], range(tamanho + 1, 1, -1)))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[tamanho]):
            return False
    return True


def como_utc(valor: datetime) -> datetime:
    """Datas sem fuso são interpretadas como UTC; com fuso são convertidas para UTC."""
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)
