from pydantic import BaseModel
from typing import Optional

class EventResponse(BaseModel):
    id: Optional[int]  # None si l'opération a échoué
    type: Optional[str]  # None si l'opération a échoué
    amount: Optional[float]  # None si l'opération a échoué
    error: Optional[str] = None

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

