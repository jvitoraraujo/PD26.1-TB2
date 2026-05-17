import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"

DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/gestao_hospitalar.db"