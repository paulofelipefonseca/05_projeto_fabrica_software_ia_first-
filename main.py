import os
import re
import uuid
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, func
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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    consent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    ip_address = Column(String, nullable=True)

class LeadCreate(BaseModel):
    name: str
    email: str
    phone: str
    consent: bool

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, v):
            raise ValueError("O e-mail fornecido não é válido.")
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if not re.match(r"^\d{10,11}$", cleaned):
            raise ValueError("O telefone deve conter DDD e de 8 a 9 dígitos numéricos.")
        return cleaned

    @field_validator('consent')
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("É necessário aceitar os termos de consentimento.")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "João Silva",
                "email": "joao.silva@example.com",
                "phone": "11999998888",
                "consent": True
            }
        }
    )

class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    consent: bool
    ip_address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="Lead Capture API", lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_index():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Página de Captura - Leads</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 flex items-center justify-center min-h-screen font-sans">
        <div class="bg-white p-8 rounded-xl shadow-lg max-w-md w-full border border-gray-100">
            <h2 class="text-3xl font-extrabold mb-2 text-center text-gray-900">Receba Novidades</h2>
            <p class="text-sm text-center text-gray-500 mb-6 font-medium">Preencha os campos abaixo para ficar por dentro de tudo!</p>
            <form id="leadForm" class="space-y-4">
                <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">Nome Completo</label>
                    <input type="text" id="name" required class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">E-mail</label>
                    <input type="email" id="email" placeholder="exemplo@email.com" required class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">Telefone (com DDD)</label>
                    <input type="text" id="phone" placeholder="11999998888" required class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition">
                </div>
                <div class="flex items-start mt-2">
                    <input type="checkbox" id="consent" required class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded mt-1 mr-2">
                    <label for="consent" class="text-xs text-gray-600 leading-normal">Aceito receber contatos e autorizo o processamento dos meus dados conforme a LGPD.</label>
                </div>
                <button type="submit" class="w-full bg-indigo-600 text-white font-semibold py-3 rounded-lg hover:bg-indigo-700 transition-colors shadow-md mt-4">Enviar Cadastro</button>
            </form>
            <div id="message" class="mt-4 p-3 rounded-lg text-sm text-center hidden"></div>
        </div>
        <script>
            document.getElementById('leadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const messageDiv = document.getElementById('message');
                messageDiv.classList.add('hidden');

                const payload = {
                    name: document.getElementById('name').value,
                    email: document.getElementById('email').value,
                    phone: document.getElementById('phone').value,
                    consent: document.getElementById('consent').checked
                };

                try {
                    const response = await fetch('/leads', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    if (response.status === 201) {
                        messageDiv.textContent = "Cadastro realizado com sucesso!";
                        messageDiv.className = "mt-4 p-3 rounded-lg text-sm text-center bg-green-50 text-green-700 font-semibold border border-green-200";
                        document.getElementById('leadForm').reset();
                    } else {
                        const errData = await response.json();
                        let errMsg = "Erro no envio dos dados.";
                        if (errData.detail) {
                            if (Array.isArray(errData.detail)) {
                                errMsg = errData.detail.map(d => d.msg).join(", ");
                            } else {
                                errMsg = errData.detail;
                            }
                        }
                        messageDiv.textContent = errMsg;
                        messageDiv.className = "mt-4 p-3 rounded-lg text-sm text-center bg-red-50 text-red-700 font-semibold border border-red-200";
                    }
                } catch (err) {
                    messageDiv.textContent = "Falha ao estabelecer conexão.";
                    messageDiv.className = "mt-4 p-3 rounded-lg text-sm text-center bg-red-50 text-red-700 font-semibold border border-red-200";
                }
                messageDiv.classList.remove('hidden');
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=status.HTTP_200_OK)

@app.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead_in: LeadCreate, request: Request, db: Session = Depends(get_db)):
    existing_lead = db.query(Lead).filter(Lead.email == lead_in.email).first()
    if existing_lead:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Este e-mail já está cadastrado no sistema."
        )

    client_ip = request.client.host if request.client else "127.0.0.1"

    db_lead = Lead(
        name=lead_in.name,
        email=lead_in.email,
        phone=lead_in.phone,
        consent=lead_in.consent,
        ip_address=client_ip
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@app.get("/leads", response_model=List[LeadResponse], status_code=status.HTTP_200_OK)
def list_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return leads

from fastapi.testclient import TestClient

def test_create_lead():
    client = TestClient(app)
    unique_email = f"lead_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "Dev Sênior",
        "email": unique_email,
        "phone": "11988887777",
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Dev Sênior"
    assert data["email"] == unique_email

def test_create_lead_invalid_phone():
    client = TestClient(app)
    payload = {
        "name": "Dev Sênior",
        "email": "invalid@example.com",
        "phone": "999",
        "consent": True
    }
    response = client.post("/leads", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY