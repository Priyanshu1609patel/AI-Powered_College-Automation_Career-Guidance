# ── Production Image ──────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# System deps needed at runtime
# - build-essential: C extensions (spacy, psycopg2 compile steps)
# - libpq-dev: PostgreSQL client lib for psycopg2-binary runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages first — cached layer, only rebuilds when requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir "gunicorn==23.0.0"

# Download spaCy model used by resume_parser/parser.py
# Install directly from GitHub releases to avoid spacy download URL resolution issues
RUN pip install --no-cache-dir \
    https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Copy project source (venv/, .env, __pycache__ etc. excluded via .dockerignore)
COPY . .

# Ensure upload directories exist for both apps
RUN mkdir -p uploads Career_Guidance_SubProject/uploads

EXPOSE 5000

# Gunicorn (production WSGI server) serves the DispatcherMiddleware from run.py
# run:application  →  both Flask apps (main + /Career_Guidance_SubProject)
# 2 workers × 2 threads = handles 4 concurrent requests with low memory
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "run:application"]
