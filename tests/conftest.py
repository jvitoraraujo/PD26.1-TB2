"""Configuração dos testes.

As variáveis de ambiente precisam ser definidas ANTES de importar `app`, pois
`app.core.config` e `app.db.db` são avaliados no import.
Os testes de API usam um banco temporário e são pulados se o MongoDB não responder.
MongoDB de teste: variável TEST_MONGODB_URL (padrão mongodb://localhost:27017).
"""
import os
import tempfile
import uuid

os.environ["MONGODB_URL"] = os.environ.get("TEST_MONGODB_URL", "mongodb://localhost:27017")
os.environ["DATABASE_NAME"] = f"hospital_test_{uuid.uuid4().hex[:8]}"
os.environ["MONGODB_TIMEOUT_MS"] = "1500"
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp(prefix="uploads_test_")

import httpx  # noqa: E402
import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402


@pytest_asyncio.fixture(scope="session")
async def app_iniciado():
    from app.db.db import client, db, init_db

    try:
        await client.admin.command("ping")
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"MongoDB indisponível ({type(exc).__name__}); testes de API pulados")
    await init_db()
    from app.main import app

    yield app
    await client.drop_database(db.name)
    await client.close()


@pytest_asyncio.fixture
async def cliente(app_iniciado):
    transport = httpx.ASGITransport(app=app_iniciado)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
