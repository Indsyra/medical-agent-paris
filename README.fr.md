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

10 User Stories réparties en 5 epics. Détails complets dans
[`docs/USER_STORIES.md`](docs/USER_STORIES.md) ; diagrammes Mermaid dans
[`docs/roadmap/`](docs/roadmap/) (vue chronologique et vue par epic).

| Epic | User Stories | Statut |
|---|---|---|
| **A — Agent Core** | US-01 Agent LangGraph (3 nœuds) | ✅ Terminé |
| **B — API & Déploiement** | US-02 Endpoint FastAPI · US-03 Docker + Cloud Run | ✅ Terminé |
| **C — Data Engineering** | US-08 Logging Supabase · US-09 Dashboard métriques PySpark · US-10 Orchestration batch Airflow | ✅ US-08 · 🔲 US-09, US-10 |
| **D — Observabilité & Conformité** | US-04 Monitoring LangSmith · US-05 Pseudonymisation RGPD | 🚧 US-04 bloquée · 🔲 US-05 |
| **E — Expérience patient** | US-06 Mémoire multi-patient ChromaDB · US-07 Transcription audio Whisper | 🔲 À faire |

L'epic C (Data Engineering) est la priorité actuelle : US-10 ajoute un DAG
Airflow pour orchestrer le pipeline batch nocturne, et US-09 introduit
PySpark pour le calcul de métriques à l'échelle.
