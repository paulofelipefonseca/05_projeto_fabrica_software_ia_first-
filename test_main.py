import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from main import app, Base, engine


@pytest.fixture(autouse=True)
def setup_database():
    """
    Garante a criação e limpeza das tabelas do banco de dados antes de cada teste,
    evitando vazamento de estado e conflito entre execuções.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """
    Retorna uma instância do TestClient do FastAPI para realizar requisições de testes.
    """
    return TestClient(app)


def test_create_lead_success(client):
    """
    Testa a criação de um lead com sucesso passando dados válidos.
    """
    payload = {
        "name": "João Silva",
        "email": "joao.silva@example.com",
        "phone": "+5511999999999",
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "João Silva"
    assert data["email"] == "joao.silva@example.com"
    assert data["phone"] == "+5511999999999"
    assert data["consent"] is True


def test_create_lead_duplicate_email(client):
    """
    Garante que não seja possível registrar dois leads com o mesmo endereço de e-mail.
    """
    payload = {
        "name": "Ana Maria",
        "email": "ana.maria@example.com",
        "phone": "11988888888",
        "consent": True
    }
    
    # Primeira inserção
    response1 = client.post("/leads", json=payload)
    assert response1.status_code == 201

    # Segunda tentativa (duplicado)
    response2 = client.post("/leads", json=payload)
    assert response2.status_code == 422
    assert response2.json()["detail"] == "Este endereço de e-mail já está cadastrado."


def test_create_lead_invalid_email(client):
    """
    Testa a validação do formato de e-mail inválido pelo Pydantic.
    """
    payload = {
        "name": "Carlos Souza",
        "email": "email_invalido.com",
        "phone": "11977777777",
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    
    errors = response.json()["detail"]
    assert any("O formato de e-mail fornecido é inválido." in err["msg"] for err in errors)


def test_create_lead_invalid_phone(client):
    """
    Garante que o número de telefone deve cumprir os padrões do validador.
    """
    payload = {
        "name": "Carlos Souza",
        "email": "carlos@example.com",
        "phone": "123",  # Telefone curto demais/fora do padrão
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    
    errors = response.json()["detail"]
    assert any("O número de telefone deve ser válido" in err["msg"] for err in errors)


def test_create_lead_without_consent(client):
    """
    Testa se a API recusa a criação de leads que não aceitam as diretrizes de privacidade (LGPD).
    """
    payload = {
        "name": "Juliana Costa",
        "email": "juliana@example.com",
        "phone": "11966666666",
        "consent": False
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422
    
    errors = response.json()["detail"]
    assert any("É obrigatório aceitar as diretrizes de privacidade (LGPD)." in err["msg"] for err in errors)


def test_create_lead_name_too_short(client):
    """
    Verifica se o nome com menos de 2 caracteres é rejeitado.
    """
    payload = {
        "name": "A",
        "email": "a@example.com",
        "phone": "11955555555",
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422


def test_list_leads_empty(client):
    """
    Verifica se a rota de listagem retorna uma lista vazia quando não há leads.
    """
    response = client.get("/leads")
    assert response.status_code == 200
    assert response.json() == []


def test_list_leads_multiple(client):
    """
    Valida se a listagem retorna todos os leads cadastrados corretamente.
    """
    lead1 = {
        "name": "Primeiro Lead",
        "email": "primeiro@example.com",
        "phone": "11911111111",
        "consent": True
    }
    lead2 = {
        "name": "Segundo Lead",
        "email": "segundo@example.com",
        "phone": "11922222222",
        "consent": True
    }
    
    client.post("/leads", json=lead1)
    client.post("/leads", json=lead2)

    response = client.get("/leads")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["email"] == "primeiro@example.com"
    assert data[1]["email"] == "segundo@example.com"