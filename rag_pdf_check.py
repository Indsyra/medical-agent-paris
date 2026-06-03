from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPEN_API_KEY")

# 1. Load the PDF
loader = PyPDFLoader("consultation.pdf")
documents = loader.load()

# 2. Split the text into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(documents)

# 3. Store in Chroma (the card drawer)
embeddings = OpenAIEmbeddings(api_key=api_key, model="text-embedding-3-small")
chroma = Chroma.from_documents(chunks, embeddings)

# 4. The librarian
retriever = chroma.as_retriever(search_kwargs={"k": 3})

# 5. Prompt template for the assistant
template = """Tu es un assistant médical. 
Utilise uniquement le contexte ci-dessous pour répondre.

Contexte : {contexte}
Question : {question}
"""
prompt = PromptTemplate.from_template(template)

# 6. The assistant (the LLM)
llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

chain = (
    {"contexte": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
)

# 7. Ask questions
questions = [
    "Quels médicaments ont été prescrits ?",
    "Quel est l'âge du patient ?",
    "Quand est le prochain rendez-vous ?",
    "Quels sont les antécédents médicaux ?"
]

for q in questions:
    answer = chain.invoke(q)
    print(f"Q: {q}")
    print(f"R: {answer.content}")
    print("---")
