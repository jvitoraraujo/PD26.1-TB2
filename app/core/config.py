import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis do ficheiro .env

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# String de conexão assíncrona (Exemplo: PostgreSQL)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://usuario:senha@localhost:5432/gestao_hospitalar"
)