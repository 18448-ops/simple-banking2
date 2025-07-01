from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, status, Response
from .models import Transaction
from .schemas import TransactionCreate, TransactionResponse
from .core import core

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is up and running!"}

# Configure Jinja2 templates
templates = Jinja2Templates(directory="app/templates")
# Route pour afficher le formulaire de création d'utilisateur
@app.get("/create_user", response_class=HTMLResponse)
async def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

# Route POST pour soumettre le formulaire de création d'utilisateur
@app.post("/create_user")
async def create_user(email: str, password: str):
    # Ici tu peux ajouter la logique pour enregistrer l'utilisateur dans ta base de données
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
        return 0
    return account.balance

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
        return response

    return process_func(transaction, response)

def process_deposit(transaction, response: Response):
    account = core.create_or_update_account(transaction.destination, transaction.amount)
    return {"destination": account}

def process_withdraw(transaction, response: Response):
    account = core.withdraw_from_account(transaction.origin, transaction.amount)
    if account is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return 0
    return {"origin": account}

def process_transfer(transaction, response: Response):
    origin, destination = core.transfer_between_accounts(transaction.origin, transaction.destination, transaction.amount)
    if origin is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return 0
    return {"origin": origin, "destination": destination}

@app.get("/")
def root():
    return {"message": "API Simple Banking fonctionne ✅"}
