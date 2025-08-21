import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def create_account(account_id: str, amount: int):
    response = client.post("/event", json={"type": "deposit", "destination": account_id, "amount": amount})
    assert response.status_code == 201
    return response.json()

def test_get_balance_non_existing_account():
    response = client.get("/balance?account_id=1234")
    assert response.status_code == 404

def test_create_account_with_initial_balance():
    result = create_account("100", 10)
    assert result["destination"] == "100"

def test_deposit_into_existing_account():
    create_account("100", 10)
    result = create_account("100", 10)
    assert result["destination"] == "100"

def test_get_balance_existing_account():
    create_account("100", 20)
    response = client.get("/balance?account_id=100")
    assert response.status_code == 200
    assert response.json() == {"balance": 20}

def test_withdraw_from_non_existing_account():
    response = client.post("/event", json={"type": "withdraw", "origin": "200", "amount": 10})
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Compte non trouvé"
    assert data["id"] is None
    assert data["type"] is None
    assert data["amount"] is None

def test_withdraw_from_existing_account():
    create_account("100", 20)
    response = client.post("/event", json={"type": "withdraw", "origin": "100", "amount": 5})
    assert response.status_code == 201
    assert response.json()["origin"] == "100"
    assert response.json()["amount"] == 5

def test_transfer_from_existing_account_to_existing_account():
    create_account("100", 20)
    create_account("101", 10)
    response = client.post("/event", json={"type": "transfer", "origin": "100", "destination": "101", "amount": 15})
    assert response.status_code == 201
    data = response.json()
    assert data["origin"] == "100"
    assert data["destination"] == "101"
    assert data["amount"] == 15

def test_transfer_from_non_existing_account():
    create_account("101", 10)
    response = client.post("/event", json={"type": "transfer", "origin": "200", "destination": "101", "amount": 15})
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Compte origine ou destination non trouvé"

