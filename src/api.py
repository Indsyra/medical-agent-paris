from fastapi import FastAPI
from pydantic import BaseModel
from src.agent import agent
from src.database import SessionLocal, Consultation, init_db
import uuid

class ConsultationRequest(BaseModel):
    text: str


class ConsultationResponse(BaseModel):
    soap_summary: str
    verification_ok: bool


app = FastAPI(
    title="Medical Consultation Summarizer",
    description="API to summarize medical consultations into SOAP format.",
    version="1.0.0"
)

init_db()

@app.post("/summarize", response_model=ConsultationResponse)
def summarize_consultation(request: ConsultationRequest):
    result = agent.invoke({
        "raw_text": request.text,
        "entities": {},
        "soap_summary": "",
        "verification_ok": False
    })

    db = SessionLocal()
    try:
        consultation = Consultation(
            id=str(uuid.uuid4()),
            input_text=request.text,
            soap_summary=result["soap_summary"],
            verification_ok=result["verification_ok"]
        )
        db.add(consultation)
        db.commit()
    except Exception as e:
        print(f"Database logging failed: {e}")
        db.rollback()
    finally:
        db.close()

    return ConsultationResponse(
        soap_summary=result["soap_summary"],
        verification_ok=result["verification_ok"]
    )
