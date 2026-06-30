from bson.errors import InvalidId
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError


class EntidadeNaoEncontradaException(Exception):
    """Levantada quando uma busca por ID ou parâmetro não encontra o registro."""

    def __init__(self, entidade: str, id_ou_parametro: str | int):
        self.entidade = entidade
        self.id_ou_parametro = id_ou_parametro


class RegraNegocioException(Exception):
    """Levantada quando uma regra de negócio é violada (ex: dados inconsistentes)."""

    def __init__(self, detalhe: str):
        self.detalhe = detalhe


class IdInvalidoException(Exception):
    """Levantada quando uma string recebida não é um ObjectId válido do MongoDB."""

    def __init__(self, valor: str, campo: str = "id"):
        self.valor = valor
        self.campo = campo


class RegistroDuplicadoException(Exception):
    """Levantada quando uma operação viola uma restrição de unicidade (ex: CPF, CRM)."""

    def __init__(self, detalhe: str):
        self.detalhe = detalhe


def configurar_excecoes(app: FastAPI):
    """Registra todos os exception handlers customizados da aplicação."""

    @app.exception_handler(EntidadeNaoEncontradaException)
    async def not_found_handler(request: Request, exc: EntidadeNaoEncontradaException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"erro": f"{exc.entidade} com valor '{exc.id_ou_parametro}' não foi encontrado(a)."},
        )

    @app.exception_handler(RegraNegocioException)
    async def regra_negocio_handler(request: Request, exc: RegraNegocioException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"erro": "Violação de regra de negócio", "detalhe": exc.detalhe},
        )

    @app.exception_handler(IdInvalidoException)
    async def id_invalido_handler(request: Request, exc: IdInvalidoException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "erro": f"O valor '{exc.valor}' informado para '{exc.campo}' não é um identificador válido.",
            },
        )

    @app.exception_handler(RegistroDuplicadoException)
    async def duplicado_handler(request: Request, exc: RegistroDuplicadoException):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"erro": "Registro duplicado", "detalhe": exc.detalhe},
        )

    @app.exception_handler(InvalidId)
    async def bson_invalid_id_handler(request: Request, exc: InvalidId):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"erro": f"Identificador inválido: {str(exc)}"},
        )

    @app.exception_handler(DuplicateKeyError)
    async def mongo_duplicate_key_handler(request: Request, exc: DuplicateKeyError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"erro": "Já existe um registro com esse valor único.", "detalhe": str(exc.details.get("keyValue", {}))},
        )