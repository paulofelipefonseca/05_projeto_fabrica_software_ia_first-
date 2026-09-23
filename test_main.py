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


def test_read_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Página de Captura" in response.text
    assert "<form id=\"leadForm\"" in response.text


def test_create_lead_success(client):
    payload = {
        "name": "João Silva",
        "email": "joao.silva@example.com",
        "phone": "(11) 99999-8888",
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "João Silva"
    assert data["email"] == "joao.silva@example.com"
    assert data["phone"] == "11999998888"  # Must check if formatting/cleaning applied correctly
    assert data["consent"] is True
    assert "ip_address" in data


def test_create_lead_duplicate_email(client):
    payload = {
        "name": "Ana Souza",
        "email": "ana.souza@example.com",
        "phone": "11988887777",
        "consent": True
    }
    
    # First creation should succeed
    response_first = client.post("/leads", json=payload)
    assert response_first.status_code == 201

    # Second creation with same email should fail
    response_duplicate = client.post("/leads", json=payload)
    assert response_duplicate.status_code == 422
    assert response_duplicate.json()["detail"] == "Este e-mail já está cadastrado no sistema."


def test_create_lead_invalid_email(client):
    payload = {
        "name": "Carlos Santos",
        "email": "invalid-email-format",
        "phone": "11977776666",
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    
    errors = response.json()["detail"]
    assert any("O e-mail fornecido não é válido." in err["msg"] for err in errors)


def test_create_lead_invalid_phone(client):
    payload = {
        "name": "Mariana Lima",
        "email": "mariana@example.com",
        "phone": "12345",  # Too short
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    
    errors = response.json()["detail"]
    assert any("O telefone deve conter DDD e de 8 a 9 dígitos numéricos." in err["msg"] for err in errors)


def test_create_lead_missing_consent(client):
    payload = {
        "name": "Roberto Dias",
        "email": "roberto@example.com",
        "phone": "11966665555",
        "consent": False
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    
    errors = response.json()["detail"]
    assert any("É necessário aceitar os termos de consentimento." in err["msg"] for err in errors)


def test_list_leads_empty(client):
    response = client.get("/leads")
    assert response.status_code == 200
    assert response.json() == []


def test_list_leads_populated(client):
    # Insert multiple test leads
    leads_to_create = [
        {"name": "Lead Um", "email": "lead1@example.com", "phone": "11955554444", "consent": True},
        {"name": "Lead Dois", "email": "lead2@example.com", "phone": "11944443333", "consent": True}
    ]
    
    for lead in leads_to_create:
        res = client.post("/leads", json=lead)
        assert res.status_code == 201

    response = client.get("/leads")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["email"] == "lead1@example.com"
    assert data[1]["email"] == "lead2@example.com"