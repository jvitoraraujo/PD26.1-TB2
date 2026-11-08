import itertools
import random

_contador = itertools.count(1)


def cpf_valido_aleatorio() -> str:
    base = [random.randint(0, 9) for _ in range(9)]
    if len(set(base)) == 1:
        base[0] = (base[0] + 1) % 10
    for tamanho in (9, 10):
        soma = sum(d * p for d, p in zip(base, range(tamanho + 1, 1, -1)))
        base.append((soma * 10 % 11) % 10)
    return "".join(map(str, base))


def novo_paciente(**extra) -> dict:
    n = next(_contador)
    return {
        "nome": f"Paciente {n}", "cpf": cpf_valido_aleatorio(), "telefone": "85999990000",
        "email": f"p{n}@exemplo.com", "cidade": "Quixadá", "uf": "ce", **extra,
    }


def nova_especialidade() -> dict:
    return {"nome": f"Especialidade {next(_contador)}-{random.randint(0, 10**6)}"}


PDF = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
