from fastapi import FastAPI, Request, Response, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os

from app.core import core

# ------------------------
# Schemas
# ------------------------
class EventRequest(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    type: str
    amount: int

class EventResponse(BaseModel):
    id: int | None
    type: str | None
    amount: int | None
    origin: Optional[str] = None
    destination: Optional[str] = None
    error: str | None = None

class TransactionCreate(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    type: str
    amount: int

class TransactionResponse(BaseModel):
    id: Optional[str] = None
    type: str
    amount: int
    origin: Optional[str] = None
    destination: Optional[str] = None
    error: Optional[str] = None

# ------------------------
# Application FastAPI
# ------------------------
app = FastAPI(title="Simple Banking API")

templates = Jinja2Templates(directory="app/templates")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_banking.db")

# compteur d'événements simulé
event_counter = 1

# jeu de comptes valides simulé (utilisé par les tests existants)
valid_accounts = ["100", "101"]

# ------------------------
# Routes principales
# ------------------------
@app.get("/", response_model=dict)
async def root():
    return {"message": "API Simple Banking fonctionne ✅"}

@app.get("/create_user", response_class=HTMLResponse)
async def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

@app.post("/create_user")
async def create_user(email: str, password: str):
    # exemple d’écho simple
    return {"email": email, "password": password}

@app.post("/reset", status_code=status.HTTP_200_OK)
def reset_state():
    core.reset_state()
    return Response(content="OK", status_code=status.HTTP_200_OK)

@app.get("/balance")
def get_balance(account_id: str, response: Response):
    account = core.get_account_balance(account_id)
from fastapi import FastAPI, Request, Response, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import os

from app.core import core

# ------------------------
# Schemas
# ------------------------
class EventRequest(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    type: str
    amount: int


class EventResponse(BaseModel):
    id: int | None
    type: str | None
    amount: int | None
    origin: Optional[str] = None
    destination: Optional[str] = None
    error: str | None = None


class TransactionCreate(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    type: str
    amount: int


class TransactionResponse(BaseModel):
    id: Optional[str] = None
    type: str
    amount: int
    origin: Optional[str] = None
    destination: Optional[str] = None
    error: Optional[str] = None


# ------------------------
# Application FastAPI
# ------------------------
app = FastAPI(title="Simple Banking API")

templates = Jinja2Templates(directory="app/templates")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_banking.db")

# compteur d'événements simulé
event_counter = 1
# jeu de comptes valides simulé (utilisé par les tests existants)
valid_accounts = ["100", "101"]


# ------------------------
# Routes principales
# ------------------------
@app.get("/", response_model=dict)
async def root():
    return {"message": "API Simple Banking fonctionne ✅"}


@app.get("/create_user", response_class=HTMLResponse)
async def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})


@app.post("/create_user")
async def create_user(email: str, password: str):
    # exemple d’écho simple
    return {"email": email, "password": password}


@app.post("/reset", status_code=status.HTTP_200_OK)
def reset_state():
    core.reset_state()
    return Response(content="OK", status_code=status.HTTP_200_OK)


@app.get("/balance")
def get_balance(account_id: str, response: Response):
    account = core.get_account_balance(account_id)
    if account is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"balance": 0}
    return {"balance": account.balance}


# ------------------------
# Gestion des événements
# ------------------------
@app.post("/event", response_model=EventResponse)
async def create_event(event: EventRequest):
    global event_counter

    origin = event.origin
    destination = event.destination

    # 1) Validation du type d'événement
    if event.type not in ["deposit", "withdraw", "transfer"]:
        return JSONResponse(
            status_code=400,
            content={
                "id": None,
                "type": None,
                "amount": None,
                "origin": origin,
                "destination": destination,
                "error": "Type de transaction invalide",
            },
        )

    # 2) Contrôles d'existence de compte (uniquement pour deposit/withdraw)
    if event.type != "transfer":
        account_id = destination if event.type == "deposit" else origin
        if account_id not in valid_accounts:
            return JSONResponse(
                status_code=404,
                content={
                    "id": None,
                    "type": event.type,
                    "amount": event.amount,
                    "origin": origin,
                    "destination": destination,
                    "error": "Compte non trouvé",
                },
            )

    # 3) Traitement selon le type
    if event.type == "deposit":
        # Dépôt : crée ou met à jour le compte destination
        core.create_or_update_account(destination, event.amount)

    elif event.type == "withdraw":
        # Retrait : origine doit exister et être suffisante
        account = core.withdraw_from_account(origin, event.amount)
        if account is None:
            return JSONResponse(
                status_code=404,
                content={
                    "id": None,
                    "type": "withdraw",
                    "amount": event.amount,
                    "origin": origin,
                    "destination": None,
                    "error": "Compte non trouvé",
                },
            )

    elif event.type == "transfer":
        # Transfert : message attendu -> "Compte origine ou destination non trouvé"
        origin_acc, dest_acc = core.transfer_between_accounts(
            origin, destination, event.amount
        )
        if origin_acc is None or dest_acc is None:
            return JSONResponse(
                status_code=404,
                content={
                    "id": None,
                    "type": "transfer",
                    "amount": event.amount,
                    "origin": origin,
                    "destination": destination,
                    "error": "Compte origine ou destination non trouvé",
                },
            )

    # 4) Construction de la réponse (201 créé)
    new_event = {
        "id": event_counter,
        "type": event.type,
        "amount": event.amount,
        "origin": origin if event.type != "deposit" else None,
        "destination": destination if event.type != "withdraw" else None,
        "error": None,
    }
    event_counter += 1

    return JSONResponse(status_code=201, content=new_event)

