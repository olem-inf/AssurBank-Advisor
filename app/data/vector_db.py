import os
import shutil
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# Chemins
CURRENT_DIR = os.path.dirname(__file__)
PERSIST_DIRECTORY = os.path.join(CURRENT_DIR, "chroma_db")
DOCS_DIRECTORY = os.path.join(CURRENT_DIR, "documents")

def get_embeddings_model():
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

def init_insurance_knowledge():
    print("⏳ Chargement des documents réels...")
    
    # 1. Vérifier si le dossier existe
    if not os.path.exists(DOCS_DIRECTORY):
        os.makedirs(DOCS_DIRECTORY)
        print(f"⚠️ Dossier '{DOCS_DIRECTORY}' créé. Mettez-y vos PDF !")
        return

    # 2. Charger les fichiers (PDF et TXT)
    # Le DirectoryLoader va scanner tout le dossier
    loader = DirectoryLoader(DOCS_DIRECTORY, glob="**/*.pdf", loader_cls=PyPDFLoader)
    raw_docs = loader.load()
    
    # Si pas de PDF, on tente les TXT
    if not raw_docs:
        loader = DirectoryLoader(DOCS_DIRECTORY, glob="**/*.txt", loader_cls=TextLoader)
        raw_docs = loader.load()

    if not raw_docs:
        print("❌ Aucun document trouvé dans app/data/documents.")
        return

    print(f"   -> {len(raw_docs)} pages lues.")

    # 3. Le Découpage (Chunking) - CRUCIAL POUR LE RAG
    # On ne donne pas 50 pages d'un coup à l'IA. On découpe en morceaux de 1000 caractères.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200, # On garde un peu de contexte entre les morceaux
        add_start_index=True
    )
    chunks = text_splitter.split_documents(raw_docs)
    print(f"   -> Découpé en {len(chunks)} morceaux (chunks) pour l'analyse.")

    # 4. Nettoyage de l'ancienne base
    if os.path.exists(PERSIST_DIRECTORY):
        shutil.rmtree(PERSIST_DIRECTORY)
        print("   -> Ancienne base vectorielle nettoyée.")

    # 5. Création de la nouvelle base
    Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings_model(),
        persist_directory=PERSIST_DIRECTORY,
        collection_name="assurance_rules"
    )
    
    print("✅ Base de connaissances mise à jour avec vos documents !")

def get_vector_db():
    return Chroma(
        persist_directory=PERSIST_DIRECTORY, 
        embedding_function=get_embeddings_model(),
        collection_name="assurance_rules"
    )

if __name__ == "__main__":
    init_insurance_knowledge()