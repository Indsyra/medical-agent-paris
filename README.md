# Medical Agent Paris

Medical Agent Paris is an AI-powered agent that generates structured SOAP summaries
from medical consultation notes, helping clinicians save time on documentation.

## Architecture

The agent is built with LangGraph and consists of 3 nodes:

- **extract_entities** — extracts key medical information from the consultation
  text (symptoms, history, medications, exams) as structured JSON
- **structure_soap** — generates a SOAP summary from the extracted entities
- **verify_soap** — verifies that all 4 SOAP sections are present and complete

A conditional edge between `extract_entities` and `structure_soap` ensures the
agent retries extraction if the output is incomplete.

```
extract_entities → (conditional edge) → structure_soap → verify_soap → END
        ↑______________________________________________|
                      (if extraction fails)
```

## Tech Stack

- Python 3.11+
- OpenAI API (gpt-4o-mini)
- LangChain
- LangGraph
- FastAPI
- Docker
- Google Cloud Run

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- Docker

### Install dependencies

```bash
uv sync
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### Configure environment

```bash
cp .env.example .env
```

Then fill in your API keys in `.env`:

```
OPENAI_API_KEY=your_openai_key_here
```

### Run locally

```bash
uvicorn src.api:app --reload
```

Open http://127.0.0.1:8000/docs to test the API interactively.

### Run with Docker

```bash
docker build -t medical-agent-paris .
docker run -p 8000:8000 --env-file .env medical-agent-paris
```

## Usage Example

### Request

```bash
POST /summarize
Content-Type: application/json
```

```json
{
  "text": "Jean Dupont, 45 years old. Chest pain since this morning. No cardiac history. Slight fever at 38.2°C, normal blood pressure. Emergency ECG prescribed. Ibuprofen 400mg."
}
```

### Response

```json
{
  "soap_summary": "**S - Subjective:**\nPatient reports chest pain since this morning with slight fever (38.2°C). No known cardiac history.\n\n**O - Objective:**\nTemperature 38.2°C, normal blood pressure. Emergency ECG prescribed.\n\n**A - Assessment:**\nAcute chest pain to investigate. Cardiac origin to be ruled out.\n\n**P - Plan:**\nEmergency ECG. Ibuprofen 400mg 3x/day for 5 days. Follow-up in 1 week.",
  "verification_ok": true
}
```

## Roadmap

- [x] LangGraph agent with 3 nodes (extraction, SOAP, verification)
- [x] FastAPI endpoint with auto-generated documentation
- [x] Docker containerization
- [ ] Cloud Run deployment — public URL
- [ ] Audio transcription (Whisper API) — convert recorded consultations to text
- [ ] GDPR / HDS compliance — patient data pseudonymization before API calls
- [ ] Multi-patient memory — persistent context across consultations using ChromaDB
- [ ] LangSmith monitoring — real-time agent observability

## License

MIT
