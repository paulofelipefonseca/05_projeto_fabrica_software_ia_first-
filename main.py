import os
import re
from typing import Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool

db_path = os.path.join(os.path.dirname(__file__), 'app.db')
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"check_same_thread": False}
)
Base = declarative_base()
Base.metadata.create_all(bind=engine)

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    consent = Column(Boolean, default=False, nullable=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LeadCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    phone: str
    consent: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        cleaned = v.strip().lower()
        if not email_regex.match(cleaned):
            raise ValueError("O formato de e-mail fornecido é inválido.")
        return cleaned

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        phone_regex = re.compile(r"^\+?[1-9][0-9]{9,14}$")
        cleaned = re.sub(r"\s+|-|\(|\)", "", v)
        if not phone_regex.match(cleaned):
            raise ValueError("O número de telefone deve ser válido no formato nacional ou internacional com DDD (ex: +5511999999999).")
        return cleaned

    @field_validator('consent')
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("É obrigatório aceitar as diretrizes de privacidade (LGPD).")
        return v

class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    consent: bool

    model_config = ConfigDict(from_attributes=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Microserviço de Captura de Leads",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    existing_lead = db.query(Lead).filter(Lead.email == lead_in.email).first()
    if existing_lead:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Este endereço de e-mail já está cadastrado."
        )
    
    db_lead = Lead(
        name=lead_in.name,
        email=lead_in.email,
        phone=lead_in.phone,
        consent=lead_in.consent
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@app.get("/leads", response_model=List[LeadResponse], status_code=status.HTTP_200_OK)
def list_leads(db: Session = Depends(get_db)):
    return db.query(Lead).all()