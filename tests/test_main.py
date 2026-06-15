import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, SessionLocal
from app.main import app, sessao_db
import httpx

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_records.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_sessao_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Injeta a sessao de testes com a nomenclatura do professor
app.dependency_overrides[sessao_db] = override_sessao_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    from app.main import CACHE_LOCAL
    CACHE_LOCAL.clear()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_get_pokemon_success(helper_mock_pokeapi):
    # Envia as credenciais no formato HTTP Basic (admin:admin) exigido pela rota
    response = client.get("/pokemons/25", auth=("admin", "admin"))
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 25
    assert data["name"] == "pikachu"

def test_get_pokemon_not_found(helper_mock_pokeapi_404):
    response = client.get("/pokemons/9999", auth=("admin", "admin"))
    assert response.status_code == 404

def test_get_pokemons_pagination_structure(helper_mock_pokeapi):
    client.get("/pokemons/25", auth=("admin", "admin"))
    response = client.get("/pokemons?limit=10&offset=0", auth=("admin", "admin"))
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert "pagination" in json_data

@pytest.fixture
def helper_mock_pokeapi(monkeypatch):
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "id": 25, "name": "pikachu", "height": 4, "weight": 60,
                "types": [{"type": {"name": "electric"}}],
                "sprites": {"front_default": "url_front", "back_default": "url_back"}
            }
        def raise_for_status(self):
            pass
    async def mock_get(*args, **kwargs):
        return MockResponse()
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

@pytest.fixture
def helper_mock_pokeapi_404(monkeypatch):
    class MockResponse404:
        status_code = 404
        def raise_for_status(self):
            pass
    async def mock_get(*args, **kwargs):
        return MockResponse404()
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)