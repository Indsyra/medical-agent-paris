# Roadmap — Vue par epic

```mermaid
graph TB
    subgraph EpicA["Epic A — Agent Core"]
        US01["US-01<br/>LangGraph agent<br/>3 nodes"]:::done
    end

    subgraph EpicB["Epic B — API &amp; Déploiement"]
        US02["US-02<br/>FastAPI<br/>POST /summarize"]:::done
        US03["US-03<br/>Docker +<br/>Cloud Run"]:::done
    end

    subgraph EpicC["Epic C — Data Engineering"]
        US08["US-08<br/>Supabase<br/>PostgreSQL logging"]:::done
        US09["US-09<br/>PySpark<br/>metrics dashboard"]:::todo
        US10["US-10<br/>Airflow<br/>batch CSV"]:::todo
    end

    subgraph EpicD["Epic D — Observabilité &amp; Conformité"]
        US04["US-04<br/>LangSmith<br/>monitoring"]:::blocked
        US05["US-05<br/>GDPR<br/>pseudonymization"]:::todo
    end

    subgraph EpicE["Epic E — Expérience patient"]
        US06["US-06<br/>ChromaDB<br/>multi-patient memory"]:::todo
        US07["US-07<br/>Whisper<br/>audio transcription"]:::todo
    end

    EpicA --> EpicB --> EpicC
    EpicB --> EpicD
    EpicC --> EpicE

    classDef done fill:#2e7d32,stroke:#1b5e20,color:#fff
    classDef todo fill:#616161,stroke:#424242,color:#fff
    classDef blocked fill:#c62828,stroke:#8e0000,color:#fff
```

**Epic C — Data Engineering** est l'epic à prioriser pour la montée en
compétences visée (Airflow via US-10, PySpark via US-09) : c'est celui qui
transforme le projet d'un "projet perso" en démonstrateur "à l'échelle
hospitalière" sur un CV Data Engineer.

**Légende** : 🟢 Done · ⚪ Todo · 🔴 Blocked
