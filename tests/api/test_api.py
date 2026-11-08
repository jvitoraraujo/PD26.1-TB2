import asyncio
import os
from datetime import datetime, timedelta, timezone


from app.core.config import settings
from tests.api.helpers import PDF, PNG, nova_especialidade, novo_paciente


async def _criar(cliente, url, corpo, status=201):
    r = await cliente.post(url, json=corpo)
    assert r.status_code == status, r.text
    return r.json()


async def _cenario(cliente):
    esp = await _criar(cliente, "/especialidades/", nova_especialidade())
    medico = await _criar(cliente, "/medicos/", {
        "nome": "Dra. Ana", "crm": f"CRM{os.urandom(4).hex()}", "telefone": "8533330000",
        "cidade": "Fortaleza", "uf": "CE", "especialidades": [esp["id"]],
    })
    paciente = await _criar(cliente, "/pacientes/", novo_paciente())
    return esp, medico, paciente


async def test_health(cliente):
    r = await cliente.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


# ---------------- pacientes ----------------
async def test_paciente_crud_e_validacoes(cliente):
    dados = novo_paciente()
    mascarado = f"{dados['cpf'][:3]}.{dados['cpf'][3:6]}.{dados['cpf'][6:9]}-{dados['cpf'][9:]}"
    criado = await _criar(cliente, "/pacientes/", {**dados, "cpf": mascarado})
    assert criado["cpf"] == dados["cpf"] and criado["uf"] == "CE"

    r = await cliente.post("/pacientes/", json=dados)  # CPF duplicado
    assert r.status_code == 409

    assert (await cliente.post("/pacientes/", json={**novo_paciente(), "cpf": "11111111111"})).status_code == 422
    assert (await cliente.get("/pacientes/abc")).status_code == 422
    assert (await cliente.get("/pacientes/" + "0" * 24)).status_code == 404

    r = await cliente.put(f"/pacientes/{criado['id']}", json={"cidade": "Fortaleza", "email": None})
    assert r.status_code == 200 and r.json()["cidade"] == "Fortaleza"
    assert r.json()["email"] == dados["email"]  # null não apaga campo obrigatório

    assert (await cliente.delete(f"/pacientes/{criado['id']}")).status_code == 200
    assert (await cliente.get(f"/pacientes/{criado['id']}")).status_code == 404


async def test_paginacao(cliente):
    for _ in range(3):
        await _criar(cliente, "/pacientes/", novo_paciente())
    r = await cliente.get("/pacientes/", params={"size": 2, "page": 1})
    corpo = r.json()
    assert r.status_code == 200 and len(corpo["items"]) == 2
    assert corpo["total"] >= 3 and corpo["page"] == 1 and corpo["size"] == 2 and corpo["pages"] >= 2

    ids_p1 = [p["id"] for p in corpo["items"]]
    ids_p2 = [p["id"] for p in (await cliente.get("/pacientes/", params={"size": 2, "page": 2})).json()["items"]]
    assert ids_p2 and not set(ids_p1) & set(ids_p2)  # páginas distintas, sem repetição

    assert (await cliente.get("/pacientes/", params={"size": 0})).status_code == 422
    assert (await cliente.get("/pacientes/", params={"page": 0})).status_code == 422


async def test_rotas_count_nao_sao_confundidas_com_id(cliente):
    for url in ("/consultas/count", "/internacoes/count", "/pacientes/count", "/medicos/count", "/exames/count"):
        r = await cliente.get(url)
        assert r.status_code == 200, url
    assert (await cliente.get("/medicos/estatisticas/count")).status_code == 200


# ---------------- médicos / especialidades ----------------
async def test_medico_especialidades(cliente):
    esp, medico, _ = await _cenario(cliente)
    assert medico["especialidades"] == [esp]

    r = await cliente.post("/medicos/", json={
        "nome": "X", "crm": "SEMESP", "telefone": "1", "cidade": "A", "uf": "CE",
        "especialidades": ["0" * 24],
    })
    assert r.status_code == 404

    r = await cliente.post("/medicos/", json={
        "nome": "Y", "crm": medico["crm"], "telefone": "1", "cidade": "A", "uf": "CE",
        "especialidades": [esp["id"]],
    })
    assert r.status_code == 409  # CRM duplicado

    r = await cliente.get("/medicos/", params={"especialidade_id": esp["id"], "uf": "ce", "cidade": "fortaleza"})
    assert r.status_code == 200 and [m["id"] for m in r.json()["items"]] == [medico["id"]]
    assert (await cliente.get(f"/medicos/{medico['id']}")).json()["especialidades"] == [esp]

    # especialidade em uso não pode ser removida
    assert (await cliente.delete(f"/especialidades/{esp['id']}")).status_code == 400


