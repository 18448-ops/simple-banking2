from pydantic import BaseModel
from typing import Optional

# Schéma pour la création d'une transaction
class TransactionCreate(BaseModel):
    type: str
    amount: int
    origin: Optional[str] = None
    destination: Optional[str] = None

# Schéma pour la réponse d'une transaction
class TransactionResponse(BaseModel):
    id: str            # id du compte impliqué
    type: str
    amount: int
    destination: str   # id du compte destination

    class Config:
        orm_mode = True

