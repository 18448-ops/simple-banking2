import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Détection de l'environnement
# Possible values: "dev" (par défaut), "prod", "test"
ENV = os.getenv("ENVIRONMENT", "dev")

if ENV == "test":
    # SQLite pour les tests
    DATABASE_URL = "sqlite:///./test_banking.db"
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL pour dev/prod
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:admin@localhost/banking"
    )
    engine = create_engine(DATABASE_URL)

# Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour les modèles ORM
Base = declarative_base()

