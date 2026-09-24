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
        "nome": "João Silva",
        "email": "joao.silva@email.com",
        "telefone": "(11) 99999-9999",
        "aceitou_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["nome"] == "João Silva"
    assert data["email"] == "joao.silva@email.com"
    assert data["telefone"] == "(11) 99999-9999"
    assert data["aceitou_lgpd"] is True
    assert "criado_em" in data

def test_create_lead_update_existing(client):
    payload_initial = {
        "nome": "João Silva",
        "email": "joao.silva@email.com",
        "telefone": "(11) 99999-9999",
        "aceitou_lgpd": True
    }
    resp_init = client.post("/leads", json=payload_initial)
    assert resp_init.status_code == 201
    id_initial = resp_init.json()["id"]

    payload_updated = {
        "nome": "João S. Silva",
        "email": "joao.silva@email.com",
        "telefone": "11988888888",
        "aceitou_lgpd": True
    }
    response = client.post("/leads", json=payload_updated)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == id_initial
    assert data["nome"] == "João S. Silva"
    assert "11988888888" in data["telefone"]

def test_create_lead_invalid_phone(client):
    payload = {
        "nome": "João Silva",
        "email": "joao.silva@email.com",
        "telefone": "123",
        "aceitou_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    assert "telefone" in response.text

def test_create_lead_invalid_email(client):
    payload = {
        "nome": "João Silva",
        "email": "email_invalido",
        "telefone": "(11) 99999-9999",
        "aceitou_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    assert "email" in response.text

def test_create_lead_without_lgpd_consent(client):
    payload = {
        "nome": "João Silva",
        "email": "joao.silva@email.com",
        "telefone": "(11) 99999-9999",
        "aceitou_lgpd": False
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    assert "aceitou_lgpd" in response.text

def test_list_leads_empty(client):
    response = client.get("/leads")
    assert response.status_code == 200
    assert response.json() == []

def test_list_leads_with_data(client):
    lead1 = {
        "nome": "Lead Um",
        "email": "lead1@email.com",
        "telefone": "(11) 91111-1111",
        "aceitou_lgpd": True
    }
    lead2 = {
        "nome": "Lead Dois",
        "email": "lead2@email.com",
        "telefone": "(11) 92222-2222",
        "aceitou_lgpd": True
    }
    client.post("/leads", json=lead1)
    client.post("/leads", json=lead2)

    response = client.get("/leads")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["email"] == "lead1@email.com"
    assert data[1]["email"] == "lead2@email.com"

def test_get_lead_by_id_success(client):
    payload = {
        "nome": "Lead Alvo",
        "email": "alvo@email.com",
        "telefone": "(11) 93333-3333",
        "aceitou_lgpd": True
    }
    create_resp = client.post("/leads", json=payload)
    lead_id = create_resp.json()["id"]

    response = client.get(f"/leads/{lead_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lead_id
    assert data["nome"] == "Lead Alvo"
    assert data["email"] == "alvo@email.com"

def test_get_lead_by_id_not_found(client):
    response = client.get("/leads/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Lead não encontrado."