import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent # <--- LE NOUVEAU STANDARD
from dotenv import load_dotenv

# Import de nos bases de données
from app.data.vector_db import get_vector_db
from app.data.sql_db import get_db_connection

from dotenv import load_dotenv, find_dotenv
# find_dotenv() va chercher le fichier .env automatiquement dans les dossiers parents/enfants
found = load_dotenv(find_dotenv()) 

if not found:
    print("⚠️ ALERTE : Fichier .env introuvable !")
else:
    print("✅ Fichier .env chargé.")

# --- DÉFINITION DES OUTILS (TOOLS) ---
# On réutilise exactement les mêmes outils, ils sont compatibles
from langchain.tools import tool

@tool
def search_insurance_policy(query: str) -> str:
    """Utiliser cet outil pour répondre aux questions sur les contrats d'assurance, 
    les garanties, les franchises et les conditions générales."""
    vector_db = get_vector_db()
    # On récupère les 2 meilleurs docs
    retriever = vector_db.as_retriever(search_kwargs={"k": 2}) 
    docs = retriever.invoke(query)
    return "\n\n".join([d.page_content for d in docs])

@tool
def get_account_balance(client_name: str) -> str:
    """Utiliser cet outil pour obtenir le solde ou le type de compte d'un client."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT type_compte, solde, devise FROM comptes WHERE client_name = ?", (client_name,))
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return f"Aucun compte trouvé pour le client nommé {client_name}."
    return "\n".join([f"- Compte {row['type_compte']}: {row['solde']} {row['devise']}" for row in results])

# --- CONFIGURATION DE L'AGENT LANGGRAPH ---

# --- CONFIGURATION DE L'AGENT LANGGRAPH ---

def get_agent_executor():
    # 1. Le modèle (Cerveau)
    # On passe sur 'gemini-pro' qui est le modèle le plus stable et compatible
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash-lite-preview-02-05", 
        #model="models/gemini-flash-latest",
        temperature=0
    )
    
    # 2. La liste des outils
    tools = [search_insurance_policy, get_account_balance]
    
    # 3. Création de l'agent
    agent_executor = create_react_agent(llm, tools)
    
    return agent_executor

# --- TEST LOCAL ---
if __name__ == "__main__":
    agent = get_agent_executor()
    
    print("--- TEST 1 : Question Assurance (RAG) ---")
    # LangGraph prend une liste de messages en entrée
    reponse1 = agent.invoke({"messages": [HumanMessage(content="Quelle est la franchise pour le bris de glace ?")]})
    # La réponse se trouve dans le dernier message généré par l'IA
    print(f"RÉPONSE IA : {reponse1['messages'][-1].content}\n")
    
    print("--- TEST 2 : Question Bancaire (SQL) ---")
    reponse2 = agent.invoke({"messages": [HumanMessage(content="Combien d'argent a Alice sur ses comptes ?")]})
    print(f"RÉPONSE IA : {reponse2['messages'][-1].content}")