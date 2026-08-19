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

# US Complètes (closed)

## US-01 — LangGraph agent with 3 nodes ✅
**En tant que** médecin,
**je veux** soumettre des notes de consultation en texte libre,
**afin d'** obtenir automatiquement un résumé SOAP structuré.

### Critères d'acceptation
- [x] Nœud extract_entities extrait les entités en JSON
- [x] Edge conditionnel relance l'extraction si incomplète
- [x] Nœud structure_soap génère le résumé SOAP
- [x] Nœud verify_soap vérifie la complétude du résumé

### Notes techniques
- LangGraph StateGraph
- OpenAI gpt-4o-mini
- TypedDict MedicalState

### Estimation
- [x] L (> 6h)

---

## US-02 — FastAPI endpoint POST /summarize ✅
**En tant que** développeur,
**je veux** exposer l'agent via une API REST,
**afin d'** intégrer l'agent dans n'importe quelle application médicale.

### Critères d'acceptation
- [x] Endpoint POST /summarize accepte un texte de consultation
- [x] Réponse structurée avec soap_summary et verification_ok
- [x] Documentation automatique disponible sur /docs
- [x] Modèles Pydantic ConsultationRequest et ConsultationResponse

### Notes techniques
- FastAPI + uvicorn
- Pydantic BaseModel
- src/api.py

### Estimation
- [x] S (1-3h)

---

## US-03 — Docker containerization + Cloud Run deployment ✅
**En tant que** développeur,
**je veux** déployer l'agent sur internet,
**afin qu'** il soit accessible depuis n'importe quelle application.

### Critères d'acceptation
- [x] Dockerfile fonctionnel avec port dynamique (PORT env var)
- [x] Image poussée sur Google Container Registry
- [x] Déployé sur Cloud Run europe-west1
- [x] URL publique live et testée

### Notes techniques
- Docker + gcr.io
- gcloud run deploy
- URL : https://medical-agent-paris-756908488363.europe-west1.run.app

### Estimation
- [x] M (3-6h)

---

# US À Faire (open)

## US-04 — LangSmith monitoring
**En tant que** développeur,
**je veux** visualiser chaque étape de l'agent en temps réel,
**afin de** déboguer et optimiser les performances.

### Critères d'acceptation
- [ ] LangSmith connecté à l'agent LangGraph
- [ ] Chaque nœud tracé avec son input/output
- [ ] Les erreurs sont loguées avec le contexte complet
- [ ] Dashboard projet accessible sur smith.langchain.com

### Notes techniques
- LANGCHAIN_TRACING_V2=true
- LANGCHAIN_API_KEY dans .env
- smith.langchain.com → Personal Access Token

### Estimation
- [ ] S (1-3h)

---

## US-05 — GDPR compliance — patient data pseudonymization
**En tant que** développeur,
**je veux** pseudonymiser les données patient avant tout appel API externe,
**afin d'** être conforme RGPD et HDS.

### Critères d'acceptation
- [ ] Les noms, dates de naissance et numéros de sécu sont remplacés par des tokens
- [ ] La pseudonymisation est appliquée avant l'appel OpenAI
- [ ] Un rapport de pseudonymisation est retourné avec la réponse
- [ ] Les données originales ne transitent jamais vers un serveur externe

### Notes techniques
- Lib : presidio-analyzer + presidio-anonymizer (Microsoft)
- Appliquer dans extract_entities avant llm.invoke()
- Ajouter champ anonymization_report dans ConsultationResponse

### Estimation
- [ ] M (3-6h)

---

## US-06 — Multi-patient memory with ChromaDB
**En tant que** médecin,
**je veux** interroger l'historique de consultations d'un patient,
**afin de** contextualiser le nouveau résumé avec ses antécédents.

### Critères d'acceptation
- [ ] Chaque consultation est stockée dans ChromaDB avec un identifiant patient
- [ ] L'agent récupère les consultations précédentes avant de générer le SOAP
- [ ] Le résumé mentionne les évolutions par rapport aux consultations passées
- [ ] Les données sont isolées par patient (pas de mélange)

### Notes techniques
- ChromaDB collection par patient_id
- RAG sur historique avant structure_soap
- Nouveau champ patient_id dans ConsultationRequest

### Estimation
- [ ] L (> 6h)

---

## US-07 — Audio transcription support via Whisper API
**En tant que** médecin,
**je veux** envoyer un fichier audio de consultation,
**afin d'** obtenir un résumé SOAP sans avoir à taper le texte.

### Critères d'acceptation
- [ ] Endpoint POST /transcribe accepte un fichier audio (.mp3, .wav, .m4a)
- [ ] Whisper API transcrit l'audio en texte français
- [ ] Le texte transcrit est automatiquement envoyé à /summarize
- [ ] La réponse contient la transcription + le résumé SOAP

### Notes techniques
- openai.audio.transcriptions.create()
- FastAPI UploadFile pour reception du fichier audio
- Nouveau endpoint POST /transcribe dans src/api.py

### Estimation
- [ ] L (> 6h)
