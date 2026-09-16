"""
Patches the 10 existing GitHub Issues with epic labels, and refreshes the
body of US-09 and US-10 with the Airflow/PySpark Data Engineering notes.

Run this INSTEAD of create_github_issues.py — the issues already exist,
this only updates labels and the two bodies that changed.

Usage:
    python scripts/apply_epic_labels.py

Environment variables (.env): same as create_github_issues.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "Indsyra")
GITHUB_REPO = os.getenv("GITHUB_REPO", "medical-agent-paris")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

BASE_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

EPIC_LABELS = {
    "epic-a-agent-core": "5319e7",
    "epic-b-api-deployment": "0e8a16",
    "epic-c-data-engineering": "fbca04",
    "epic-d-observability-compliance": "1d76db",
    "epic-e-patient-experience": "c5def5",
}

# issue number -> extra labels to add (kept + existing ones, GitHub PATCH
# on /labels replaces the whole set, so we re-add "enhancement"/"blocked" too)
ISSUE_LABELS = {
    1: ["enhancement", "epic-a-agent-core"],                       # US-01
    2: ["enhancement", "epic-b-api-deployment"],                   # US-02
    3: ["enhancement", "epic-b-api-deployment"],                   # US-03
    4: ["enhancement", "epic-c-data-engineering"],                 # US-08
    5: ["enhancement", "blocked", "epic-d-observability-compliance"],  # US-04
    6: ["enhancement", "epic-d-observability-compliance"],         # US-05
    7: ["enhancement", "epic-e-patient-experience"],               # US-06
    8: ["enhancement", "epic-e-patient-experience"],               # US-07
    9: ["enhancement", "epic-c-data-engineering"],                 # US-09
    10: ["enhancement", "epic-c-data-engineering"],                # US-10
}

US09_BODY = """## User Story
En tant que **médecin chef**,
je veux **voir les métriques d'utilisation de l'agent**,
afin de **monitorer la qualité des résumés produits**.

## Critères d'acceptation
- [ ] Nombre de consultations par jour
- [ ] Taux de verification_ok
- [ ] Temps de réponse moyen
- [ ] Dashboard accessible sur `/metrics`

## Notes techniques
- Requêtes SQL sur table consultations (Supabase) pour les petits volumes
- PySpark pour le calcul des métriques dès que le volume dépasse ce que
  pandas encaisse confortablement (JDBC vers PostgreSQL, DataFrame API,
  groupBy/agg) — objectif : montée en compétence Data Engineering
- Nouveau endpoint GET /metrics dans src/api.py
- Visualisation avec Chart.js ou simple JSON

## Estimation
- [ ] M (3-6h)"""

US10_BODY = """## User Story
En tant que **médecin**,
je veux **uploader un fichier CSV de consultations**,
afin d'**obtenir tous les résumés SOAP en une seule fois**.

## Critères d'acceptation
- [ ] Endpoint `POST /batch` accepte un fichier CSV
- [ ] Traite chaque ligne comme une consultation
- [ ] Retourne un CSV avec les SOAP générés
- [ ] Gère les erreurs ligne par ligne sans bloquer le batch
- [ ] Un DAG Airflow orchestre le traitement batch automatiquement (ex.
      tous les soirs à minuit) au lieu d'un déclenchement manuel

## Notes techniques
- FastAPI UploadFile pour reception du CSV
- pandas pour lecture et écriture CSV
- Logging de chaque ligne dans Supabase
- Apache Airflow : DAG (`dags/batch_consultations_dag.py`) qui appelle
  `/batch` sur un scheduler quotidien — objectif : montée en compétence
  Data Engineering (orchestration, scheduling, retries)

## Estimation
- [ ] M (3-6h)"""


def create_label(name: str, color: str) -> None:
    response = requests.post(
        f"{BASE_URL}/labels", json={"name": name, "color": color}, headers=HEADERS
    )
    if response.status_code == 201:
        print(f"  🏷️  Label '{name}' created")
    elif response.status_code == 422:
        print(f"  🏷️  Label '{name}' already exists")
    else:
        print(f"  ⚠️  Label '{name}' — unexpected status {response.status_code}")


def patch_issue(number: int, labels: list[str], body: str | None = None) -> None:
    payload: dict = {"labels": labels}
    if body is not None:
        payload["body"] = body
    response = requests.patch(
        f"{BASE_URL}/issues/{number}", json=payload, headers=HEADERS
    )
    response.raise_for_status()
    print(f"  ✅ Issue #{number} updated (labels{' + body' if body else ''})")


def main() -> None:
    print("Creating epic labels...")
    for name, color in EPIC_LABELS.items():
        create_label(name, color)

    print("\nPatching issues...")
    for number, labels in ISSUE_LABELS.items():
        body = US09_BODY if number == 9 else US10_BODY if number == 10 else None
        patch_issue(number, labels, body)

    print(f"\nDone! View issues at: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/issues")


if __name__ == "__main__":
    main()
