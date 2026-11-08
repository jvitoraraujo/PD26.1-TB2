"""Executa o seed (com poucos registros) no banco temporário e confere o que foi gravado."""
import pytest

pytest.importorskip("faker")


async def test_seed_grava_dados_consistentes(cliente):
    from seed import ESPECIALIDADES, seed, verificar

    problemas = await seed(5)
    assert problemas == []

    # a API enxerga o que o seed gravou (dados e relacionamentos)
    r = await cliente.get("/medicos/count")
    assert r.json()["total_medicos"] == 5
    r = await cliente.get("/especialidades/", params={"size": 100})
    assert r.json()["total"] == len(ESPECIALIDADES)
    medicos = (await cliente.get("/medicos/")).json()["items"]
    assert all(m["especialidades"] for m in medicos)
    consulta = (await cliente.get("/consultas/")).json()["items"][0]
    assert (await cliente.get(f"/pacientes/{consulta['paciente_id']}")).status_code == 200
    assert (await cliente.get(f"/medicos/{consulta['medico_id']}")).status_code == 200

    # re-executar limpa e recria, sem acumular nem violar os índices únicos
    assert await seed(3) == []
    assert await verificar(3) == []
