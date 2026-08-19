# Medical Agent Paris
Medical Agent Paris est un agent qui permet de fournir un résumé SOAP sur la base des notes de consultation d'un médecin.

## Architecture
L'agent est constitué de 3 noeuds : extract_entities, SOAP et verify_soap. 
Le noeud "extract_entities" sert à prélever du texte de la consultation, les informations utiles à la génération du résumé. 
Un edge conditionnel relie "extract_entities" au noeud "SOAP" pour que l'agent puisse revenir au premier noeud en cas d'échec.
Le noeud "SOAP" génère un résumé SOAP à partir des informations issues de "extract_entities".
Le noeud "verify_soap" vérifie que toutes les parties de la sortie du noeud SOAP sont bien présentes et conformes à ce qu'est un résumé SOAP.

extract_entities → (edge conditionnel) → structure_soap → verify_soap → END
        ↑_________________________________________|
                    (si extraction échoue)
## Stack technique
- Python 3.11+
- OpenAI API (gpt-4o-mini)
- LangChain
- LangGraph
- FastAPI

## Installation
### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) installé
  
### Dependencies installation
```bash
uv sync
source .venv/bin/activate
```

### Configuration
Copy `.env_example` in `.env`, then fill API keys :
```bash
cp .env.example .env
```

### Launch
```bash
uvicorn src.api:app --reload
```

Open http://127.0.0.1:8000/docs to test API interactively.

## Usage Example

### Request
Send a POST request to `/summarize` with the following body:

```json
{
  "text": "Jean Dupont, 45 ans. Douleur thoracique ce matin. Pas d'antécédents cardiaques. Fièvre 38.2°C, tension normale. ECG en urgence prescrit. Ibuprofène 400mg."
}
```

### Response
```json
{
  "soap_summary": "**S - Subjectif :**\nLe patient se plaint de douleurs thoraciques et présente une fièvre à 38.2°C. Aucun antécédent cardiaque notable.\n\n**O - Objectif :**\nTempérature 38.2°C, tension normale. ECG prescrit en urgence.\n\n**A - Analyse :**\nDouleur thoracique aiguë à investiguer, origine cardiaque à écarter.\n\n**P - Plan :**\nECG en urgence. Ibuprofène 400mg 3x/jour. Suivi dans 1 semaine.",
  "verification_ok": true
}
```

## Roadmap

- [ ] Audio transcription support (Whisper API) — convert recorded consultations to text automatically
- [ ] GDPR / HDS compliance — pseudonymization of patient data before API calls
- [ ] Multi-patient memory — persistent context across consultations using ChromaDB
- [ ] Docker deployment — containerized app ready for Google Cloud Run
