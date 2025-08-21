from fastapi import FastAPI, Request, status, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .models import Transaction, Account
from .schemas import TransactionCreate, TransactionResponse
from .core import core
import os

app = FastAPI()

# Configuration templates
templates = Jinja2Templates(directory="app/templates")

# Détection de l'environnement pour la DB
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_banking.db")
core.init_database(DATABASE_URL)  # Assure que core gère la DB correctement


@app.get("/", response_model=dict)
async def root():
    return {"message": "API Simple Banking fonctionne ✅"}


@app.get("/create_user", response_class=HTMLResponse)
async def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})


@app.post("/create_user")
async def create_user(email: str, password: str):
    # Logique d'ajout utilisateur (à implémenter)
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


@app.post("/event", status_code=201, response_model=TransactionResponse)
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
        id=str(account.id),
        type="deposit",
        amount=transaction.amount,
        destination=str(account.id)
    )


def process_withdraw(transaction: TransactionCreate, response: Response):
    account = core.withdraw_from_account(transaction.origin, transaction.amount)
    if account is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Compte non trouvé"}
    return TransactionResponse(
        id=str(account.id),
        type="withdraw",
        amount=transaction.amount,
        destination=str(account.id)
    )


def process_transfer(transaction: TransactionCreate, response: Response):
    origin, destination = core.transfer_between_accounts(
        transaction.origin, transaction.destination, transaction.amount
    )
    if origin is None or destination is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Compte origine ou destination non trouvé"}
    return TransactionResponse(
        id=str(origin.id),
        type="transfer",
        amount=transaction.amount,
        destination=str(destination.id)
    )

