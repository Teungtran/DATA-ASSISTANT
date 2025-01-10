from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from uuid import uuid4
from langchain.chains.question_answering import load_qa_chain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
import warnings
warnings.filterwarnings('ignore')
import chromadb
import os
# ___________________________Set environment variables_____________________________________
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# ________________________________________________________RAG WORKFLOW____________________________________________

def process_pdf(file):
    loader = UnstructuredPDFLoader(file)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
    chunks = text_splitter.split_documents(data)
    # Create vectordb
    embedding_function = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma(
        client=chromadb.PersistentClient(path="db/chroma_store"),
        collection_name="pdf_collection",
        embedding_function=embedding_function,
    )
    documents = [Document(page_content=chunk.page_content, metadata=chunk.metadata) for chunk in chunks]
    vectorstore.add_documents(documents=documents, ids=[str(uuid4()) for _ in documents])
    return vectorstore  

def llm_query(vectorstore, question):
        genllm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
        prompt_template = """
        You are an advanced AI assistant whose name is "Nexus" tasked with answering user {question} based on the provided document's extracted {context}.You can also analyse data from CSV/Excel files reports, database.
        Use the following rules:
        - You can understand both Vietnamses and English 
        - Always utilize all relevant context to generate a complete and accurate response.
        - If the context lacks information, clearly state: "Answer not found in the provided context."
        - Respond in the same language as the input question.
        - Provide structured responses (e.g., lists or bullet points) when applicable for clarity.
        - Prioritize the most relevant information and avoid irrelevant details.
        Context:
        {context}
        Question:
        {question}
        Response:
        """
        human_message = HumanMessagePromptTemplate.from_template(template=prompt_template)
        prompt = ChatPromptTemplate.from_messages([human_message])
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        qa_chain = load_qa_chain(genllm, chain_type="stuff", prompt=prompt, verbose=True)
        retriever_qa = RetrievalQA(combine_documents_chain=qa_chain, retriever=retriever, verbose=True)
        return retriever_qa.invoke(question)

