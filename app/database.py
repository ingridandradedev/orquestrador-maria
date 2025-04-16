import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Parâmetros do pooler
DB_HOST = "aws-0-sa-east-1.pooler.supabase.com"
DB_PORT = 6543
DB_NAME = "postgres"
DB_USER = "postgres.sxzgjdqxmsdgfqjvzwak"
DB_PASSWORD = ".vFVC29KtuY%YH2"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Número máximo de conexões no pool
    max_overflow=5,  # Número máximo de conexões extras
    pool_timeout=30,  # Tempo limite para obter uma conexão
    pool_pre_ping=True  # Verifica se a conexão está ativa antes de usá-la
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()