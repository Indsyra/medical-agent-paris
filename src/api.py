from fastapi import FastAPI
from pydantic import BaseModel
from medical_react_agent import agent

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


@app.post("/summarize", response_model=ConsultationResponse)
def summarize_consultation(request: ConsultationRequest):
    result = agent.invoke({"raw_text": request.text, "entities": {}, "soap_summary": "", "verification_ok": False})
    return ConsultationResponse(
        soap_summary=result["soap_summary"],
        verification_ok=result["verification_ok"]
    )
