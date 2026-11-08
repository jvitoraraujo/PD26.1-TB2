from bson.errors import InvalidId
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError


class EntidadeNaoEncontradaException(Exception):
    def __init__(self, entidade: str, id_ou_parametro: str | int):
        self.entidade = entidade
        self.id_ou_parametro = id_ou_parametro


class RegraNegocioException(Exception):
    def __init__(self, detalhe: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detalhe = detalhe
        self.status_code = status_code


def configurar_excecoes(app: FastAPI) -> None:
    """Registra os manipuladores globais de exceção."""

    @app.exception_handler(EntidadeNaoEncontradaException)
    async def not_found_handler(request: Request, exc: EntidadeNaoEncontradaException):
        mensagem = f"{exc.entidade} com valor '{exc.id_ou_parametro}' não foi encontrado(a)."
        # "detail" mantém compatibilidade com o formato padrão do FastAPI
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"erro": mensagem, "detail": mensagem},
        )

    @app.exception_handler(RegraNegocioException)
    async def regra_negocio_handler(request: Request, exc: RegraNegocioException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"erro": "Violação de regra de negócio", "detalhe": exc.detalhe},
        )

    @app.exception_handler(DuplicateKeyError)
    async def duplicado_handler(request: Request, exc: DuplicateKeyError):
        campos = ", ".join((exc.details or {}).get("keyPattern", {})) or "campo único"
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"erro": "Registro duplicado", "detalhe": f"Já existe um registro com o mesmo valor de: {campos}."},
        )

    @app.exception_handler(InvalidId)
    async def id_invalido_handler(request: Request, exc: InvalidId):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"erro": "Identificador inválido", "detalhe": str(exc)},
        )
