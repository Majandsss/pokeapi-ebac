import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carrega as variáveis do arquivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback de segurança caso o sistema não leia o .env no Windows
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./pokemons.db"

# O argumento 'check_same_thread=False' é obrigatório para o SQLite trabalhar com o FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Função que abre uma sessão do banco para a rota usar e fecha quando a requisição termina
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()