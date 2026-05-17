"""
Script de carga inicial — popula o banco SQLite com dados realistas.
Execute com: uv run python scripts/carga_inicial_tp2.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from random import choice, randint

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.consulta import Consulta
from app.models.exame import Exame
from app.models.internacao import Internacao

fake = Faker("pt_BR")

ESPECIALIDADES = [
    "Cardiologia", "Pediatria", "Ortopedia", "Neurologia",
    "Dermatologia", "Ginecologia", "Oftalmologia", "Psiquiatria",
    "Endocrinologia", "Urologia", "Clínica Geral", "Oncologia",
    "Reumatologia", "Pneumologia", "Gastroenterologia",
]

UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]

MOTIVOS_INTERNACAO = [
    "Pneumonia", "Cirurgia eletiva", "Fratura de fêmur",
    "Infarto agudo do miocárdio", "AVC isquêmico", "Apendicite aguda",
    "Parto normal", "Parto cesárea", "Insuficiência renal aguda",
    "Sepse hospitalar",
]

TIPOS_EXAME = [
    "Hemograma completo", "Raio-X tórax", "Ressonância magnética",
    "Tomografia computadorizada", "Eletrocardiograma", "Ultrassom abdominal",
    "Glicemia em jejum", "Colesterol total", "TSH", "PSA",
]

QUARTOS = [f"{andar}{str(numero).zfill(2)}" for andar in range(1, 6) for numero in range(1, 11)]


async def criar_medicos(session: AsyncSession, quantidade: int) -> list[Medico]:
    print(f"  Inserindo {quantidade} médicos...")
    medicos = []
    for i in range(quantidade):
        uf = choice(UFS)
        medico = Medico(
            nome=fake.name(),
            crm=f"CRM/{uf} {randint(10000, 99999)}",
            especialidade=choice(ESPECIALIDADES),
            telefone=fake.phone_number(),
            email=fake.email() if randint(0, 1) else None,
            cidade=fake.city(),
            uf=uf,
            ativo=choice([True, True, True, False]),
        )
        session.add(medico)
        medicos.append(medico)
        if (i + 1) % 100 == 0:
            print(f"    {i + 1} médicos...")
    await session.flush()
    return medicos


async def criar_pacientes(session: AsyncSession, quantidade: int) -> list[Paciente]:
    print(f"  Inserindo {quantidade} pacientes...")
    pacientes = []
    cpfs_usados = set()
    for i in range(quantidade):
        cpf = fake.cpf().replace(".", "").replace("-", "")
        while cpf in cpfs_usados:
            cpf = fake.cpf().replace(".", "").replace("-", "")
        cpfs_usados.add(cpf)
        paciente = Paciente(
            nome=fake.name(),
            cpf=cpf,
            telefone=fake.phone_number(),
            email=fake.email(),
            cidade=fake.city(),
            uf=choice(UFS),
        )
        session.add(paciente)
        pacientes.append(paciente)
        if (i + 1) % 100 == 0:
            print(f"    {i + 1} pacientes...")
    await session.flush()
    return pacientes


async def criar_consultas(
    session: AsyncSession,
    pacientes: list[Paciente],
    medicos: list[Medico],
    quantidade: int,
) -> list[Consulta]:
    print(f"  Inserindo {quantidade} consultas...")
    consultas = []
    for i in range(quantidade):
        data = fake.date_time_between(start_date="-2y", end_date="now")
        consulta = Consulta(
            data_consulta=data,
            diagnostico=fake.sentence(nb_words=5) if randint(0, 1) else None,
            paciente_id=choice(pacientes).id,
            medico_id=choice(medicos).id,
        )
        session.add(consulta)
        consultas.append(consulta)
        if (i + 1) % 100 == 0:
            print(f"    {i + 1} consultas...")
    await session.flush()
    return consultas


async def criar_exames(
    session: AsyncSession,
    consultas: list[Consulta],
    quantidade: int,
) -> None:
    print(f"  Inserindo {quantidade} exames...")
    for i in range(quantidade):
        exame = Exame(
            tipo=choice(TIPOS_EXAME),
            resultado=fake.sentence(nb_words=6),
            consulta_id=choice(consultas).id,
        )
        session.add(exame)
        if (i + 1) % 100 == 0:
            print(f"    {i + 1} exames...")
    await session.flush()


async def criar_internacoes(
    session: AsyncSession,
    pacientes: list[Paciente],
    medicos: list[Medico],
    quantidade: int,
) -> None:
    print(f"  Inserindo {quantidade} internações...")
    for i in range(quantidade):
        entrada = fake.date_time_between(start_date="-2y", end_date="-3d")
        ainda_internado = randint(0, 4) == 0
        saida = None if ainda_internado else fake.date_time_between(
            start_date=entrada, end_date="now"
        )
        internacao = Internacao(
            data_entrada=entrada,
            data_saida=saida,
            quarto=choice(QUARTOS),
            motivo=choice(MOTIVOS_INTERNACAO),
            observacoes=fake.sentence(nb_words=8) if randint(0, 1) else None,
            valor_diaria=round(randint(300, 2500) + 0.0, 2),
            paciente_id=choice(pacientes).id,
            medico_id=choice(medicos).id,
        )
        session.add(internacao)
        if (i + 1) % 100 == 0:
            print(f"    {i + 1} internações...")
    await session.flush()


async def main() -> None:
    print("🏥 Iniciando carga inicial do banco (TP2)...\n")

    async with AsyncSessionLocal() as session:
        async with session.begin():
            medicos = await criar_medicos(session, 100)
            pacientes = await criar_pacientes(session, 100)
            consultas = await criar_consultas(session, pacientes, medicos, 100)
            await criar_exames(session, consultas, 100)
            await criar_internacoes(session, pacientes, medicos, 100)

    print("\n✅ Carga concluída! 500 registros inseridos.")


if __name__ == "__main__":
    asyncio.run(main())