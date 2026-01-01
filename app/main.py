import os
import time
from typing import List

from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel

# Désactivation télémétrie Chroma
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from langchain_mistralai import ChatMistralAI
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from chromadb.config import Settings



# Clé API via variable d’environnement UNIQUEMENT
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise RuntimeError("❌ MISTRAL_API_KEY non configurée")

# Modèle Mistral officiel 
llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0.1,
    mistral_api_key=MISTRAL_API_KEY
)

# Embeddings locaux 
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Base vectorielle locale (sans télémétrie)
vector_db = Chroma(
    persist_directory="./db",
    embedding_function=embeddings,
    client_settings=Settings(anonymized_telemetry=False)
)

# 2. Prompt médical 

RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "Tu es un assistant IA intelligent basé sur une architecture RAG.\n\n"
        "RÈGLES IMPORTANTES :\n"
        "- Utilise PRIORITAIREMENT le CONTEXTE fourni s’il est pertinent.\n"
        "- Si le contexte est insuffisant, répond avec des connaissances générales fiables.\n"
        "- Ne devine pas les informations absentes.\n"
        "- Réponds de manière claire, structurée et professionnelle.\n\n"
        "CONTEXTE (extraits de documents) :\n{context}\n\n"
        "QUESTION UTILISATEUR :\n{question}\n\n"
        "RÉPONSE FINALE :"
    )
)

def create_qa_chain():
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": RAG_PROMPT}
    )

qa_chain = create_qa_chain()

# 3. API FastAPI

app = FastAPI(title="Assistant Intelligent")

class Question(BaseModel):
    query: str

@app.get("/health")
def health_check():
    try:
        ids = vector_db.get()["ids"]
        return {
            "status": "healthy",
            "vector_db_docs": len(ids) if ids else 0,
            "llm_provider": "Mistral AI (Official)",
            "model": "mistral-large-latest"
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/ask")
def ask(question: Question):
    if not question.query.strip():
        raise HTTPException(status_code=400, detail="Question vide")

    print(f"--- Question envoyée à Mistral : {question.query} ---")
    start_time = time.time()

    try:
        result = qa_chain.invoke({"query": question.query})

        elapsed_time = time.time() - start_time
        print(f"Réponse reçue en {elapsed_time:.2f}s")

        return {
            "answer": result["result"].strip(),
            "processing_time": f"{elapsed_time:.2f}s"
        }

    except Exception as e:
        print(f"❌ ERREUR MISTRAL : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest-pdf")
async def ingest_pdf(
    document_name: str = Form(...),
    chunks: List[str] = Form(...)
):
    try:
        docs = [
            Document(
                page_content=c,
                metadata={"source": document_name, "page": i + 1}
            )
            for i, c in enumerate(chunks)
        ]

        vector_db.add_documents(docs)

        global qa_chain
        qa_chain = create_qa_chain()

        return {
            "status": "success",
            "message": f"{len(docs)} chunks ajoutés à la base"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
