from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def appeler_gpt(texte_consultation):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es un assistant médical. Tu résumes des consultations médicales en français de façon claire et structurée."},
            {"role": "user", "content": f"Voici la consultation à résumer : \n\n{texte_consultation}"}
        ]
    )
    return response.choices[0].message.content
