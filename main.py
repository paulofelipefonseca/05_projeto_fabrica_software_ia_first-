import os
import re
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool

# Configuração de Banco de Dados SQLite Local
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'app.db')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"check_same_thread": False}
)

Base = declarative_base()

# Diretriz Obrigatória: Criação Global de Tabelas
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modelo do Banco de Dados (SQLAlchemy)
class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, nullable=False)
    consentimento_lgpd = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    ip_origem = Column(String, nullable=True)

# Modelos Pydantic V2 para Entrada e Saída
class LeadCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    telefone: str
    consentimento_lgpd: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator('consentimento_lgpd')
    @classmethod
    def check_consentimento(cls, v: bool) -> bool:
        if not v:
            raise ValueError("O consentimento para tratamento de dados (LGPD) é obrigatório.")
        return v

    @field_validator('telefone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Validação Rigorosa com Uso Obrigatório de Raw Strings em Regex
        pattern = r"^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$"
        digits_only_pattern = r"^\d{10,11}$"
        
        if not re.match(pattern, v) and not re.match(digits_only_pattern, v):
            raise ValueError("Telefone inválido. Utilize o formato (XX) 9XXXX-XXXX ou apenas números com DDD.")
        return v

class LeadResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    consentimento_lgpd: bool
    criado_em: datetime
    ip_origem: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Dependência do Banco de Dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Gerenciador de contexto Lifespan do FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executado ao iniciar
    yield
    # Executado ao finalizar

app = FastAPI(
    title="Landing Page Lead Capture API",
    version="1.0.0",
    lifespan=lifespan
)

# Endpoints da API
@app.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_lead(lead_in: LeadCreate, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"

    # RF-005: Prevenção de Duplicidade (Atualiza o cadastro caso e-mail já exista)
    existing_lead = db.query(Lead).filter(Lead.email == lead_in.email).first()
    if existing_lead:
        existing_lead.nome = lead_in.nome
        existing_lead.telefone = lead_in.telefone
        existing_lead.consentimento_lgpd = lead_in.consentimento_lgpd
        existing_lead.ip_origem = client_ip
        db.commit()
        db.refresh(existing_lead)
        return existing_lead

    new_lead = Lead(
        nome=lead_in.nome,
        email=lead_in.email,
        telefone=lead_in.telefone,
        consentimento_lgpd=lead_in.consentimento_lgpd,
        ip_origem=client_ip
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead

@app.get("/leads", response_model=List[LeadResponse], status_code=status.HTTP_200_OK)
def list_leads(db: Session = Depends(get_db)):
    return db.query(Lead).all()

@app.get("/leads/{lead_id}", response_model=LeadResponse, status_code=status.HTTP_200_OK)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead não encontrado"
        )
    return lead

# --- TESTES INTEGRADOS (Pytest) ---
from fastapi.testclient import TestClient

def test_create_and_update_lead():
    client = TestClient(app)
    
    # Criar um novo lead válido
    payload = {
        "nome": "João Silva",
        "email": "joao@example.com",
        "telefone": "(11) 99999-8888",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "João Silva"
    assert data["email"] == "joao@example.com"
    assert data["consentimento_lgpd"] is True
    assert "id" in data
    
    # Atualizar o mesmo lead (Evitando duplicidade)
    payload_update = {
        "nome": "João S. Silva",
        "email": "joao@example.com",
        "telefone": "11988887777",
        "consentimento_lgpd": True
    }
    response_update = client.post("/leads", json=payload_update)
    assert response_update.status_code == 201
    data_update = response_update.json()
    assert data_update["id"] == data["id"]
    assert data_update["nome"] == "João S. Silva"
    assert data_update["telefone"] == "11988887777"

def test_validation_errors():
    client = TestClient(app)
    
    # Telefone inválido
    payload_invalid_phone = {
        "nome": "Ana Souza",
        "email": "ana@example.com",
        "telefone": "123",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload_invalid_phone)
    assert response.status_code == 422
    
    # Falta de consentimento LGPD
    payload_no_consent = {
        "nome": "Ana Souza",
        "email": "ana@example.com",
        "telefone": "11999998888",
        "consentimento_lgpd": False
    }
    response = client.post("/leads", json=payload_no_consent)
    assert response.status_code == 422

    # Nome curto demais (RF-002)
    payload_short_name = {
        "nome": "Lu",
        "email": "lu@example.com",
        "telefone": "11999998888",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload_short_name)
    assert response.status_code == 422