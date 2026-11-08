from .paciente import Paciente
from .medico import Medico
from .consulta import Consulta
from .internacao import Internacao
from .exame import Exame
from .documento import Documento
from .especialidade import Especialidade

# Fonte única da lista de modelos (usada por app.db.db.init_db e pelo seed)
MODELOS = [
    Paciente,
    Medico,
    Consulta,
    Internacao,
    Exame,
    Documento,
    Especialidade,
]

__all__ = ["MODELOS", *(m.__name__ for m in MODELOS)]
