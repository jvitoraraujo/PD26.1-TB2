import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Vamos ignorar o .env e forçar o uso do SQLite diretamente
DATABASE_URL = "sqlite+aiosqlite:///./gestao_hospitalar.db"