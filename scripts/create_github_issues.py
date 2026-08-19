"""
GitHub Issues creation script.
Creates all User Stories as GitHub Issues automatically.

Usage:
    python scripts/create_github_issues.py

Requirements:
    pip install requests python-dotenv

Environment variables (.env):
    GITHUB_TOKEN=your_github_personal_access_token
    GITHUB_OWNER=Indsyra
    GITHUB_REPO=medical-agent-paris
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "Indsyra")
GITHUB_REPO = os.getenv("GITHUB_REPO", "medical-agent-paris")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

BASE_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

ISSUES = [
    # ── DONE ──────────────────────────────────────────────────────────────
    {
        "title": "[US-01] LangGraph agent with 3 nodes",
        "body": """## User Story
En tant que **médecin**,
je veux **soumettre des notes de consultation en texte libre**,
afin d'**obtenir automatiquement un résumé SOAP structuré**.

## Critères d'acceptation
- [x] Nœud `extract_entities` extrait les entités en JSON
- [x] Edge conditionnel relance l'extraction si incomplète
- [x] Nœud `structure_soap` génère le résumé SOAP
- [x] Nœud `verify_soap` vérifie la complétude du résumé

## Notes techniques
- LangGraph StateGraph
- OpenAI gpt-4o-mini
- TypedDict MedicalState

## Estimation
- [x] L (> 6h)""",
        "labels": ["enhancement"],
        "state": "closed"
    },
    {
        "title": "[US-02] FastAPI endpoint POST /summarize",
        "body": """## User Story
En tant que **développeur**,
je veux **exposer l'agent via une API REST**,
afin d'**intégrer l'agent dans n'importe quelle application médicale**.

## Critères d'acceptation
- [x] Endpoint `POST /summarize` accepte un texte de consultation
- [x] Réponse structurée avec `soap_summary` et `verification_ok`
- [x] Documentation automatique disponible sur `/docs`
- [x] Modèles Pydantic `ConsultationRequest` et `ConsultationResponse`

## Notes techniques
- FastAPI + uvicorn
- Pydantic BaseModel
- src/api.py

## Estimation
- [x] S (1-3h)""",
        "labels": ["enhancement"],
        "state": "closed"
    },
    {
        "title": "[US-03] Docker containerization + Cloud Run deployment",
        "body": """## User Story
En tant que **développeur**,
je veux **déployer l'agent sur internet**,
afin qu'**il soit accessible depuis n'importe quelle application**.

## Critères d'acceptation
- [x] Dockerfile fonctionnel avec port dynamique (PORT env var)
- [x] Image poussée sur Google Container Registry
- [x] Déployé sur Cloud Run europe-west1
- [x] URL publique live et testée

## Notes techniques
- Docker + gcr.io
- gcloud run deploy
- URL : https://medical-agent-paris-756908488363.europe-west1.run.app

## Estimation
- [x] M (3-6h)""",
        "labels": ["enhancement"],
        "state": "closed"
    },
    {
        "title": "[US-08] PostgreSQL logging with Supabase",
        "body": """## User Story
En tant que **développeur**,
je veux **sauvegarder chaque consultation traitée en base de données**,
afin de **conserver un historique exploitable**.

## Critères d'acceptation
- [x] Table `consultations` avec id, input_text, soap_summary, verification_ok, created_at
- [x] Chaque appel à `/summarize` insère une ligne
- [x] PostgreSQL + SQLAlchemy + Supabase

## Notes techniques
- SQLAlchemy + psycopg2-binary
- Supabase (EU region)
- src/database.py

## Estimation
- [x] S (1-3h)""",
        "labels": ["enhancement"],
        "state": "closed"
    },
    # ── OPEN ───────────────────────────────────────────────────────────────
    {
        "title": "[US-04] LangSmith monitoring — real-time agent observability",
        "body": """## User Story
En tant que **développeur**,
je veux **visualiser chaque étape de l'agent en temps réel**,
afin de **déboguer et optimiser les performances**.

## Critères d'acceptation
- [ ] LangSmith connecté à l'agent LangGraph
- [ ] Chaque nœud tracé avec son input/output
- [ ] Les erreurs sont loguées avec le contexte complet
- [ ] Dashboard projet accessible sur smith.langchain.com

## Notes techniques
- LANGCHAIN_TRACING_V2=true
- LANGCHAIN_API_KEY dans .env
- smith.langchain.com → Personal Access Token

## Estimation
- [ ] S (1-3h)""",
        "labels": ["enhancement", "blocked"],
        "state": "open"
    },
    {
        "title": "[US-05] GDPR compliance — patient data pseudonymization",
        "body": """## User Story
En tant que **développeur**,
je veux **pseudonymiser les données patient avant tout appel API externe**,
afin d'**être conforme RGPD et HDS**.

## Critères d'acceptation
- [ ] Les noms, dates de naissance et numéros de sécu sont remplacés par des tokens
- [ ] La pseudonymisation est appliquée avant l'appel OpenAI
- [ ] Un rapport de pseudonymisation est retourné avec la réponse
- [ ] Les données originales ne transitent jamais vers un serveur externe

## Notes techniques
- Lib : presidio-analyzer + presidio-anonymizer (Microsoft)
- Appliquer dans extract_entities avant llm.invoke()
- Ajouter champ anonymization_report dans ConsultationResponse

