# app/models/schemas.py

from pydantic import BaseModel
from typing import Optional

class Transaction(BaseModel):
    type: str
    amount: int
    origin: Optional[str] = None
    destination: Optional[str] = None
