import os
import re
from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Configuração do caminho absoluto do banco SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"

# Instanciação do engine com pool e conexões otimizados para testes
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"check_same_thread": False}
)
Base = declarative_base()

# Diretriz técnica obrigatória: Criação global de tabelas abaixo do engine e Base
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modelo de Banco de Dados
class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    telefone = Column(String(20), nullable=False)
    aceitou_lgpd = Column(Boolean, nullable=False, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

# Esquemas de Validação Pydantic (Apenas tipos primitivos e model_config)
class LeadCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., max_length=150)
    telefone: str = Field(..., max_length=20)
    aceitou_lgpd: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, v: str) -> str:
        # Validação explícita de telefone utilizando Raw String no regex
        cleaned = re.sub(r"\s+", "", v)
        phone_pattern = r"^\+?[0-9]{10,15}$|^\(?[1-9]{2}\)?\s?9?[0-9]{4}-?[0-9]{4}$"
        if not re.match(phone_pattern, cleaned):
            raise ValueError("Formato de telefone inválido. Use (XX) 9XXXX-XXXX ou apenas dígitos com DDD.")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        # Validação explícita de e-mail utilizando Raw String no regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v):
            raise ValueError("Endereço de e-mail inválido.")
        return v

    @field_validator("aceitou_lgpd")
    @classmethod
    def validate_lgpd(cls, v: bool) -> bool:
        if not v:
            raise ValueError("O consentimento para a LGPD é obrigatório.")
        return v

class LeadResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    aceitou_lgpd: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)

# Gerenciador de ciclo de vida (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Landing Page Lead Capture API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependência da sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para Captura de Leads (Cria ou atualiza com base no email - RN-01)
@app.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    existing_lead = db.query(Lead).filter(Lead.email == lead_in.email).first()
    
    if existing_lead:
        # Atualiza o cadastro existente mantendo a unicidade do e-mail
        existing_lead.nome = lead_in.nome
        existing_lead.telefone = lead_in.telefone
        existing_lead.aceitou_lgpd = lead_in.aceitou_lgpd
        existing_lead.criado_em = datetime.utcnow()
        db.commit()
        db.refresh(existing_lead)
        return existing_lead

    db_lead = Lead(
        nome=lead_in.nome,
        email=lead_in.email,
        telefone=lead_in.telefone,
        aceitou_lgpd=lead_in.aceitou_lgpd
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

# Endpoint administrativo para listar leads
@app.get("/leads", response_model=List[LeadResponse], status_code=status.HTTP_200_OK)
def list_leads(db: Session = Depends(get_db)):
    return db.query(Lead).all()

# Endpoint para buscar lead específico
@app.get("/leads/{lead_id}", response_model=LeadResponse, status_code=status.HTTP_200_OK)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead não encontrado."
        )
    return lead

# Código de Testes Unitários e Integração integrado para o Pytest
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_lead_success():
    db = SessionLocal()
    db.query(Lead).delete()
    db.commit()
    db.close()

    payload = {
        "nome": "João Silva",
        "email": "joao.silva@email.com",
        "telefone": "(11) 99999-9999",
        "aceitou_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == "joao.silva@email.com"

def test_create_lead_update_existing():
    payload_initial = {
        "nome": "João Silva",
        "email": "joao.silva@email.com",
        "telefone": "(11) 99999-9999",
        "aceitou_lgpd": True
    }
    client.post("/leads", json=payload_initial)

    payload_updated = {
        "nome": "João S. Silva",
        "email": "joao.silva@email.com",
        "telefone": "11988888888",
        "aceitou_lgpd": True
    }
    response = client.post("/leads", json=payload_updated)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "João S. Silva"
    assert "11988888888" in data["telefone"]

def test_create_lead_invalid_phone():
    payload = {
        "nome": "João Silva",
        "email": "joao.silva@email.com",
        "telefone": "123",
        "aceitou_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422

def test_create_lead_without_lgpd_consent():
    payload = {
        "nome": "João Silva",
        "email": "joao.silva@email.com",
        "telefone": "(11) 99999-9999",
        "aceitou_lgpd": False
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422