# 1. On part d'une version légère de Python (Linux)
FROM python:3.11-slim

# 2. On empêche Python de garder des fichiers cache inutiles
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. On crée un dossier de travail dans le conteneur
WORKDIR /app

# 4. On installe les outils système nécessaires (pour SQLite et GCC)
RUN apt-get update && apt-get install -y \
    gcc \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. On copie la liste des librairies et on les installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. On copie tout votre code dans le conteneur
COPY . .

# 7. On dit à Docker que le port 8000 sera utilisé
EXPOSE 8000

# 8. Commande de démarrage par défaut (Lance l'API)
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]