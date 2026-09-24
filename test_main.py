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

def test_create_lead_success(client):
    payload = {
        "name": "João Silva",
        "email": "joao.silva@example.com",
        "phone": "11999998888",
        "company": "Tech Innovators",
        "role": "Software Engineer",
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["phone"] == payload["phone"]
    assert data["company"] == payload["company"]
    assert data["role"] == payload["role"]
    assert data["consent"] is True

def test_create_lead_duplicate_email(client):
    payload = {
        "name": "Maria Souza",
        "email": "maria.souza@example.com",
        "phone": "11988887777",
        "company": "Design Co",
        "role": "Product Designer",
        "consent": True
    }
    # Criar o primeiro lead
    response_first = client.post("/leads", json=payload)
    assert response_first.status_code == 201

    # Tentar criar o segundo lead com o mesmo e-mail
    response_duplicate = client.post("/leads", json=payload)
    assert response_duplicate.status_code == 422
    assert response_duplicate.json()["detail"] == "Este e-mail já foi cadastrado para outra oferta."

def test_create_lead_missing_consent(client):
    payload = {
        "name": "Pedro Santos",
        "email": "pedro.santos@example.com",
        "phone": "11977776666",
        "company": "Finance Inc",
        "role": "Analyst",
        "consent": False
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    
    # Valida se a mensagem de erro de consentimento disparou no Pydantic
    errors = response.json()["detail"]
    assert any("O consentimento dos termos de privacidade (LGPD) é obrigatório." in err["msg"] for err in errors)

def test_create_lead_invalid_phone(client):
    payload = {
        "name": "Ana Costa",
        "email": "ana.costa@example.com",
        "phone": "1234-abc",
        "company": "Consulting Ltd",
        "role": "Manager",
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    
    # Valida se a mensagem de erro de telefone disparou no Pydantic
    errors = response.json()["detail"]
    assert any("Formato de telefone inválido. Insira um número válido com DDD." in err["msg"] for err in errors)

def test_create_lead_invalid_email_format(client):
    payload = {
        "name": "Lucas Lima",
        "email": "lucas.lima.invalid.com",
        "phone": "11966665555",
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    
    errors = response.json()["detail"]
    assert any("value is not a valid email address" in err["msg"].lower() for err in errors)

def test_list_leads_empty(client):
    response = client.get("/leads")
    assert response.status_code == 200
    assert response.json() == []

def test_list_leads_with_records(client):
    lead_1 = {
        "name": "Lead Um",
        "email": "lead1@teste.com",
        "phone": "11955554444",
        "consent": True
    }
    lead_2 = {
        "name": "Lead Dois",
        "email": "lead2@teste.com",
        "phone": "21944443333",
        "consent": True
    }
    
    # Cadastra dois leads
    assert client.post("/leads", json=lead_1).status_code == 201
    assert client.post("/leads", json=lead_2).status_code == 201

    # Listar leads
    response = client.get("/leads")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["email"] == "lead1@teste.com"
    assert data[1]["email"] == "lead2@teste.com"