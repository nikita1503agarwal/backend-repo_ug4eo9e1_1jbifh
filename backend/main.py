from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from database import create_document, db
from datetime import datetime

app = FastAPI(title="9okXE Portfolio API", version="1.0.0")

# CORS: allow frontend to call API from any origin in this demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    description: str = Field(..., min_length=10, max_length=5000)
    deadline: Optional[str] = None
    budget: Optional[str] = None

class ContactResponse(BaseModel):
    ok: bool
    message: str

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}

@app.get("/test")
def test_db():
    try:
        status = db is not None
        return {"database": "connected" if status else "not_configured"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}

@app.post("/contact", response_model=ContactResponse)
def submit_contact(payload: ContactRequest):
    try:
        data = payload.model_dump()
        data.update({"status": "new", "source": "portfolio", "received_at": datetime.utcnow()})
        create_document("contactsubmission", data)
        return ContactResponse(
            ok=True,
            message="Thanks! I’ll reply from okvr500@gmail.com with your quote and next steps.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to submit: {e}")
