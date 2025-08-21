from typing import Optional, Dict
from ..models import Account

accounts: Dict[str, Account] = {}

def reset_state():
    accounts.clear()

def get_account_balance(account_id: str) -> Optional[Account]:
    return accounts.get(account_id)

def create_or_update_account(account_id: str, amount: int) -> Account:
    if account_id in accounts:
        accounts[account_id].balance += amount
    else:
        accounts[account_id] = Account(id=account_id, balance=amount)
    return accounts[account_id]

def withdraw_from_account(account_id: str, amount: int) -> Optional[Account]:
    account = accounts.get(account_id)
    if not account or account.balance < amount:
        return None
    account.balance -= amount
    return account

def transfer_between_accounts(origin: str, destination: str, amount: int) -> (Optional[Account], Optional[Account]):
    origin_acc = accounts.get(origin)
    if not origin_acc or origin_acc.balance < amount:
        return None, None

    origin_acc.balance -= amount

    dest_acc = accounts.get(destination)
    if not dest_acc:
        dest_acc = Account(id=destination, balance=0)
        accounts[destination] = dest_acc

    dest_acc.balance += amount

    return origin_acc, dest_acc

