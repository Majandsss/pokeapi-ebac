import os
import json
import time
import logging
import secrets
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import httpx

# Bibliotecas extras para os bônus (Rate Limiting)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database import Base, engine, SessionLocal
from app.models import PokemonModel
from app.schemas import PaginatedPokemonResponse, PokemonResponse, PokemonSprites

load_dotenv_r = os.path.exists(".env")
if load_dotenv_r:
    from dotenv import load_dotenv
    load_dotenv()

# --- LOGS ESTRUTURADOS EM JSON ---
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_object = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }
        return json.dumps(log_object)

logger = logging.getLogger("fastapi")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(JSONFormatter())
logger.addHandler(ch)

# --- EXTRA: RATE LIMITING ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Sua PokéAPI Completa - EBAC")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- EXTRA: CACHE EM MEMÓRIA ---
CACHE_LOCAL = {}
CACHE_EXPIRATION_SECONDS = 300

# --- AUTENTICAÇÃO VIA HTTP BASIC ---
MEU_USUARIO = os.getenv("MEU_USUARIO")
MINHA_SENHA = os.getenv("MINHA_SENHA")

if not MEU_USUARIO or not MINHA_SENHA:
    logger.warning("ATENÇÃO: Variáveis de ambiente MEU_USUARIO ou MINHA_SENHA não foram configuradas!")

security = HTTPBasic()

def autenticar_meu_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, MEU_USUARIO)
    is_password_correct = secrets.compare_digest(credentials.password, MINHA_SENHA)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Usuário não autorizado! Credenciais inválidas!",
            headers={"WWW-Authenticate": "Basic"}
        )
    return credentials

# --- EXTRA: TRATAMENTO DE EXCEÇÃO PERSONALIZADO ---
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"Erro capturado na rota {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "detail": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )

# Cria as tabelas do SQLite automaticamente
Base.metadata.create_all(bind=engine)

# --- GEREANCIADOR DE SESSÃO DO BANCO ---
def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon"

async def fetch_from_pokeapi(pokemon_id: int) -> PokemonModel:
    current_time = time.time()
    if pokemon_id in CACHE_LOCAL:
        cache_data, timestamp = CACHE_LOCAL[pokemon_id]
        if current_time - timestamp < CACHE_EXPIRATION_SECONDS:
            logger.info(f"Cache Hit em memoria para o Pokemon ID: {pokemon_id}")
            return cache_data

    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Buscando Pokemon ID {pokemon_id} na PokeAPI externa...")
            response = await client.get(f"{POKEAPI_URL}/{pokemon_id}")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Pokémon não encontrado na PokéAPI original.")
            response.raise_for_status()
        except httpx.HTTPError:
            raise HTTPException(status_code=502, detail="Erro ao se comunicar com a PokéAPI externa.")
        
        raw_data = response.json()
        types_list = [t["type"]["name"] for t in raw_data["types"]]
        
        pokemon = PokemonModel(
            id=pokemon_id,
            name=raw_data["name"],
            height=raw_data["height"],
            weight=raw_data["weight"],
            types=",".join(types_list),
            front_default=raw_data["sprites"]["front_default"],
            back_default=raw_data["sprites"]["back_default"]
        )
        
        CACHE_LOCAL[pokemon_id] = (pokemon, current_time)
        return pokemon

# Endpoint 1: Detalhes Protegido por Basic Auth
@app.get("/pokemons/{id}", response_model=PokemonResponse)
@limiter.limit("5/minute")
async def get_pokemon_by_id(
    request: Request, 
    id: int, 
    db: Session = Depends(sessao_db), 
    usuario: HTTPBasicCredentials = Depends(autenticar_meu_usuario)
):
    pokemon = db.query(PokemonModel).filter(PokemonModel.id == id).first()
    
    if not pokemon:
        pokemon = await fetch_from_pokeapi(id)
        db.add(pokemon)
        db.commit()
        db.refresh(pokemon)
        
    return PokemonResponse(
        id=pokemon.id,
        name=pokemon.name,
        height=pokemon.height,
        weight=pokemon.weight,
        types=pokemon.types.split(","),
        sprites=PokemonSprites(front_default=pokemon.front_default, back_default=pokemon.back_default)
    )

# Endpoint 2: Listagem Paginada Protegida por Basic Auth
@app.get("/pokemons", response_model=PaginatedPokemonResponse)
@limiter.limit("10/minute")
def get_pokemons(
    request: Request,
    limit: int = Query(default=20, ge=1),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(sessao_db),
    usuario: HTTPBasicCredentials = Depends(autenticar_meu_usuario)
):
    total_records = db.query(PokemonModel).count()
    pokemons_db = db.query(PokemonModel).offset(offset).limit(limit).all()
    
    formatted_data = [
        PokemonResponse(
            id=p.id,
            name=p.name,
            height=p.height,
            weight=p.weight,
            types=p.types.split(","),
            sprites=PokemonSprites(front_default=p.front_default, back_default=p.back_default)
        )
        for p in pokemons_db
    ]
    
    base_url = "/pokemons"
    next_url = f"{base_url}?limit={limit}&offset={offset + limit}" if (offset + limit) < total_records else None
    prev_offset = max(0, offset - limit)
    previous_url = f"{base_url}?limit={limit}&offset={prev_offset}" if offset > 0 else None

    logger.info(f"Listagem acessada por {usuario.username}. Registros locais: {total_records}")

    return PaginatedPokemonResponse(
        data=formatted_data,
        pagination={
            "total": total_records,
            "limit": limit,
            "offset": offset,
            "next": next_url,
            "previous": previous_url
        }
    )