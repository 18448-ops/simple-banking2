from pydantic import BaseModel
from typing import Optional

class TransactionBase(BaseModel):
    type: str
    amount: int
    origin: Optional[str] = None
    destination: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: str  # correspond à l'ID du compte pour deposit/withdraw/transfer

    class Config:
        orm_mode = True

