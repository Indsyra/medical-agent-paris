# User Stories — Medical Agent Paris

10 User Stories réparties en **5 epics (A → E)**. Statut synchronisé avec le
Kanban GitHub Projects (`Medical Agent Paris — Roadmap`).

Deux vues Mermaid du roadmap sont disponibles dans `docs/roadmap/` :
- [`roadmap-chronological.md`](roadmap/roadmap-chronological.md) — ordre de réalisation (US-01 → US-10)
- [`roadmap-by-epic.md`](roadmap/roadmap-by-epic.md) — vue par epic

---

## Epic A — Agent Core (pipeline LangGraph)

### US-01 — LangGraph agent with 3 nodes ✅ Done
**En tant que** médecin, **je veux** soumettre des notes de consultation en
texte libre, **afin d'**obtenir automatiquement un résumé SOAP structuré.

- Nœuds : `extract_entities` → `structure_soap` → `verify_soap`
- Edge conditionnel qui relance l'extraction si incomplète
- Stack : LangGraph StateGraph, OpenAI gpt-4o-mini, TypedDict `MedicalState`
- Estimation : L (> 6h)

---

## Epic B — API & Déploiement

### US-02 — FastAPI endpoint POST /summarize ✅ Done
**En tant que** développeur, **je veux** exposer l'agent via une API REST,
**afin d'**intégrer l'agent dans n'importe quelle application médicale.

- Endpoint `POST /summarize`, modèles Pydantic `ConsultationRequest` / `ConsultationResponse`
- Doc auto-générée sur `/docs`
- Estimation : S (1-3h)

### US-03 — Docker containerization + Cloud Run deployment ✅ Done
**En tant que** développeur, **je veux** déployer l'agent sur internet,
**afin qu'**il soit accessible depuis n'importe quelle application.

- Docker + Google Container Registry, déploiement Cloud Run (europe-west1)
- URL live : https://medical-agent-paris-756908488363.europe-west1.run.app
- Estimation : M (3-6h)

---

## Epic C — Data Engineering (persistance, orchestration, analytics à l'échelle)

C'est l'epic qui porte la montée en compétence Data Engineering du projet :
Supabase pour la persistance, **Airflow** pour l'orchestration batch, **PySpark**
pour le calcul de métriques à l'échelle.

### US-08 — PostgreSQL logging with Supabase ✅ Done
**En tant que** développeur, **je veux** sauvegarder chaque consultation
traitée en base de données, **afin de** conserver un historique exploitable.

- Table `consultations` (id, input_text, soap_summary, verification_ok, created_at)
- SQLAlchemy + psycopg2-binary, Supabase (EU region), `src/database.py`
- Estimation : S (1-3h)

### US-09 — Monitoring dashboard — usage metrics 🔲 Todo
**En tant que** médecin chef, **je veux** voir les métriques d'utilisation de
l'agent, **afin de** monitorer la qualité des résumés produits.

**Critères d'acceptation**
- [ ] Nombre de consultations par jour
- [ ] Taux de `verification_ok`
- [ ] Temps de réponse moyen
- [ ] Dashboard accessible sur `/metrics`

**Notes techniques**
- Requêtes SQL sur la table `consultations` (Supabase) pour les petits volumes
- **PySpark** pour le calcul des métriques dès que le volume dépasse ce que
  pandas encaisse confortablement (simulateur : générer un jeu de données
  synthétique de plusieurs centaines de milliers de lignes pour justifier le
  passage à Spark en entretien)
- Nouveau endpoint `GET /metrics` dans `src/api.py`
- Visualisation avec Chart.js ou simple JSON

**Compétence Data Engineering visée** : agrégations distribuées (PySpark
DataFrame API, `groupBy`/`agg`), lecture Spark depuis PostgreSQL (JDBC)

- Estimation : M (3-6h)

### US-10 — Batch processing — CSV upload 🔲 Todo
**En tant que** médecin, **je veux** uploader un fichier CSV de consultations,
**afin d'**obtenir tous les résumés SOAP en une seule fois.

**Critères d'acceptation**
- [ ] Endpoint `POST /batch` accepte un fichier CSV
- [ ] Traite chaque ligne comme une consultation
- [ ] Retourne un CSV avec les SOAP générés
- [ ] Gère les erreurs ligne par ligne sans bloquer le batch
- [ ] **Orchestration Airflow** : un DAG déclenche le traitement batch
      automatiquement (ex. tous les soirs à minuit) au lieu d'un appel manuel

**Notes techniques**
- FastAPI `UploadFile` pour réception du CSV, pandas pour lecture/écriture
- Logging de chaque ligne dans Supabase
- **Apache Airflow** : DAG simple (`PythonOperator` ou `BashOperator`) qui
  appelle `/batch` sur un scheduler quotidien ; artefact concret et lisible
  sur un CV (`dags/batch_consultations_dag.py`)

**Compétence Data Engineering visée** : écriture d'un DAG Airflow, scheduling,
gestion des erreurs/retries au niveau orchestration (pas seulement applicatif)

- Estimation : M (3-6h)

---

## Epic D — Observabilité & Conformité

### US-04 — LangSmith monitoring — real-time agent observability 🚧 Blocked
**En tant que** développeur, **je veux** visualiser chaque étape de l'agent en
temps réel, **afin de** déboguer et optimiser les performances.

- `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY`
- Bloqué : erreur 403 persistante sur le Personal Access Token LangSmith
- Estimation : S (1-3h)

### US-05 — GDPR compliance — patient data pseudonymization 🔲 Todo
**En tant que** développeur, **je veux** pseudonymiser les données patient
avant tout appel API externe, **afin d'**être conforme RGPD et HDS.

- Lib : `presidio-analyzer` + `presidio-anonymizer` (Microsoft)
- Pseudonymisation appliquée avant l'appel OpenAI, dans `extract_entities`
- Champ `anonymization_report` ajouté à `ConsultationResponse`
- Estimation : M (3-6h)

---

## Epic E — Expérience patient (mémoire & entrées multimodales)

### US-06 — Multi-patient memory with ChromaDB 🔲 Todo
**En tant que** médecin, **je veux** interroger l'historique de consultations
d'un patient, **afin de** contextualiser le nouveau résumé avec ses antécédents.

- Collection ChromaDB par `patient_id`, RAG sur historique avant `structure_soap`
- Isolation stricte des données par patient
- Estimation : L (> 6h)

### US-07 — Audio transcription support via Whisper API 🔲 Todo
**En tant que** médecin, **je veux** envoyer un fichier audio de consultation,
**afin d'**obtenir un résumé SOAP sans avoir à taper le texte.

- `openai.audio.transcriptions.create()`, endpoint `POST /transcribe`
- Le texte transcrit est automatiquement envoyé à `/summarize`
- Estimation : L (> 6h)

---

## Vue d'ensemble par statut

| Statut | US |
|---|---|
| ✅ Done | US-01, US-02, US-03, US-08 |
| 🔲 Todo | US-05, US-06, US-07, US-09, US-10 |
| 🚧 Blocked | US-04 |
