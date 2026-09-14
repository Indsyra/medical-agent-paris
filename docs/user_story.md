---
name: User Story
about: Nouvelle fonctionnalité ou amélioration
title: "[US] "
labels: enhancement
assignees: Indsyra
---

## User Story
En tant que **[médecin / développeur / administrateur]**,
je veux **[action]**
afin de **[bénéfice]**.

## Critères d'acceptation
- [ ] ...
- [ ] ...
- [ ] ...

## Notes techniques
<!-- Libs, endpoints, modèles concernés -->

## Estimation
- [ ] XS (< 1h)
- [ ] S (1-3h)
- [ ] M (3-6h)
- [ ] L (> 6h)

---

# Completed US (closed)

## US-01 — LangGraph agent with 3 nodes ✅
**As a** clinician,
**I want to** submit free-text consultation notes,
**so that** I automatically get a structured SOAP summary.

### Acceptance criteria
- [x] Node `extract_entities` extracts entities as JSON
- [x] Conditional edge retries extraction if incomplete
- [x] Node `structure_soap` generates the SOAP summary
- [x] Node `verify_soap` verifies completeness of the summary

### Technical notes
- LangGraph StateGraph
- OpenAI gpt-4o-mini
- TypedDict MedicalState

### Estimation
- [x] L (> 6h)

---

## US-02 — FastAPI endpoint POST /summarize ✅
**As a** developer,
**I want to** expose the agent via a REST API,
**so that** it can be integrated into any medical application.

### Acceptance criteria
- [x] `POST /summarize` endpoint accepts a consultation text
- [x] Structured response with `soap_summary` and `verification_ok`
- [x] Auto-generated documentation available at `/docs`
- [x] Pydantic models `ConsultationRequest` and `ConsultationResponse`

### Technical notes
- FastAPI + uvicorn
- Pydantic BaseModel
- src/api.py

### Estimation
- [x] S (1-3h)

---

## US-03 — Docker containerization + Cloud Run deployment ✅
**As a** developer,
**I want to** deploy the agent on the internet,
**so that** it is accessible from any application worldwide.

### Acceptance criteria
- [x] Dockerfile with dynamic port (PORT env var)
- [x] Image pushed to Google Container Registry
- [x] Deployed on Cloud Run europe-west1
- [x] Public URL live and tested

### Technical notes
- Docker + gcr.io
- gcloud run deploy
- URL: https://medical-agent-paris-756908488363.europe-west1.run.app

### Estimation
- [x] M (3-6h)

---

## US-08 — PostgreSQL logging with Supabase ✅
**As a** developer,
**I want to** save every processed consultation to a database,
**so that** I have an exploitable history of all summaries.

### Acceptance criteria
- [x] Table `consultations` with id, input_text, soap_summary, verification_ok, created_at
- [x] Every `/summarize` call inserts a row
- [x] PostgreSQL + SQLAlchemy + Supabase

### Technical notes
- SQLAlchemy + psycopg2-binary
- Supabase (EU region)
- src/database.py

### Estimation
- [x] S (1-3h)

---

# Open US (backlog)

## US-04 — LangSmith monitoring ⛔ Blocked
**As a** developer,
**I want to** visualize every agent step in real time,
**so that** I can debug and optimize performance.

### Acceptance criteria
- [ ] LangSmith connected to the LangGraph agent
- [ ] Every node traced with its input/output
- [ ] Errors logged with full context
- [ ] Project dashboard accessible on smith.langchain.com

### Technical notes
- LANGCHAIN_TRACING_V2=true
- LANGCHAIN_API_KEY in .env
- smith.langchain.com → Personal Access Token
- ⛔ Blocked: 403 error on API — Personal Access Token scope issue

### Estimation
- [ ] S (1-3h)

---

## US-05 — GDPR compliance — patient data pseudonymization
**As a** developer,
**I want to** pseudonymize patient data before any external API call,
**so that** the system is compliant with GDPR and HDS regulations.

### Acceptance criteria
- [ ] Names, birth dates and social security numbers replaced by tokens
- [ ] Pseudonymization applied before OpenAI API call
- [ ] Anonymization report returned with the response
- [ ] Raw patient data never sent to an external server

### Technical notes
- Lib: presidio-analyzer + presidio-anonymizer (Microsoft)
- Apply in extract_entities before llm.invoke()
- Add anonymization_report field to ConsultationResponse

### Estimation
- [ ] M (3-6h)

---

## US-06 — Multi-patient memory with ChromaDB
**As a** clinician,
**I want to** query a patient's consultation history,
**so that** the new SOAP summary is contextualized with past records.

### Acceptance criteria
- [ ] Each consultation stored in ChromaDB with a patient_id
- [ ] Agent retrieves previous consultations before generating SOAP
- [ ] Summary mentions changes compared to past consultations
- [ ] Data isolated per patient (no cross-patient mixing)

### Technical notes
- ChromaDB collection per patient_id
- RAG on history before structure_soap node
- New field patient_id in ConsultationRequest

### Estimation
- [ ] L (> 6h)

---

## US-07 — Audio transcription support via Whisper API
**As a** clinician,
**I want to** upload an audio recording of a consultation,
**so that** I get a SOAP summary without typing the text manually.

### Acceptance criteria
- [ ] `POST /transcribe` endpoint accepts audio files (.mp3, .wav, .m4a)
- [ ] Whisper API transcribes audio to French text
- [ ] Transcribed text automatically sent to /summarize
- [ ] Response contains both transcription and SOAP summary

### Technical notes
- openai.audio.transcriptions.create()
- FastAPI UploadFile for audio file reception
- New endpoint POST /transcribe in src/api.py

### Estimation
- [ ] L (> 6h)

---

## US-09 — Monitoring dashboard — usage metrics (PySpark)
**As a** medical director,
**I want to** see agent usage metrics,
**so that** I can monitor the quality of generated summaries at scale.

### Acceptance criteria
- [ ] Number of consultations per day
- [ ] verification_ok rate
- [ ] Average response time
- [ ] Dashboard accessible at `/metrics`
- [ ] PySpark handles computation on large volumes (100k+ rows)

### Technical notes
- **PySpark** for metric computation on large datasets
  - SparkSession reading from Supabase via JDBC
  - Aggregations: count per day, avg response time, success rate
  - Output written back to a `metrics` table in Supabase
- New endpoint `GET /metrics` in src/api.py
- Why PySpark: pandas breaks above ~100k rows; PySpark scales to millions

### Estimation
- [ ] L (> 6h)

---

## US-10 — Batch processing — CSV upload (Airflow)
**As a** clinician,
**I want to** upload a CSV file of consultations,
**so that** I get all SOAP summaries processed in one go.

### Acceptance criteria
- [ ] `POST /batch` endpoint accepts a CSV file
- [ ] Each row processed as an independent consultation
- [ ] Output CSV returned with generated SOAPs
- [ ] Row-level error handling without blocking the entire batch
- [ ] Airflow DAG orchestrates nightly batch automatically

### Technical notes
- **Apache Airflow** for batch orchestration
  - DAG runs nightly at midnight
  - Task 1: extract unprocessed consultations from Supabase
  - Task 2: send each to /summarize endpoint
  - Task 3: update Supabase with results
  - Task 4: send summary report by email
- FastAPI UploadFile for CSV reception
- pandas for CSV read/write
- Why Airflow: replaces manual batch runs with a scheduled, monitored pipeline

### Estimation
- [ ] L (> 6h)
