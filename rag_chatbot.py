from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# Load and process the PDF document
print("📄 Loading and processing PDF document...")
loader = PyPDFLoader("restaurant_guide.pdf")
documents = loader.load()
print(f"📄 Loaded {len(documents)} pages from the PDF.")

# split the document into smaller chunks
print("✂️ Splitting document into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

chunks = splitter.split_documents(documents)
print(f"✂️ Split into {len(chunks)} chunks.")

# Create embeddings and store in FAISS
print("🔍 Creating embeddings and storing in FAISS...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
print("🔍 Embeddings created and stored.")

# Set up the chatbot with retrieval
print("🤖 Setting up the chatbot...")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    )

prompt =ChatPromptTemplate.from_template("""
You are a customer service assistant for Tasty Bites Restaurant in Dhaka, Bangladesh.
STRICT RULES: 
- ONLY use information provided below. Never make up information.
- If unsure, say: "এই বিষয়ে নিশ্চিত না, 01712-345678 এ call করুন"
- Always respond in Bengali
- Never mention other cities or locations outside of what's given  
                                         
Context: {context}
Question: {question}
""")

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
)

print("🤖 Chatbot is ready! Ask your questions about Tasty Bites Restaurant.\n")

while True:
    user_input = input("Customer: ")
    if user_input.lower() == "exit":
        break

    response = chain.invoke(user_input)
    print(f"Assistant: {response.content}\n")