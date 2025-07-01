# Utilise une image officielle de Python
FROM python:3.10-slim

# Définit le dossier de travail
WORKDIR /app

# Copie les fichiers nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste du code
COPY src/ .

# Lance l’application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

