from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.schemas import EventResponse
from fastapi import FastAPI, Request, status, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.models import Transaction, Account
from app.schemas import TransactionCreate, TransactionResponse
from app.core import core
from pydantic import BaseModel
import os

class EventRequest(BaseModel):
    origin: str
    type: str
    amount: int

class EventResponse(BaseModel):
    id: int | None
    type: str | None
    amount: int | None
    error: str | None = None

app = FastAPI(title="Simple Banking API")

templates = Jinja2Templates(directory="app/templates")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_banking.db")
# La DB est initialisée via les models et SQLAlchemy Base.metadata.create_all ailleurs

@app.get("/", response_model=dict)
async def root():
    return {"message": "API Simple Banking fonctionne ✅"}

@app.get("/create_user", response_class=HTMLResponse)
async def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

@app.post("/create_user")
async def create_user(email: str, password: str):
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

@app.post("/event", response_model=EventResponse)
async def create_event(event: EventRequest):
    origin = event.origin
    event_type = event.type
    amount = event.amount

    # Vérification si le compte existe
    if origin not in ["100", "101"]:
        return JSONResponse(
            status_code=404,
            content={"id": None, "type": None, "amount": None, "error": "Compte non trouvé"})

    # Exemple de création d'un événement
    new_event_id = 1
    return JSONResponse(
        status_code=201,
        content={"id": new_event_id, "type": event_type, "amount": amount, "error": None})
def post_event(transaction: TransactionCreate, response: Response):
    strategy_map = {
        "deposit": process_deposit,
        "withdraw": process_withdraw,
        "transfer": process_transfer,
    }

    process_func = strategy_map.get(transaction.type)
    if process_func is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Type de transaction invalide"}

    return process_func(transaction, response)

def process_deposit(transaction: TransactionCreate, response: Response):
    account = core.create_or_update_account(transaction.destination, transaction.amount)
    return TransactionResponse(
        id=account.id,
        type="deposit",
        amount=transaction.amount,
        origin=None,
        destination=account.id
    )

def process_withdraw(transaction: TransactionCreate, response: Response):
    account = core.withdraw_from_account(transaction.origin, transaction.amount)
    if account is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Compte non trouvé"}
    return TransactionResponse(
        id=account.id,
        type="withdraw",
        amount=transaction.amount,
        origin=account.id,
        destination=None
    )

def process_transfer(transaction: TransactionCreate, response: Response):
    origin, destination = core.transfer_between_accounts(
        transaction.origin, transaction.destination, transaction.amount
    )
    if origin is None or destination is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Compte origine ou destination non trouvé"}
    return TransactionResponse(
        id=origin.id,
        type="transfer",
        amount=transaction.amount,
        origin=origin.id,
        destination=destination.id
    )

