import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal

client = TestClient(app)

# Fixture pour réinitialiser la base SQLite avant chaque test
@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Supprimer toutes les tables et les recréer
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Optionnel : nettoyage après le test
    Base.metadata.drop_all(bind=engine)


def create_account(account_id: str, amount: int):
    """Fonction utilitaire pour créer un compte avec un dépôt initial"""
    response = client.post("/event", json={"type": "deposit", "destination": account_id, "amount": amount})
    assert response.status_code == 201
    return response.json()


def test_get_balance_non_existing_account():
    response = client.get("/balance?account_id=1234")
    assert response.status_code == 404


def test_create_account_with_initial_balance():
    result = create_account("100", 10)
    assert result == {"destination": {"id": "100", "balance": 10}}


def test_deposit_into_existing_account():
    create_account("100", 10)
    result = create_account("100", 10)  # dépôt supplémentaire
    assert result == {"destination": {"id": "100", "balance": 20}}


def test_get_balance_existing_account():
    create_account("100", 20)
    response = client.get("/balance?account_id=100")
    assert response.status_code == 200
    assert response.json() == {"balance": 20}


def test_withdraw_from_non_existing_account():
    response = client.post("/event", json={"type": "withdraw", "origin": "200", "amount": 10})
    assert response.status_code == 404


def test_withdraw_from_existing_account():
    create_account("100", 20)
    response = client.post("/event", json={"type": "withdraw", "origin": "100", "amount": 5})
    assert response.status_code == 201
    assert response.json() == {"origin": {"id": "100", "balance": 15}}


def test_transfer_from_existing_account():
    create_account("100", 20)
    response = client.post("/event", json={"type": "transfer", "origin": "100", "amount": 15, "destination": "300"})
    assert response.status_code == 201
    assert response.json() == {"origin": {"id": "100", "balance": 5}, "destination": {"id": "300", "balance": 15}}


def test_transfer_from_non_existing_account():
    response = client.post("/event", json={"type": "transfer", "origin": "200", "amount": 15, "destination": "300"})
    assert response.status_code == 404

