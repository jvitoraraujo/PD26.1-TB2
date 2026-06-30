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

# -----------------------
# Especialidades reais
# -----------------------

ESPECIALIDADES = [
    "Acupuntura", "Alergia e Imunologia", "Anestesiologia", "Angiologia",
    "Cardiologia", "Cirurgia Cardiovascular", "Cirurgia Geral",
    "Cirurgia Plástica", "Cirurgia Torácica", "Cirurgia Vascular",
    "Clínica Médica", "Dermatologia", "Endocrinologia", "Gastroenterologia",
    "Geriatria", "Ginecologia", "Hematologia", "Infectologia",
    "Mastologia", "Medicina de Família e Comunidade", "Nefrologia",
    "Neurocirurgia", "Neurologia", "Oftalmologia", "Oncologia",
    "Ortopedia", "Otorrinolaringologia", "Pediatria", "Pneumologia",
    "Psiquiatria", "Radiologia", "Reumatologia", "Urologia",
    "Medicina Intensiva", "Medicina do Trabalho", "Medicina Esportiva",
    "Cirurgia Pediátrica", "Endoscopia", "Coloproctologia",
    "Medicina Nuclear", "Patologia", "Radioterapia",
    "Medicina Legal", "Genética Médica", "Nutrologia",
    "Cirurgia Oncológica", "Hepatologia", "Neonatologia",
    "Medicina Fetal", "Dor", "Sono"
]

async def seed():

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

    especialidades = []

    for _ in range(100):
        esp = Especialidade(
            nome=random.choice(ESPECIALIDADES)
        )
        await esp.insert()
        especialidades.append(esp)

    print("100 especialidades criadas")

    medicos = []

    for _ in range(100):
        medico = Medico(
            nome=fake.name(),
            crm=f"{random.randint(10000,99999)}/{fake.estado_sigla()}",
            telefone=fake.phone_number(),
            email=f"dr.{fake.last_name().lower()}{random.randint(1,999)}@hospital.com.br",
            cidade=fake.city(),
            uf=fake.estado_sigla(),
            ativo=random.choice([True, True, True, False]),
            especialidades=random.sample(especialidades, k=random.randint(1, 3)),
        )

        await medico.insert()
        medicos.append(medico)

    print("100 médicos criados")

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

    for _ in range(100):

        entrada = fake.date_time_between("-2y", "now")
        saida = entrada + timedelta(days=random.randint(1, 20))

        internacao = Internacao(
            data_entrada=entrada,
            data_saida=saida,
            quarto=str(random.randint(100, 999)),
            motivo=fake.sentence(),
            observacoes=fake.text(max_nb_chars=120),
            valor_diaria=round(random.uniform(200, 2000), 2),
            paciente=random.choice(pacientes),
            medico=random.choice(medicos),
        )

        await internacao.insert()

    print("100 internações criadas")

    documentos = []

    TIPOS_DOCUMENTO = [
        ("application/pdf", "pdf", "laudo"),
        ("application/pdf", "pdf", "receita"),
        ("application/pdf", "pdf", "atestado"),
        ("image/jpeg", "jpg", "radiografia"),
        ("image/png", "png", "ultrassom"),
    ]

    for paciente in random.sample(pacientes, 100):

        content_type, extension, tipo = random.choice(TIPOS_DOCUMENTO)

        sobrenome = paciente.nome.split()[-1].lower().replace(" ", "_")

        documento = Documento(
            original_filename=f"{tipo}_{sobrenome}_{random.randint(1000,9999)}.{extension}",
            content_type=content_type,
            extension=extension,
            size_bytes=random.randint(100_000, 8_000_000),
            created_at=fake.date_time_between("-2y", "now"),
            paciente=paciente,
        )

        await documento.insert()
        documentos.append(documento)

    print("100 documentos criados")

    TIPOS_EXAME = [
        "Hemograma Completo",
        "Glicemia em Jejum",
        "Colesterol Total",
        "Triglicerídeos",
        "Raio-X de Tórax",
        "Tomografia Computadorizada",
        "Ressonância Magnética",
        "Ultrassonografia Abdominal",
        "Eletrocardiograma",
        "Ecocardiograma",
        "Urina Tipo I",
        "Creatinina",
        "Ureia",
        "TSH",
        "T4 Livre",
        "Vitamina D",
        "PCR",
        "Gasometria Arterial",
        "Densitometria Óssea",
        "Mamografia",
    ]

    RESULTADOS = [
        "Dentro dos valores de referência.",
        "Sem alterações significativas.",
        "Leve alteração observada.",
        "Resultado compatível com o quadro clínico.",
        "Necessário acompanhamento médico.",
        "Sem evidências de anormalidades.",
        "Alteração discreta nos parâmetros.",
        "Resultado normal.",
        "Paciente estável clinicamente.",
        "Recomenda-se acompanhamento periódico.",
    ]

    for _ in range(100):

        exame = Exame(
            tipo=random.choice(TIPOS_EXAME),
            resultado=random.choice(RESULTADOS),
            consulta=random.choice(consultas),
        )

        await exame.insert()

    print("100 exames criados")

    print("Seed finalizado com sucesso!")

if __name__ == "__main__":
    asyncio.run(seed())