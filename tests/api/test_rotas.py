"""Garante que nenhuma rota literal (ex.: /count) seja engolida por uma rota com parâmetro."""
import re

from fastapi.routing import APIRoute

import tests.conftest  # noqa: F401  (define as variáveis de ambiente)


def test_rotas_literais_nao_sao_sombreadas():
    from app.main import app

    rotas = [r for r in app.routes if isinstance(r, APIRoute)]
    for rota in rotas:
        concreto = re.sub(r"\{[^}]+\}", "x", rota.path)
        for metodo in rota.methods:
            primeira = next(r for r in rotas if metodo in r.methods and r.path_regex.match(concreto))
            assert primeira is rota, f"{metodo} {rota.path} é sombreada por {primeira.path}"
