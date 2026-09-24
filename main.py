import os
import re
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

# 1. Caminho Absoluto do SQLite e Configuração do Engine
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Modelo de Banco de Dados SQLAlchemy
class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    company = Column(String, nullable=True)
    role = Column(String, nullable=True)
    consent = Column(Boolean, default=False, nullable=False)

# 3. Schemas do Pydantic V2 com Tipagem Primitiva e ConfigDict
class LeadCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str
    company: Optional[str] = None
    role: Optional[str] = None
    consent: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Regex em raw string validando formato com ou sem DDD/máscara nacional
        phone_regex = re.compile(r"^\+?(\d{2})?\s?\(?\d{2}\)?\s?\d{4,5}-?\d{4}$")
        if not phone_regex.match(v):
            raise ValueError("Formato de telefone inválido. Insira um número válido com DDD.")
        return v

    @field_validator("consent")
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("O consentimento dos termos de privacidade (LGPD) é obrigatório.")
        return v

class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    company: Optional[str] = None
    role: Optional[str] = None
    consent: bool

    model_config = ConfigDict(from_attributes=True)

# 4. Gerenciamento de Contexto Lifespan do FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Criação das Tabelas no arranque da aplicação
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Microserviço de Captura de Leads",
    version="1.0.0",
    lifespan=lifespan
)

# Dependência do Banco de Dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. Endpoints HTTP
@app.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead_in: LeadCreate, db=Depends(get_db)):
    # Regra de Negócio: Impedir e-mails duplicados (RN-001)
    existing_lead = db.query(Lead).filter(Lead.email == lead_in.email).first()
    if existing_lead:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Este e-mail já foi cadastrado para outra oferta."
        )

    db_lead = Lead(
        name=lead_in.name,
        email=lead_in.email,
        phone=lead_in.phone,
        company=lead_in.company,
        role=lead_in.role,
        consent=lead_in.consent
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@app.get("/leads", response_model=List[LeadResponse], status_code=status.HTTP_200_OK)
def list_leads(db=Depends(get_db)):
    return db.query(Lead).all()


# 6. Testes Unitários Integrados (Executados via Pytest)
from fastapi.testclient import TestClient

def test_flow_leads():
    with TestClient(app) as client:
        # 1. Criação de lead válida
        import uuid
        unique_email = f"lead_{uuid.uuid4().hex[:8]}@empresa.com.br"
        payload = {
            "name": "Carlos Silva",
            "email": unique_email,
            "phone": "11988887777",
            "company": "Tech Solutions",
            "role": "CTO",
            "consent": True
        }
        response = client.post("/leads", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["email"] == unique_email

        # 2. Rejeição de e-mail duplicado (RN-001)
        response_dup = client.post("/leads", json=payload)
        assert response_dup.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Este e-mail já foi cadastrado" in response_dup.json()["detail"]

        # 3. Rejeição por falta de consentimento LGPD (RN-002)
        payload["email"] = f"outro_{uuid.uuid4().hex[:8]}@empresa.com"
        payload["consent"] = False
        response_consent = client.post("/leads", json=payload)
        assert response_consent.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # 4. Rejeição por formato de telefone inválido
        payload["consent"] = True
        payload["phone"] = "abc123"
        response_phone = client.post("/leads", json=payload)
        assert response_phone.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY