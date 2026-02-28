import os
from dotenv import load_dotenv

# Load .env from parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres.sjvzrzqzftixopjgiuos:priyanshu552@aws-1-ap-south-1.pooler.supabase.com:5432/postgres'
)
SECRET_KEY = os.getenv('SECRET_KEY', 'your_super_secret_key_123')

# Supabase Storage Config
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://sjvzrzqzftixopjgiuos.supabase.co')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
SUPABASE_BUCKET = 'user_logo'
