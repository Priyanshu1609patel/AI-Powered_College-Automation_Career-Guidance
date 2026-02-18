import os
from dotenv import load_dotenv

load_dotenv()

# --- Database (Supabase PostgreSQL via psycopg2) ---
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:priyanshu552@db.sjvzrzqzftixopjgiuos.supabase.co:5432/postgres'
)

# --- Supabase REST (used by career guidance sub-module) ---
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://sjvzrzqzftixopjgiuos.supabase.co')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
SUPABASE_BUCKET = 'user_logo'

# --- Flask ---
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production-use-random-bytes')
DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
