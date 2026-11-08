"""Popula o banco com dados fictícios (Faker pt_BR).

Uso:
    python seed.py                  # pede confirmação antes de apagar os dados
    python seed.py --yes            # sem confirmação
    python seed.py --quantidade 500 # registros por entidade (padrão: 100)
"""
import argparse
import asyncio
import random
import re
from datetime import timedelta

from faker import Faker

from app.core.config import settings
from app.core.validadores import somente_digitos
from app.db.db import close_db, init_db
from app.models import Consulta, Especialidade, Exame, Internacao, Medico, Paciente, Documento

fake = Faker("pt_BR")

ESPECIALIDADES = [
    "Cardiologia", "Pediatria", "Ortopedia", "Neurologia", "Dermatologia",
    "Psiquiatria", "Urologia", "Oftalmologia", "Ginecologia", "Clínica Geral",
]
TIPOS_EXAME = ["Hemograma", "Raio-X", "Ressonância", "Ultrassom", "Eletrocardiograma", "Glicemia"]


ARQUIVO_DOCUMENTO = re.compile(r"^[0-9a-f]{24}\.(pdf|jpg|png|webp)$")


def _limpar_arquivos_enviados() -> int:
    """Remove os arquivos de documentos (<id>.<ext>) que ficariam órfãos ao apagar a coleção."""
    if not settings.UPLOAD_DIR.is_dir():
        return 0
    arquivos = [a for a in settings.UPLOAD_DIR.iterdir() if ARQUIVO_DOCUMENTO.match(a.name)]
    for arquivo in arquivos:
        arquivo.unlink()
    return len(arquivos)


async def seed(quantidade: int) -> list[str]:
    await init_db()

    print("Limpando coleções...")
    for modelo in (Documento, Exame, Internacao, Consulta, Paciente, Medico, Especialidade):
        await modelo.delete_all()
    removidos = _limpar_arquivos_enviados()
    if removidos:
        print(f"{removidos} arquivo(s) de documentos removido(s)")

    # insert_many não preenche os ids nos objetos locais; por isso cada lote é relido do banco
    await Especialidade.insert_many([Especialidade(nome=n) for n in ESPECIALIDADES])
    especialidades = await Especialidade.find_all().to_list()
    print(f"{len(especialidades)} especialidades criadas")

    await Medico.insert_many([
        Medico(
            nome=fake.name(),
            crm=str(fake.unique.random_int(100000, 999999)),
            telefone=fake.phone_number(),
            email=fake.email(),
            cidade=fake.city(),
            uf=fake.estado_sigla(),
            ativo=random.choice([True, False]),
            especialidades=random.sample(especialidades, k=random.randint(1, 3)),
        )
        for _ in range(quantidade)
    ])
    medicos = await Medico.find_all().to_list()
    print(f"{len(medicos)} médicos criados")

    await Paciente.insert_many([
        Paciente(
            nome=fake.name(),
            cpf=somente_digitos(fake.unique.cpf()),
            telefone=fake.phone_number(),
            email=fake.email(),
            cidade=fake.city(),
            uf=fake.estado_sigla(),
        )
        for _ in range(quantidade)
    ])
    pacientes = await Paciente.find_all().to_list()
    print(f"{len(pacientes)} pacientes criados")

    await Consulta.insert_many([
        Consulta(
            data_consulta=fake.date_time_between("-2y", "now"),
            diagnostico=fake.sentence(),
            paciente=random.choice(pacientes),
            medico=random.choice(medicos),
        )
        for _ in range(quantidade)
    ])
    consultas = await Consulta.find_all().to_list()
    print(f"{len(consultas)} consultas criadas")

    await Exame.insert_many([
        Exame(tipo=random.choice(TIPOS_EXAME), resultado=fake.sentence(), consulta=random.choice(consultas))
        for _ in range(quantidade)
    ])
    print(f"{quantidade} exames criados")

    internacoes = []
    for _ in range(quantidade):
        entrada = fake.date_time_between("-2y", "now")
        internacoes.append(Internacao(
            data_entrada=entrada,
            data_saida=entrada + timedelta(days=random.randint(1, 15)),
            quarto=str(random.randint(100, 999)),
            motivo=fake.sentence(),
            observacoes=fake.text(max_nb_chars=100),
            valor_diaria=round(random.uniform(150, 1500), 2),
            paciente=random.choice(pacientes),
            medico=random.choice(medicos),
        ))
    await Internacao.insert_many(internacoes)
    print(f"{quantidade} internações criadas")

    print("Verificando integridade...")
    problemas = await verificar(quantidade)
    for problema in problemas:
        print(f"  ✗ {problema}")
    print("Seed finalizado com sucesso!" if not problemas else f"Seed concluído com {len(problemas)} problema(s).")
    return problemas


async def _links_nao_resolvidos(modelo, campos: dict) -> int:
    """Conta referências que não apontam para um documento existente (o Beanie deixa um `Link` não resolvido)."""
    docs = await modelo.find(fetch_links=True).to_list()
    return sum(1 for d in docs for campo, alvo in campos.items() if not isinstance(getattr(d, campo), alvo))


async def verificar(quantidade: int) -> list[str]:
    """Confere o que foi gravado: contagens, unicidade de CPF/CRM e referências válidas. Retorna os problemas."""
    problemas: list[str] = []

    esperado = {
        Especialidade: len(ESPECIALIDADES), Medico: quantidade, Paciente: quantidade,
        Consulta: quantidade, Exame: quantidade, Internacao: quantidade,
    }
    for modelo, n in esperado.items():
        total = await modelo.count()
        if total != n:
            problemas.append(f"{modelo.__name__}: esperado {n} registros, encontrado {total}")

    for modelo, campo in ((Paciente, "cpf"), (Medico, "crm")):
        valores = [getattr(d, campo) for d in await modelo.find_all().to_list()]
        if len(valores) != len(set(valores)):
            problemas.append(f"{modelo.__name__}.{campo} possui valores repetidos")

    for modelo, campos in (
        (Consulta, {"paciente": Paciente, "medico": Medico}),
        (Exame, {"consulta": Consulta}),
        (Internacao, {"paciente": Paciente, "medico": Medico}),
    ):
        quebrados = await _links_nao_resolvidos(modelo, campos)
        if quebrados:
            problemas.append(f"{modelo.__name__}: {quebrados} referência(s) para documentos inexistentes")

    for medico in await Medico.find(fetch_links=True).to_list():
        if not medico.especialidades or not all(isinstance(e, Especialidade) for e in medico.especialidades):
            problemas.append(f"Médico {medico.crm}: especialidades ausentes ou inválidas")
            break
    return problemas


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--yes", action="store_true", help="não pedir confirmação")
    parser.add_argument("--quantidade", type=int, default=100, help="registros por entidade")
    args = parser.parse_args()

    if not args.yes:
        resposta = input(
            f"ATENÇÃO: todas as coleções do banco '{settings.DATABASE_NAME}' serão APAGADAS. Continuar? [s/N] "
        )
        if resposta.strip().lower() != "s":
            print("Cancelado.")
            return
    try:
        problemas = await seed(args.quantidade)
    finally:
        await close_db()
    if problemas:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
