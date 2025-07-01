from app.database import Base, engine
from app.models.models import User, Account, Transaction

# Crée toutes les tables dans la base si elles n'existent pas
Base.metadata.create_all(bind=engine)

print("✅ Tables créées avec succès dans la base 'banking'.")
