# ── Base image ─────────────────────────────────────────────────────────────────
FROM python:3.13-slim

# ── Variables d'environnement ──────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# ── Répertoire de travail ──────────────────────────────────────────────────────
WORKDIR /app

# ── Dépendances système (LightGBM a besoin de libgomp) ────────────────────────
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ── Dépendances Python ─────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Copie du code source ───────────────────────────────────────────────────────
COPY app/ ./app/
COPY src/ ./src/
COPY data/ ./data/
COPY .streamlit/ ./.streamlit/

# ── Créer les dossiers de données nécessaires ─────────────────────────────────
RUN mkdir -p data/records data/tracking

# ── Port exposé ────────────────────────────────────────────────────────────────
EXPOSE 8501

# ── Healthcheck ────────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# ── Lancement ──────────────────────────────────────────────────────────────────
CMD ["streamlit", "run", "app/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]