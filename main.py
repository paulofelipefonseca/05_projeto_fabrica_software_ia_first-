import os
import re
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Response
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, "app.db")}'

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"check_same_thread": False}
)
Base = declarative_base()
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class LeadDB(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, nullable=False)
    consentimento_lgpd = Column(Boolean, nullable=False, default=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LeadCreate(BaseModel):
    nome_completo: str = Field(..., min_length=2, max_length=100)
    email: str
    telefone: str
    consentimento_lgpd: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator("consentimento_lgpd")
    @classmethod
    def must_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("O consentimento para uso de dados (LGPD) é obrigatório.")
        return v

    @field_validator("telefone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if not (10 <= len(cleaned) <= 11):
            raise ValueError("O telefone deve conter entre 10 e 11 dígitos numéricos com DDD.")
        
        pattern = r"^[1-9]{2}9?[0-9]{8}$"
        if not re.match(pattern, cleaned):
            raise ValueError("Número de telefone inválido. Verifique o DDD e o formato.")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, v):
            raise ValueError("Formato de e-mail inválido.")
        return v.lower()

class LeadResponse(BaseModel):
    id: int
    nome_completo: str
    email: str
    telefone: str
    consentimento_lgpd: bool
    data_criacao: datetime
    data_atualizacao: datetime

    model_config = ConfigDict(from_attributes=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Lead Capture Microservice",
    description="API robusta de captura de leads com conformidade com LGPD",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_lead(lead_in: LeadCreate, response: Response, db: Session = Depends(get_db)):
    existing_lead = db.query(LeadDB).filter(LeadDB.email == lead_in.email).first()
    if existing_lead:
        existing_lead.nome_completo = lead_in.nome_completo
        existing_lead.telefone = lead_in.telefone
        existing_lead.consentimento_lgpd = lead_in.consentimento_lgpd
        existing_lead.data_atualizacao = datetime.utcnow()
        db.commit()
        db.refresh(existing_lead)
        response.status_code = status.HTTP_200_OK
        return existing_lead

    new_lead = LeadDB(
        nome_completo=lead_in.nome_completo,
        email=lead_in.email,
        telefone=lead_in.telefone,
        consentimento_lgpd=lead_in.consentimento_lgpd
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead

@app.get("/leads", response_model=List[LeadResponse], status_code=status.HTTP_200_OK)
def list_leads(db: Session = Depends(get_db)):
    return db.query(LeadDB).all()

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy"}


# --- PYTEST UNIT TESTS ---
from fastapi.testclient import TestClient

def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_lead_success():
    client = TestClient(app)
    payload = {
        "nome_completo": "Carlos Silva",
        "email": "carlos@example.com",
        "telefone": "11999999999",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code in [201, 200]
    data = response.json()
    assert data["email"] == "carlos@example.com"
    assert data["nome_completo"] == "Carlos Silva"

def test_create_lead_invalid_phone():
    client = TestClient(app)
    payload = {
        "nome_completo": "Carlos Silva",
        "email": "carlos_fail_phone@example.com",
        "telefone": "12345",
        "consentimento_lgpd": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422

def test_create_lead_no_consent():
    client = TestClient(app)
    payload = {
        "nome_completo": "Carlos Silva",
        "email": "carlos_fail_consent@example.com",
        "telefone": "11999999999",
        "consentimento_lgpd": False
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422

def test_create_duplicate_lead_updates():
    client = TestClient(app)
    payload1 = {
        "nome_completo": "Lead Original",
        "email": "duplicado@example.com",
        "telefone": "11999999999",
        "consentimento_lgpd": True
    }
    r1 = client.post("/leads", json=payload1)
    assert r1.status_code in [200, 201]

    payload2 = {
        "nome_completo": "Lead Atualizado",
        "email": "duplicado@example.com",
        "telefone": "11988888888",
        "consentimento_lgpd": True
    }
    r2 = client.post("/leads", json=payload2)
    assert r2.status_code == 200
    data = r2.json()
    assert data["nome_completo"] == "Lead Atualizado"
    assert data["telefone"] == "11988888888"