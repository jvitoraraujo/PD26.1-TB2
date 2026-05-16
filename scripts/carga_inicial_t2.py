"""
Carga inicial de Pacientes, Consultas e Exames (100+ registros cada)
Executar: uv run python scripts/carga_inicial_t2.py
"""

import sys
import asyncio
from pathlib import Path
from random import choice, randint
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from faker import Faker
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.paciente import Paciente
from app.models.consulta import Consulta
from app.models.exame import Exame

fake = Faker("pt_BR")

QUANTIDADE_PACIENTES = 150
QUANTIDADE_CONSULTAS = 300
QUANTIDADE_EXAMES = 400

UFS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]
TIPOS_EXAME = ["Hemograma", "Raio-X", "Ressonância", "Tomografia", "Ultrassom", "Eletrocardiograma", "Colesterol", "Glicemia"]


async def carregar_pacientes(session):
    print(f"Carregando {QUANTIDADE_PACIENTES} pacientes...")
    for _ in range(QUANTIDADE_PACIENTES):
        paciente = Paciente(
            nome=fake.name(),
            cpf=fake.cpf(),
            telefone=fake.phone_number(),
            email=fake.email(),
            cidade=fake.city(),
            uf=choice(UFS)
        )
        session.add(paciente)
    await session.commit()
    print("Pacientes inseridos.")


async def carregar_consultas(session):
    # Busca todos os IDs de pacientes já inseridos
    result = await session.execute(select(Paciente.id))
    pacientes_ids = [row[0] for row in result.all()]
    if not pacientes_ids:
        print("Nenhum paciente encontrado. Execute primeiro a carga de pacientes.")
        return

    print(f"Carregando {QUANTIDADE_CONSULTAS} consultas...")
    hoje = datetime.now()
    for _ in range(QUANTIDADE_CONSULTAS):
        dias_antes = randint(0, 180)
        consulta = Consulta(
            data_consulta=hoje - timedelta(days=dias_antes),
            paciente_id=choice(pacientes_ids)
        )
        session.add(consulta)
    await session.commit()
    print("Consultas inseridas.")


async def carregar_exames(session):
    result = await session.execute(select(Consulta.id))
    consultas_ids = [row[0] for row in result.all()]
    if not consultas_ids:
        print("Nenhuma consulta encontrada. Execute primeiro a carga de consultas.")
        return

    print(f"Carregando {QUANTIDADE_EXAMES} exames...")
    for _ in range(QUANTIDADE_EXAMES):
        exame = Exame(
            tipo=choice(TIPOS_EXAME),
            resultado=fake.sentence(nb_words=5),
            consulta_id=choice(consultas_ids)
        )
        session.add(exame)
    await session.commit()
    print("Exames inseridos.")


async def main():
    async with AsyncSessionLocal() as session:
        await carregar_pacientes(session)
        await carregar_consultas(session)
        await carregar_exames(session)

    print("\n✅ Carga completa! Pacientes, consultas e exames populados.")


if __name__ == "__main__":
    asyncio.run(main())