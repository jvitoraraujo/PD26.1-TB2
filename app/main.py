from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.routers import medicos

app = FastAPI(title="Gestão Hospitalar", version="1.0.0")
  
app.include_router(medicos.router)

# Inicializa a paginação globalmente na aplicação
add_pagination(app)

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "API de Gestão Hospitalar Operacional"}