## Estimation
- [ ] M (3-6h)""",
        "labels": ["enhancement"],
        "state": "open"
    },
    {
        "title": "[US-06] Multi-patient memory with ChromaDB",
        "body": """## User Story
En tant que **médecin**,
je veux **interroger l'historique de consultations d'un patient**,
afin de **contextualiser le nouveau résumé avec ses antécédents**.

## Critères d'acceptation
- [ ] Chaque consultation est stockée dans ChromaDB avec un identifiant patient
- [ ] L'agent récupère les consultations précédentes avant de générer le SOAP
- [ ] Le résumé mentionne les évolutions par rapport aux consultations passées
- [ ] Les données sont isolées par patient (pas de mélange)

## Notes techniques
- ChromaDB collection par patient_id
- RAG sur historique avant structure_soap
- Nouveau champ patient_id dans ConsultationRequest

## Estimation
- [ ] L (> 6h)""",
        "labels": ["enhancement"],
        "state": "open"
    },
    {
        "title": "[US-07] Audio transcription support via Whisper API",
        "body": """## User Story
En tant que **médecin**,
je veux **envoyer un fichier audio de consultation**,
afin d'**obtenir un résumé SOAP sans avoir à taper le texte**.

## Critères d'acceptation
- [ ] Endpoint `POST /transcribe` accepte un fichier audio (.mp3, .wav, .m4a)
- [ ] Whisper API transcrit l'audio en texte français
- [ ] Le texte transcrit est automatiquement envoyé à `/summarize`
- [ ] La réponse contient la transcription + le résumé SOAP

## Notes techniques
- openai.audio.transcriptions.create()
- FastAPI UploadFile pour reception du fichier audio
- Nouveau endpoint POST /transcribe dans src/api.py

## Estimation
- [ ] L (> 6h)""",
        "labels": ["enhancement"],
        "state": "open"
    },
    {
        "title": "[US-09] Monitoring dashboard — usage metrics",
        "body": """## User Story
En tant que **médecin chef**,
je veux **voir les métriques d'utilisation de l'agent**,
afin de **monitorer la qualité des résumés produits**.

## Critères d'acceptation
- [ ] Nombre de consultations par jour
- [ ] Taux de verification_ok
- [ ] Temps de réponse moyen
- [ ] Dashboard accessible sur `/metrics`

## Notes techniques
- Requêtes SQL sur table consultations (Supabase)
- Nouveau endpoint GET /metrics dans src/api.py
- Visualisation avec Chart.js ou simple JSON

## Estimation
- [ ] M (3-6h)""",
        "labels": ["enhancement"],
        "state": "open"
    },
    {
        "title": "[US-10] Batch processing — CSV upload",
        "body": """## User Story
En tant que **médecin**,
je veux **uploader un fichier CSV de consultations**,
afin d'**obtenir tous les résumés SOAP en une seule fois**.

## Critères d'acceptation
- [ ] Endpoint `POST /batch` accepte un fichier CSV
- [ ] Traite chaque ligne comme une consultation
- [ ] Retourne un CSV avec les SOAP générés
- [ ] Gère les erreurs ligne par ligne sans bloquer le batch

## Notes techniques
- FastAPI UploadFile pour reception du CSV
- pandas pour lecture et écriture CSV
- Logging de chaque ligne dans Supabase

## Estimation
- [ ] M (3-6h)""",
        "labels": ["enhancement"],
        "state": "open"
    }
]


def create_label(name: str, color: str) -> None:
    """Create a label if it doesn't exist."""
    url = f"{BASE_URL}/labels"
    response = requests.post(
        url,
        json={"name": name, "color": color},
        headers=HEADERS
    )
    if response.status_code == 201:
        print(f"  🏷️  Label '{name}' created")
    elif response.status_code == 422:
        print(f"  🏷️  Label '{name}' already exists")


def create_issue(issue: dict) -> int:
    """Create a GitHub issue and return its number."""
    url = f"{BASE_URL}/issues"
    payload = {
        "title": issue["title"],
        "body": issue["body"],
        "labels": issue["labels"]
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    issue_number = response.json()["number"]
    print(f"  ✅ Created issue #{issue_number}: {issue['title']}")
    return issue_number


def close_issue(issue_number: int) -> None:
    """Close a GitHub issue."""
    url = f"{BASE_URL}/issues/{issue_number}"
    response = requests.patch(
        url,
        json={"state": "closed"},
        headers=HEADERS
    )
    response.raise_for_status()
    print(f"  🔒 Closed issue #{issue_number}")


def main() -> None:
    print("Creating GitHub Issues...")
    print(f"Repo: {GITHUB_OWNER}/{GITHUB_REPO}\n")

    # Create labels
    print("Creating labels...")
    create_label("enhancement", "a2eeef")
    create_label("blocked", "d93f0b")
    print()

    # Create issues
    print("Creating issues...")
    for issue in ISSUES:
        issue_number = create_issue(issue)
        if issue.get("state") == "closed":
            close_issue(issue_number)

    print(f"\nDone! {len(ISSUES)} issues created.")
    print(f"View them at: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/issues")


if __name__ == "__main__":
    main()
