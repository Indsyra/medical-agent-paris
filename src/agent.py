from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import TypedDict, Literal
import logging
import json
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


class MedicalState(TypedDict):
    raw_text: str
    entities: dict
    soap_summary: str
    verification_ok: bool


class VitalSigns(BaseModel):
    blood_pressure: str = Field(default="", description="Blood pressure, e.g. '150/95 mmHg'. Empty string if not mentioned.")
    heart_rate: str = Field(default="", description="Heart rate, e.g. '110 bpm'. Empty string if not mentioned.")
    temperature: str = Field(default="", description="Temperature, e.g. '38.2°C'. Empty string if not mentioned.")
    oxygen_saturation: str = Field(default="", description="Oxygen saturation, e.g. '94%'. Empty string if not mentioned.")


class ExtractedEntities(BaseModel):
    patient: str = Field(default="", description="Patient name, empty if not mentioned")
    age: str = Field(default="")
    source_language: Literal["french", "english", "other"] = Field(
        description="Main language of the source text — required, always determine this."
    )
    symptoms: list[str] = Field(default_factory=list)
    medical_history: list[str] = Field(default_factory=list)
    vital_signs: VitalSigns = Field(default_factory=VitalSigns)
    medications: list[str] = Field(default_factory=list)
    exams: list[str] = Field(default_factory=list)


llm = ChatOpenAI(model="gpt-4.1-mini", api_key=api_key)
extraction_llm = llm.with_structured_output(ExtractedEntities)

LANGUAGE_LABELS = {
    "french": "French",
    "english": "English",
    "other": "English",  # fallback when source is neither French nor English
}


def extract_entities(state: MedicalState):
    prompt = f"""Extract the medical information from this consultation note.

Strict rules:
- Do not invent any value: if a piece of information is not present in the
  text, leave the field empty. Never guess or approximate a number.
- NEVER translate the extracted values: keep the exact original language of
  the source text for every text field (symptoms, medical history, etc.).
- Identify the main language of the source text (french, english, or other).
- Fill in EVERY sub-field of vital_signs that is mentioned in the text, even
  when several values are given in the same sentence (blood pressure AND
  heart rate AND oxygen saturation AND temperature, if present).

Text: {state["raw_text"]}"""

    try:
        result = extraction_llm.invoke(prompt)
        logger.debug(f"Raw extraction result: {result}")
        entities = result.model_dump()
        logger.info(f"Extracted entities: {entities}")
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        entities = {}

    return {"entities": entities}


def check_extraction(state: MedicalState):
    entities = state["entities"]
    if not entities or not entities.get("symptoms"):
        return "extract_entities"
    return "structure_soap"


def structure_soap(state: MedicalState):
    """Generate the SOAP note.
    """
    entities = state["entities"]
    source_language = entities.get("source_language")
    logger.debug(f"Source language detected: {source_language}")
    output_language = LANGUAGE_LABELS.get(source_language, "English")
    logger.debug(f"Output language set to: {output_language}")

    system_instruction = f"""You are a medical assistant. Your entire response MUST be in {output_language}.
Use {output_language} for every word, including SOAP section headings. Do not write French unless the required output language is French."""
    prompt_soap = f"""Write a SOAP note (Subjective, Objective, Assessment, Plan) from the
following structured information:

{json.dumps(entities, ensure_ascii=False, indent=2)}

The required output language is {output_language}.

Strict rules:
- Start the note with a short two-line patient identification header,
  BEFORE the S/O/A/P sections: one line for the patient's name (label it
  "Patient"), one line for their age (label it "Age", or its equivalent in
  {output_language}). If a value is missing, write "not provided" (or its
  equivalent in {output_language}) — this header is REQUIRED, it is not
  the kind of preamble the next rule is about.
- Beyond that header, respond ONLY with the SOAP note, no other preamble or
  commentary.
- Never include raw text, JSON, quotes, or curly braces in the output.
- Always rephrase in your own words, do not copy the fields verbatim.
- Do not invent or alter ANY numeric value (blood pressure, heart rate,
  temperature, oxygen saturation, dosages). Use exactly the figures provided
  above, nothing else.
- In the Objective section, EXPLICITLY list each vital sign present in
  "vital_signs" with its own clearly labeled value (e.g. "Blood pressure:
  150/95 mmHg", translated into {output_language}) — one per vital sign
  present, not folded vaguely into a general sentence. Do not omit any
  vital sign that is filled in.
- If a piece of data is not filled in the structured information, state that
  explicitly instead of inventing it.

The note must be clear, structured, and concise.
S - Subjective: the patient's symptoms and complaints.
O - Objective: clinical signs, exams, and results.
A - Assessment: the medical interpretation of the data.
P - Plan: recommendations, treatments, and further exams.
"""

    logger.debug(f"SOAP note prompt: {prompt_soap}")
    response = llm.invoke([
        SystemMessage(content=system_instruction),
        HumanMessage(content=prompt_soap),
    ]).content
    logger.debug(f"SOAP note response: {response}")

    return {"soap_summary": response}


def verify_soap(state: MedicalState):
    soap = state["soap_summary"]
    prompt_verify = f"""
    Check that this SOAP note contains the Subjective, Objective, Assessment,
    and Plan sections, regardless of the language used:
    {soap}

    Respond only with "OK" or "NOT OK".
    """
    logger.debug(f"SOAP verification prompt: {prompt_verify}")
    response = llm.invoke(prompt_verify).content.strip()
    if response == "OK":
        logger.debug("SOAP verification: OK")
        return {"verification_ok": True}
    else:
        logger.warning("SOAP verification: NOT OK")
        return {"verification_ok": False, "soap_summary": soap + "\n\nIncomplete note - to be completed by the physician"}


graph = StateGraph(MedicalState)
graph.add_node("extract_entities", extract_entities)
graph.set_entry_point("extract_entities")
graph.add_conditional_edges("extract_entities", check_extraction)

graph.add_node("structure_soap", structure_soap)
graph.add_edge("structure_soap", "verify_soap")

graph.add_node("verify_soap", verify_soap)
graph.add_edge("verify_soap", END)

agent = graph.compile()

if __name__ == "__main__":
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
    print("SOAP verification:", "OK" if result["verification_ok"] else "Incomplete")