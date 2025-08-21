from typing import Optional, Tuple
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Account, Transaction, Base

# Engine et session globale
engine = None
SessionLocal = None

def init_database(database_url: str):
    """
    Initialise la base de données et crée les tables si nécessaire.
    """
    global engine, SessionLocal
    engine = create_engine(database_url, connect_args={"check_same_thread": False} if "sqlite" in database_url else {})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


def reset_state():
    """
    Réinitialise tous les comptes et transactions (utile pour tests).
    """
    session: Session = SessionLocal()
    session.query(Transaction).delete()
    session.query(Account).delete()
    session.commit()
    session.close()


def get_account_balance(account_id: str) -> Optional[Account]:
    session: Session = SessionLocal()
    account = session.query(Account).filter(Account.id == account_id).first()
    session.close()
    return account


def create_or_update_account(account_id: str, amount: int) -> Account:
    session: Session = SessionLocal()
    account = session.query(Account).filter(Account.id == account_id).first()
    if account:
        account.balance += amount
    else:
        account = Account(id=account_id, balance=amount)
        session.add(account)
    # Enregistrement de la transaction
    session.add(Transaction(type="deposit", amount=amount, destination=account_id))
    session.commit()
    session.refresh(account)
    session.close()
    return account


def withdraw_from_account(account_id: str, amount: int) -> Optional[Account]:
    session: Session = SessionLocal()
    account = session.query(Account).filter(Account.id == account_id).first()
    if not account or account.balance < amount:
        session.close()
        return None
    account.balance -= amount
    session.add(Transaction(type="withdraw", amount=amount, origin=account_id))
    session.commit()
    session.refresh(account)
    session.close()
    return account


def transfer_between_accounts(origin_id: str, destination_id: str, amount: int) -> Tuple[Optional[Account], Optional[Account]]:
    session: Session = SessionLocal()
    origin = session.query(Account).filter(Account.id == origin_id).first()
    if not origin or origin.balance < amount:
        session.close()
        return None, None

    destination = session.query(Account).filter(Account.id == destination_id).first()
    if not destination:
        destination = Account(id=destination_id, balance=0)
        session.add(destination)

    origin.balance -= amount
    destination.balance += amount

    # Enregistrement de la transaction
    session.add(Transaction(type="transfer", amount=amount, origin=origin_id, destination=destination_id))
    session.commit()
    session.refresh(origin)
    session.refresh(destination)
    session.close()
    return origin, destination

