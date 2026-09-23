import os
import re
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool

DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'app.db')}"

engine = create_engine(DATABASE_URL, poolclass=NullPool, connect_args={"check_same_thread": False})
Base = declarative_base()
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, nullable=False)
    consentimento = Column(Boolean, default=False, nullable=False)
    ip_origem = Column(String, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

class LeadCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefone: str
    consentimento: bool
    ip_origem: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("consentimento")
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("O consentimento de privacidade e uso de dados é obrigatório.")
        return v

    @field_validator("telefone")
    @classmethod
    def validate_phone_format(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if not re.match(r"^\d{10,11}$", cleaned):
            raise ValueError("O telefone deve conter de 10 a 11 digitos numericos, incluindo o DDD.")
        return cleaned

class LeadResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    telefone: str
    consentimento: bool
    ip_origem: Optional[str]
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Lead Capture Microservice",
    description="API robusta de captura de leads em conformidade com a LGPD"
)

@app.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead_in: LeadCreate, request: Request, db: Session = Depends(get_db)):
    db_lead = db.query(Lead).filter(Lead.email == lead_in.email).first()
    if db_lead:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O e-mail informado já está cadastrado em nossa base."
        )
    
    ip = lead_in.ip_origem or (request.client.host if request.client else "127.0.0.1")
    
    new_lead = Lead(
        nome=lead_in.nome,
        email=lead_in.email,
        telefone=lead_in.telefone,
        consentimento=lead_in.consentimento,
        ip_origem=ip
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead

@app.get("/leads", response_model=List[LeadResponse], status_code=status.HTTP_200_OK)
def list_leads(db: Session = Depends(get_db)):
    return db.query(Lead).all()

# --- TEST SUITE ---
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_lead_success():
    unique_email = f"lead_{datetime.utcnow().timestamp()}@testdomain.com"
    payload = {
        "nome": "Carlos Silva",
        "email": unique_email,
        "telefone": "11987654321",
        "consentimento": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == unique_email
    assert response.json()["nome"] == "Carlos Silva"

def test_create_lead_no_consent():
    payload = {
        "nome": "Ana Souza",
        "email": "ana@testdomain.com",
        "telefone": "21987654321",
        "consentimento": False
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422

def test_create_lead_invalid_phone():
    payload = {
        "nome": "Lucas Lima",
        "email": "lucas@testdomain.com",
        "telefone": "12345",
        "consentimento": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == 422