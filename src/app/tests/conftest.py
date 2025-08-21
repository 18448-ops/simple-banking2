import pytest
from app.database import Base, engine

@pytest.fixture(scope="function", autouse=True)
def prepare_db():
    """
    Cette fixture s'exécute avant chaque test pour réinitialiser la base SQLite.
    Elle supprime toutes les tables et les recrée.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
