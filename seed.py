print("INICIANDO SEED")
import asyncio
import random
from datetime import datetime, timedelta

from faker import Faker
from beanie import init_beanie

from app.db.db import client, db

from app.models import (
    Paciente,
    Medico,
    Consulta,
    Internacao,
    Exame,
    Documento,
    Especialidade,
)

fake = Faker("pt_BR")

ESPECIALIDADES = [
    "Cardiologia",
    "Pediatria",
    "Ortopedia",
    "Neurologia",
    "Dermatologia",
    "Psiquiatria",
    "Urologia",
    "Oftalmologia",
    "Ginecologia",
    "Clínica Geral",
]


async def seed():

    # 🔴 PRIMEIRO: inicializa Beanie aqui também
    await init_beanie(
        database=db,
        document_models=[
            Paciente,
            Medico,
            Consulta,
            Internacao,
            Exame,
            Documento,
            Especialidade,
        ],
    )

    print("Limpando coleções...")

    await Paciente.delete_all()
    await Medico.delete_all()
    await Consulta.delete_all()
    await Internacao.delete_all()
    await Exame.delete_all()
    await Documento.delete_all()
    await Especialidade.delete_all()

    # -----------------------
    # Especialidades
    # -----------------------
    especialidades = []

    for nome in ESPECIALIDADES:
        esp = Especialidade(nome=nome)
        await esp.insert()
        especialidades.append(esp)

    print("Especialidades criadas")

    # -----------------------
    # Médicos
    # -----------------------
    medicos = []

    for _ in range(100):
        medico = Medico(
            nome=fake.name(),
            crm=str(fake.random_number(digits=6)),
            telefone=fake.phone_number(),
            email=fake.email(),
            cidade=fake.city(),
            uf=fake.estado_sigla(),
            ativo=random.choice([True, False]),
            especialidades=random.sample(especialidades, k=random.randint(1, 3)),
        )
        await medico.insert()
        medicos.append(medico)

    print("100 médicos criados")

    # -----------------------
    # Pacientes
    # -----------------------
    pacientes = []

    for _ in range(100):
        paciente = Paciente(
            nome=fake.name(),
            cpf=fake.cpf(),
            telefone=fake.phone_number(),
            email=fake.email(),
            cidade=fake.city(),
            uf=fake.estado_sigla(),
        )
        await paciente.insert()
        pacientes.append(paciente)

    print("100 pacientes criados")

    # -----------------------
    # Consultas
    # -----------------------
    consultas = []

    for _ in range(100):
        consulta = Consulta(
            data_consulta=fake.date_time_between("-2y", "now"),
            diagnostico=fake.sentence(),
            paciente=random.choice(pacientes),
            medico=random.choice(medicos),
        )
        await consulta.insert()
        consultas.append(consulta)

    print("100 consultas criadas")

    # -----------------------
    # Internações
    # -----------------------
    for _ in range(100):

        entrada = fake.date_time_between("-2y", "now")
        saida = entrada + timedelta(days=random.randint(1, 15))

        internacao = Internacao(
            data_entrada=entrada,
            data_saida=saida,
            quarto=str(random.randint(100, 999)),
            motivo=fake.sentence(),
            observacoes=fake.text(max_nb_chars=100),
            valor_diaria=round(random.uniform(150, 1500), 2),
            paciente=random.choice(pacientes),
            medico=random.choice(medicos),
        )

        await internacao.insert()

    print("100 internações criadas")

    print("Seed finalizado com sucesso!")


if __name__ == "__main__":
    asyncio.run(seed())