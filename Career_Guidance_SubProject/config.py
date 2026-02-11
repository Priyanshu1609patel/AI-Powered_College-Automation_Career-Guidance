import os

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres.sjvzrzqzftixopjgiuos:priyanshu552@aws-1-ap-south-1.pooler.supabase.com:5432/postgres'
)
SECRET_KEY = 'your_super_secret_key_123'
