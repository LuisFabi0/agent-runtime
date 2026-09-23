from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="agent-runtime", version="0.1.0")


class Health(BaseModel):
    status: str


@app.get("/health")
def health() -> Health:
    return Health(status="ok")