# ---------------- consultas / exames ----------------
async def test_fluxo_consulta_exame_e_integridade(cliente):
    _, medico, paciente = await _cenario(cliente)
    corpo = {"paciente_id": paciente["id"], "medico_id": medico["id"], "diagnostico": "Gripe forte"}

    c1 = await _criar(cliente, "/consultas/", corpo)
    await asyncio.sleep(0.05)
    c2 = await _criar(cliente, "/consultas/", {**corpo, "diagnostico": "Outra"})
    assert c1["data_consulta"] != c2["data_consulta"]  # regressão: default avaliado uma única vez

    assert (await cliente.post("/consultas/", json={**corpo, "medico_id": "0" * 24})).status_code == 404
    assert (await cliente.post("/consultas/", json={**corpo, "paciente_id": "xyz"})).status_code == 422

    r = await cliente.get("/consultas/", params={"paciente_id": paciente["id"], "diagnostico": "gripe"})
    assert [c["id"] for c in r.json()["items"]] == [c1["id"]]
    amanha = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    r = await cliente.get("/consultas/", params={"medico_id": medico["id"], "data_inicio": amanha})
    assert r.json()["items"] == [] and r.json()["total"] == 0

    r = await cliente.put(f"/consultas/{c1['id']}", json={"medico_id": "0" * 24})
    assert r.status_code == 404  # antes: AttributeError -> 500
    r = await cliente.put(f"/consultas/{c1['id']}", json={"diagnostico": None})
    assert r.status_code == 200 and r.json()["diagnostico"] is None

    exame = await _criar(cliente, "/exames/", {"tipo": "Hemograma", "resultado": "ok", "consulta_id": c1["id"]})
    r = await cliente.put(f"/exames/{exame['id']}", json={"tipo": None, "resultado": "normal"})
    assert r.status_code == 200 and r.json()["tipo"] == "Hemograma"

    assert (await cliente.delete(f"/consultas/{c1['id']}")).status_code == 400  # tem exame
    assert (await cliente.delete(f"/pacientes/{paciente['id']}")).status_code == 400  # tem consulta
    assert (await cliente.delete(f"/medicos/{medico['id']}")).status_code == 400

    assert (await cliente.delete(f"/exames/{exame['id']}")).status_code == 200
    assert (await cliente.delete(f"/consultas/{c1['id']}")).status_code == 200


# ---------------- internações ----------------
async def test_internacao(cliente):
    _, medico, paciente = await _cenario(cliente)
    base = {
        "paciente_id": paciente["id"], "medico_id": medico["id"], "quarto": "101",
        "motivo": "Cirurgia", "valor_diaria": 350.0, "data_entrada": "2026-01-10T10:00:00",
    }
    assert (await cliente.post("/internacoes/", json={**base, "data_saida": "2026-01-09T10:00:00"})).status_code == 422
    assert (await cliente.post("/internacoes/", json={**base, "valor_diaria": -1})).status_code == 422
    assert (await cliente.post("/internacoes/", json={**{k: v for k, v in base.items() if k != "quarto"}})).status_code == 422

    criada = await _criar(cliente, "/internacoes/", base)
    assert criada["data_saida"] is None

    r = await cliente.put(f"/internacoes/{criada['id']}", json={"data_saida": "2026-01-15T10:00:00"})  # alta
    assert r.status_code == 200 and r.json()["data_saida"].startswith("2026-01-15")
    r = await cliente.put(f"/internacoes/{criada['id']}", json={"data_saida": "2026-01-01T10:00:00"})
    assert r.status_code == 400

    r = await cliente.get("/internacoes/", params={"paciente_id": paciente["id"]})
    assert [i["id"] for i in r.json()["items"]] == [criada["id"]]
    assert (await cliente.delete(f"/internacoes/{criada['id']}")).status_code == 200


# ---------------- documentos ----------------
async def test_documentos_upload_download_delete(cliente, monkeypatch):
    paciente = await _criar(cliente, "/pacientes/", novo_paciente())
    url = f"/pacientes/{paciente['id']}/documents"

    r = await cliente.post(url, files={"file": ("../../laudo.pdf", PDF, "application/pdf")})
    assert r.status_code == 201, r.text
    doc = r.json()
    assert doc["original_filename"] == "laudo.pdf" and doc["extension"] == ".pdf" and doc["size_bytes"] == len(PDF)

    r = await cliente.get(f"/documents/{doc['id']}/download")
    assert r.status_code == 200 and r.content == PDF
    assert r.headers["x-content-type-options"] == "nosniff"

    # tipo declarado x conteúdo real, tipo proibido, vazio e grande demais
    assert (await cliente.post(url, files={"file": ("a.pdf", b"<html>", "application/pdf")})).status_code == 400
    assert (await cliente.post(url, files={"file": ("a.html", b"<html>", "text/html")})).status_code == 400
    assert (await cliente.post(url, files={"file": ("a.png", b"", "image/png")})).status_code == 400
    monkeypatch.setattr(settings, "MAX_UPLOAD_BYTES", 10)
    assert (await cliente.post(url, files={"file": ("a.png", PNG, "image/png")})).status_code == 413
    monkeypatch.undo()

    # não sobram temporários nem arquivos órfãos
    assert not [f for f in os.listdir(settings.UPLOAD_DIR) if f.endswith(".tmp")]

    lista = (await cliente.get(url)).json()
    assert [d["id"] for d in lista["items"]] == [doc["id"]]

    assert (await cliente.delete(f"/documents/{doc['id']}")).status_code == 200
    assert (await cliente.get(f"/documents/{doc['id']}/download")).status_code == 404
    assert not os.path.exists(settings.UPLOAD_DIR / f"{doc['id']}.pdf")


async def test_excluir_paciente_remove_documentos(cliente):
    paciente = await _criar(cliente, "/pacientes/", novo_paciente())
    r = await cliente.post(f"/pacientes/{paciente['id']}/documents", files={"file": ("x.png", PNG, "image/png")})
    doc = r.json()
    assert (await cliente.delete(f"/pacientes/{paciente['id']}")).status_code == 200
    assert (await cliente.get(f"/documents/{doc['id']}")).status_code == 404
    assert not os.path.exists(settings.UPLOAD_DIR / f"{doc['id']}.png")
