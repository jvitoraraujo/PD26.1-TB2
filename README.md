# Sistema de Gestão Hospitalar - API

API para gestão hospitalar com suporte a gerenciamento de entidades (Pacientes, Médicos, etc.) e armazenamento em nuvem de exames e documentos.

## Tecnologias
- **FastAPI**: Framework web Python.
- **MongoDB / Beanie**: Banco de dados NoSQL e ODM.
- **MinIO**: Object Storage (compatível com Amazon S3) para arquivos físicos.
- **Docker**: Orquestração de containers.

## Como rodar o projeto localmente

1. Certifique-se de ter o Docker e Docker Compose instalados.
2. Clone o repositório.
3. Na raiz do projeto, execute:
   ```bash
   docker-compose up --build -d

## Diagrama de Classes

```mermaid
classDiagram
class Paciente {
    -String id
    -String nome
    -String cpf
    -Date data_nascimento
    -String telefone
    -String endereco
    +cadastrar()
    +atualizarDados()
}
class Medico {
    -String id
    -String nome
    -String crm
    +cadastrar()
    +atualizarDados()
}
class Especialidade {
    -String id
    -String nome
    -String descricao
}
class Consulta {
    -String id
    -Date data_hora
    -String status
    -String diagnostico
    +agendar()
    +cancelar()
    +finalizar()
}
class Exame {
    -String id
    -String nome
    -Date data_realizacao
    -String resultado
    +registrar()
}
class Internacao {
    -String id
    -Date data_entrada
    -Date data_alta
    -String leito
    -String motivo
    +registrarEntrada()
    +registrarAlta()
}
class Documento {
    -String id
    -String original_filename
    -String content_type
    -String extension
    -int size_bytes
    -Date created_at
    +upload()
    +download()
    +deletar()
}
%% Relacionamentos do Sistema Hospitalar
Paciente "1" --> "*" Consulta : realiza
Paciente "1" --> "*" Exame : faz
Paciente "1" --> "*" Internacao : possui
Paciente "1" --> "*" Documento : possui
Medico "1" --> "*" Consulta : atende
Medico "*" --> "1" Especialidade : possui
Consulta "1" --> "*" Exame : gera
```