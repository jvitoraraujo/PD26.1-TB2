"""Utilitários compartilhados pelos routers (busca com 404, ids de links, paginação)."""
from collections.abc import Callable

from beanie import Document, Link, PydanticObjectId
from fastapi_pagination.ext.beanie import apaginate

from app.core.exceptions import EntidadeNaoEncontradaException


def link_id(valor: Link | Document) -> PydanticObjectId:
    """Id do documento relacionado, esteja o link carregado (Document) ou não (Link).

    Evita o $lookup de `fetch_links=True` quando só o id é necessário.
    """
    if isinstance(valor, Link):
        return valor.ref.id
    return valor.id


async def obter_ou_404[T: Document](modelo: type[T], id_: str | PydanticObjectId, entidade: str) -> T:
    doc = await modelo.get(PydanticObjectId(id_))
    if doc is None:
        raise EntidadeNaoEncontradaException(entidade, str(id_))
    return doc


async def paginar(busca, converter: Callable):
    """Pagina uma busca do Beanie com fastapi-pagination.

    A busca é ordenada por _id (paginação estável) e cada documento é convertido por `converter`.
    Use em rotas com `response_model=Page[Schema]`; page/size vêm da query string.
    """
    return await apaginate(
        busca.sort("_id"),
        transformer=lambda itens: [converter(i) for i in itens],
    )
