from sqlalchemy.orm import Session
from ..models import Account, Transaction
from ..database import SessionLocal

# Fonctions utilitaires pour gérer les comptes en DB

def reset_state():
    db = SessionLocal()
    try:
        db.query(Transaction).delete()
        db.query(Account).delete()
        db.commit()
    finally:
        db.close()

def get_account_balance(account_id: str):
    db = SessionLocal()
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        return account
    finally:
        db.close()

def create_or_update_account(account_id: str, amount: int):
    db = SessionLocal()
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if account:
            account.balance += amount
        else:
            account = Account(id=account_id, balance=amount)
            db.add(account)
        db.commit()
        db.refresh(account)
        return account
    finally:
        db.close()

def withdraw_from_account(account_id: str, amount: int):
    db = SessionLocal()
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account or account.balance < amount:
            return None
        account.balance -= amount
        db.commit()
        db.refresh(account)
        return account
    finally:
        db.close()

def transfer_between_accounts(origin: str, destination: str, amount: int):
    db = SessionLocal()
    try:
        origin_acc = db.query(Account).filter(Account.id == origin).first()
        if not origin_acc or origin_acc.balance < amount:
            return None, None

        origin_acc.balance -= amount

        dest_acc = db.query(Account).filter(Account.id == destination).first()
        if not dest_acc:
            dest_acc = Account(id=destination, balance=0)
            db.add(dest_acc)

        dest_acc.balance += amount

        db.commit()
        db.refresh(origin_acc)
        db.refresh(dest_acc)
        return origin_acc, dest_acc
    finally:
        db.close()

