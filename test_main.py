import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from main import app, Base, engine


@pytest.fixture(autouse=True)
def setup_database():
    """
    Garante a criação de todas as tabelas no banco de dados antes do início de
    cada teste e realiza o drop das mesmas após a execução do teste.
    Crucial para isolamento de testes e pipelines de CI/CD.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Fixture que fornece o TestClient para simulação das chamadas HTTP."""
    return TestClient(app)


def test_create_lead_success(client):
    """Testa o cadastro com sucesso de um novo lead atendendo aos critérios da LGPD."""
    payload = {
        "nome": "João Silva",
        "email": "joao.silva@exemplo.com",
        "telefone": "11 98765-4321",
        "consentimento": True,
        "ip_origem": "192.168.1.50"
    }
    response = client.post("/leads", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["nome"] == payload["nome"]
    assert data["email"] == payload["email"]
    assert data["telefone"] == "11987654321"  # Deve vir limpo (apenas dígitos)
    assert data["consentimento"] is True
    assert data["ip_origem"] == "192.168.1.50"
    assert "criado_em" in data


def test_create_lead_without_ip_uses_fallback(client):
    """Testa o cadastro de lead omitindo o IP, validando se assume o fallback padrão."""
    payload = {
        "nome": "Maria Souza",
        "email": "maria.souza@exemplo.com",
        "telefone": "(21) 99999-8888",
        "consentimento": True
    }
    response = client.post("/leads", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["ip_origem"] is not None  # Deve assumir IP do client ou localhost


def test_create_lead_duplicate_email(client):
    """Testa a restrição de unicidade para e-mails cadastrados."""
    payload = {
        "nome": "Primeiro Lead",
        "email": "duplicado@exemplo.com",
        "telefone": "11912345678",
        "consentimento": True
    }
    
    # Primeiro cadastro
    response_first = client.post("/leads", json=payload)
    assert response_first.status_code == 201

    # Segunda tentativa de cadastro com o mesmo e-mail
    response_duplicate = client.post("/leads", json=payload)
    assert response_duplicate.status_code == 422
    assert response_duplicate.json()["detail"] == "O e-mail informado já está cadastrado em nossa base."


def test_create_lead_without_consent(client):
    """Testa a validação obrigatória do consentimento LGPD."""
    payload = {
        "nome": "Lead Sem Consentimento",
        "email": "sem.consentimento@exemplo.com",
        "telefone": "11912345678",
        "consentimento": False
    }
    response = client.post("/leads", json=payload)
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("consentimento" in err["loc"] for err in errors)
    assert any("O consentimento de privacidade e uso de dados é obrigatório." in err["msg"] for err in errors)


def test_create_lead_invalid_phone_format(client):
    """Testa a validação do formato do telefone (deve conter de 10 a 11 dígitos numéricos)."""
    payload = {
        "nome": "Lead Telefone Invalido",
        "email": "fone.invalido@exemplo.com",
        "telefone": "123456789",  # Apenas 9 dígitos
        "consentimento": True
    }
    response = client.post("/leads", json=payload)
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("telefone" in err["loc"] for err in errors)
    assert any("O telefone deve conter de 10 a 11 digitos numericos" in err["msg"] for err in errors)


def test_create_lead_invalid_email_format(client):
    """Testa a validação sintática do campo de e-mail usando Pydantic EmailStr."""
    payload = {
        "nome": "Email Invalido",
        "email": "email-sem-arroba.com",
        "telefone": "11999998888",
        "consentimento": True
    }
    response = client.post("/leads", json=payload)
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("email" in err["loc"] for err in errors)


def test_list_leads_empty(client):
    """Garante que a listagem retorna uma lista vazia quando não há leads no banco."""
    response = client.get("/leads")
    assert response.status_code == 200
    assert response.json() == []


def test_list_leads_success(client):
    """Testa a listagem de múltiplos leads cadastrados na base."""
    # Cadastro de dois leads distintos
    lead_1 = {
        "nome": "Lead Um",
        "email": "lead1@exemplo.com",
        "telefone": "11999991111",
        "consentimento": True
    }
    lead_2 = {
        "nome": "Lead Dois",
        "email": "lead2@exemplo.com",
        "telefone": "21999992222",
        "consentimento": True
    }
    
    client.post("/leads", json=lead_1)
    client.post("/leads", json=lead_2)

    # Obtenção da lista
    response = client.get("/leads")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["email"] == "lead1@exemplo.com"
    assert data[1]["email"] == "lead2@exemplo.com"