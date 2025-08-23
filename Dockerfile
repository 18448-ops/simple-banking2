# Utilise une image officielle de Python
FROM python:3.10-slim

# Définit le dossier de travail
WORKDIR /app

# Met à jour les paquets Debian et installe les dépendances système essentielles
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential gcc libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copie le fichier des dépendances Python
COPY requirements.txt .

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste du code source
COPY src/ .

# Expose le port de l'application
EXPOSE 8000

# Lance l’application FastAPI avec uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

