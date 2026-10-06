# API HTTP mínima que n8n invoca. Por ahora solo expone /health para probar
# la conexión n8n -> pb-coach; POST /plan y POST /semana/ajustar llegan
# cuando el motor y el agente estén listos.

from fastapi import FastAPI

app = FastAPI(title="pb-coach")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
