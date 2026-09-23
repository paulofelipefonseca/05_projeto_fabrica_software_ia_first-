import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from main import app, Base, engine

from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_create_lead_success(client):
    payload = {
        "nome": "João Silva",
        "email": "joao.silva@example.com",
        "telefone": "11999999999",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["nome"] == payload["nome"]
    assert data["email"] == payload["email"]
    assert data["telefone"] == payload["telefone"]  # Validação do campo de telefone conforme diretriz
    assert data["consentimento_lgpd"] is True
    assert "id" in data
    assert "criado_em" in data

def test_create_lead_duplicate_updates_existing(client):
    payload_initial = {
        "nome": "Carlos Souza",
        "email": "carlos@example.com",
        "telefone": "11988887777",
        "consentimento_lgpd": True
    }
    response_initial = client.post("/leads", json=payload_initial)
    assert response_initial.status_code == 201
    initial_data = response_initial.json()
    initial_id = initial_data["id"]

    # Atualiza o lead usando o mesmo e-mail (Prevenção de Duplicidade)
    payload_update = {
        "nome": "Carlos S. Souza",
        "email": "carlos@example.com",
        "telefone": "11977776666",
        "consentimento_lgpd": True
    }
    response_update = client.post("/leads", json=payload_update)
    assert response_update.status_code == 201
    
    updated_data = response_update.json()
    assert updated_data["id"] == initial_id
    assert updated_data["nome"] == "Carlos S. Souza"
    assert updated_data["telefone"] == "11977776666"

def test_list_leads(client):
    # Criar dois leads distintos
    lead_1 = {
        "nome": "Ana Oliveira",
        "email": "ana@example.com",
        "telefone": "11955554444",
        "consentimento_lgpd": True
    }
    lead_2 = {
        "nome": "Bruno Santos",
        "email": "bruno@example.com",
        "telefone": "21944443333",
        "consentimento_lgpd": True
    }
    client.post("/leads", json=lead_1)
    client.post("/leads", json=lead_2)

    response = client.get("/leads")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_get_lead_by_id(client):
    payload = {
        "nome": "Juliana Lima",
        "email": "juliana@example.com",
        "telefone": "31933332222",
        "consentimento_lgpd": True
    }
    create_response = client.post("/leads", json=payload)
    lead_id = create_response.json()["id"]

    response = client.get(f"/leads/{lead_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == lead_id
    assert data["nome"] == "Juliana Lima"
    assert data["telefone"] == "31933332222"

def test_get_lead_not_found(client):
    response = client.get("/leads/99999")
    assert response.status_code == 404

def test_validation_invalid_phone(client):
    payload = {
        "nome": "Roberto Alencar",
        "email": "roberto@example.com",
        "telefone": "123-abc",  # Telefone inválido
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422

def test_validation_missing_lgpd_consent(client):
    payload = {
        "nome": "Roberto Alencar",
        "email": "roberto@example.com",
        "telefone": "11922221111",
        "consentimento_lgpd": False  # Consentimento obrigatório
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422

def test_validation_short_name(client):
    payload = {
        "nome": "Ed",  # Menor que o mínimo de 3 caracteres
        "email": "ed@example.com",
        "telefone": "11911110000",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422

def test_validation_invalid_email(client):
    payload = {
        "nome": "Eduardo Ramos",
        "email": "eduardo-invalid-email",  # Email inválido
        "telefone": "11911110000",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422