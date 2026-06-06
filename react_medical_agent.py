from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPEN_API_KEY")


class MedicalState(TypedDict):
    raw_text: str
    entities: dict
    soap_summary: str
    verification_ok: bool


llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)


def extract_entities(state: MedicalState):
    prompt = f"""Extrais les informations médicales de ce texte en JSON.
Réponds UNIQUEMENT en JSON, sans texte avant ni après.

Format attendu :
{{
  "patient": "",
  "age": "",
  "symptomes": [],
  "antecedents": [],
  "medicaments": [],
  "examens": []
}}

Texte : {state["raw_text"]}"""

    response = llm.invoke(prompt).content

    try:
        entities = json.loads(response)
    except:
        entities = {}

    return {"entities": entities}


def check_extraction(state: MedicalState):
    entities = state["entities"]
    if not entities or not entities.get("symptomes"):
        return "extract_entities"
    return "structure_soap"


def structure_soap(state: MedicalState):
    entities = state["entities"]
    prompt_soap = f"""
    Tu es un assistant médical. 
    Rédige un compte-rendu en format SOAP (Subjectif, Objectif, Analyse, Plan) en français
    à partir de ces informations:

    {json.dumps(entities, ensure_ascii=False, indent=2)}

    Le compte-rendu doit être clair, structuré et concis.
    S - Subjectif : les symptômes et plaintes du patient.
    O - Objectif : les signes cliniques, examens et résultats.
    A - Analyse : l'interprétation médicale des données.
    P - Plan : les recommandations, traitements et examens complémentaires.
    """

    response = llm.invoke(prompt_soap).content

    return {"soap_summary": response}


def verify_soap(state: MedicalState):
    soap = state["soap_summary"]
    prompt_verify = f"""
    Vérifie que dans ce compte-rendu SOAP, les éléments Subjectif, Objectif, Analyse et Plan sont présents:
    {soap}

    Réponds uniquement par "OK" ou "NOT OK".
    """

    response = llm.invoke(prompt_verify).content.strip()
    if response == "OK":
        return {"verification_ok": True}
    else:
        return {"verification_ok": False, "soap_summary": soap + "\n\n⚠️ Compte-rendu incomplet - À compléter par le médecin"}


graph = StateGraph(MedicalState)
graph.add_node("extract_entities", extract_entities)
graph.set_entry_point("extract_entities")
graph.add_conditional_edges("extract_entities", check_extraction)

graph.add_node("structure_soap", structure_soap)
graph.add_edge("structure_soap", "verify_soap")

graph.add_node("verify_soap", verify_soap)
graph.add_edge("verify_soap", END)

agent = graph.compile()

consultation = """
Jean Dupont, 45 ans. Douleur thoracique ce matin.
Pas d'antécédents cardiaques. Fièvre 38.2°C, tension normale.
ECG en urgence prescrit. Ibuprofène 400mg.
"""

result = agent.invoke({
    "raw_text": consultation,
    "entities": {},
    "soap_summary": "",
    "verification_ok": False
})

print(json.dumps(result["entities"], indent=2, ensure_ascii=False))
print(result["soap_summary"])
print("Vérification SOAP:", "OK" if result["verification_ok"] else "Incomplet")

