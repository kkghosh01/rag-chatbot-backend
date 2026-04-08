from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import tempfile
import os

load_dotenv()

app = FastAPI()

# React থেকে request আসতে দেওয়ার জন্য
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://rag-chatbot-backend-cipn.onrender.com",  
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
vectorstore = None
embeddings = None

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant. Answer based ONLY on the context below.
If the answer is not in context, say "এই তথ্য আমার কাছে নেই।"
Answer in Bengali.

Context: {context}
Question: {question}
""")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


@app.on_event("startup")
async def startup_event():
    global vectorstore, embeddings
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    if os.path.exists("restaurant_guide.pdf"):
        loader = PyPDFLoader("restaurant_guide.pdf")
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50
        )
        chunks = splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(chunks, embeddings)
        print("✓ PDF auto-loaded!")

# ── Route 1: PDF upload ──
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vectorstore

    # PDF টা temp file এ save করো
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # RAG pipeline
    loader = PyPDFLoader(tmp_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)

    vectorstore = FAISS.from_documents(chunks, embeddings)
    os.unlink(tmp_path)

    return {"message": f"PDF processed! {len(chunks)} chunks ready."}

# ── Route 2: Question ask ──
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    if vectorstore is None:
        return {"answer": "আগে একটা PDF upload করুন।"}

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    chain = (
        {"context": retriever | format_docs, 
         "question": RunnablePassthrough()}
        | prompt
        | llm
    )

    response = chain.invoke(request.question)
    return {"answer": response.content}

# ── Route 3: Health check ──
@app.get("/")
def root():
    return {"status": "API is running!"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)