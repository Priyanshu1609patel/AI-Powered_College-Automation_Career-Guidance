import os

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres.sjvzrzqzftixopjgiuos:priyanshu552@aws-1-ap-south-1.pooler.supabase.com:5432/postgres'
)
SECRET_KEY = 'your_super_secret_key_123'

# Supabase Storage Config
SUPABASE_URL = 'https://sjvzrzqzftixopjgiuos.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNqdnpyenF6ZnRpeG9wamdpdW9zIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNjkzNTk3NywiZXhwIjoyMDUyNTExOTc3fQ.6wGJ5wZ_EYqVYxGqH0FqH0FqH0FqH0FqH0FqH0FqH0E'
SUPABASE_BUCKET = 'user_logo'
SUPABASE_BUCKET = 'user_logo'
