import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from main import app, Base, engine

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_lead_success(client):
    payload = {
        "nome_completo": "Ana Souza",
        "email": "ana.souza@example.com",
        "telefone": "11987654321",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["nome_completo"] == "Ana Souza"
    assert data["email"] == "ana.souza@example.com"
    assert data["telefone"] == "11987654321"
    assert data["consentimento_lgpd"] is True
    assert "data_criacao" in data
    assert "data_atualizacao" in data

def test_create_lead_updates_existing(client):
    payload1 = {
        "nome_completo": "Carlos Silva",
        "email": "carlos.silva@example.com",
        "telefone": "11999999999",
        "consentimento_lgpd": True
    }
    response1 = client.post("/leads", json=payload1)
    assert response1.status_code == 201
    initial_data = response1.json()

    payload2 = {
        "nome_completo": "Carlos Silva Atualizado",
        "email": "carlos.silva@example.com",
        "telefone": "11988888888",
        "consentimento_lgpd": True
    }
    response2 = client.post("/leads", json=payload2)
    assert response2.status_code == 200
    updated_data = response2.json()
    
    assert updated_data["id"] == initial_data["id"]
    assert updated_data["nome_completo"] == "Carlos Silva Atualizado"
    assert updated_data["telefone"] == "11988888888"

def test_create_lead_invalid_phone(client):
    payload = {
        "nome_completo": "João Silva",
        "email": "joao@example.com",
        "telefone": "12345",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    assert "O telefone deve conter entre 10 e 11 dígitos numéricos" in response.text

def test_create_lead_no_consent(client):
    payload = {
        "nome_completo": "Maria Silva",
        "email": "maria@example.com",
        "telefone": "11999999999",
        "consentimento_lgpd": False
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    assert "O consentimento para uso de dados (LGPD) é obrigatório." in response.text

def test_create_lead_invalid_email(client):
    payload = {
        "nome_completo": "Pedro Santos",
        "email": "pedro-invalid-email",
        "telefone": "11999999999",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    assert "Formato de e-mail inválido." in response.text

def test_create_lead_name_too_short(client):
    payload = {
        "nome_completo": "J",
        "email": "j@example.com",
        "telefone": "11999999999",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422

def test_list_leads_empty(client):
    response = client.get("/leads")
    assert response.status_code == 200
    assert response.json() == []

def test_list_leads_multiple(client):
    lead1 = {
        "nome_completo": "Lead Um",
        "email": "lead1@example.com",
        "telefone": "11911111111",
        "consentimento_lgpd": True
    }
    lead2 = {
        "nome_completo": "Lead Dois",
        "email": "lead2@example.com",
        "telefone": "11922222222",
        "consentimento_lgpd": True
    }
    client.post("/leads", json=lead1)
    client.post("/leads", json=lead2)

    response = client.get("/leads")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["email"] == "lead1@example.com"
    assert data[1]["email"] == "lead2@example.com"