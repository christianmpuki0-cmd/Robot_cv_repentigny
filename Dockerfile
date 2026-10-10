# Utilisation de l'image officielle Playwright avec Python pré-installé
FROM ://microsoft.com

# Définition du répertoire de travail
WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du reste du code de l'application
COPY . .

# Commande pour lancer le bot
CMD ["python", "bot_repentigny.py"]
