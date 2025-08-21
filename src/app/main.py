from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os

from app.core import core
from app.models import Transaction, Account
from app.schemas import TransactionCreate, TransactionResponse

# Models pour endpoint /event
class EventRequest(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    type: str
    amount: int

class EventResponse(BaseModel):
    id: int | None
    type: str | None
    amount: int | None
    error: str | None = None

app = FastAPI(title="Simple Banking API")

# Compteur global pour simuler IDs
event_counter = 1

@app.get("/", response_model=dict)
async def root():
    return {"message": "API Simple Banking fonctionne ✅"}

@app.post("/event", response_model=EventResponse)
async def create_event(event: EventRequest):
    global event_counter

    # Vérifier les comptes
    if event.type == "deposit":
        account_id = event.destination
    else:
        account_id = event.origin

    if account_id not in ["100", "101"]:
        return JSONResponse(
            status_code=404,
            content={"id": None, "type": None, "amount": None, "error": "Compte non trouvé"}
        )

    # Créer l'événement
    new_event = {
        "id": event_counter,
        "type": event.type,
        "amount": event.amount,
        "error": None
    }
    event_counter += 1

    return JSONResponse(status_code=201, content=new_event)

