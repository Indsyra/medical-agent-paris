from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def appeler_gpt(texte_consultation, specialite, nom_patient):
    template = """
    Tu es un assistant médical en {specialite}. 
    Résume la consultation de {nom_patient} en français de façon claire et structurée. 

    Consultation : 
    {texte_consultation}
    """
    prompt_template = PromptTemplate.from_template(
        template,
    )

    llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")
    llm_chain = prompt_template | llm
    return llm_chain.invoke({
        "texte_consultation": texte_consultation,
        "specialite": specialite,
        "nom_patient": nom_patient
    }).content
