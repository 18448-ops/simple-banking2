from sqlalchemy import Column, Integer, String
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    password = Column(String, nullable=False)

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)
    balance = Column(Integer, default=0)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    origin = Column(String, nullable=True)
    destination = Column(String, nullable=True)

