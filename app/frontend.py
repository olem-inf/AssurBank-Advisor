import streamlit as st
import requests
import os
import sys
from dotenv import load_dotenv

# --- CONFIGURATION INITIALE ---
# On charge les variables d'environnement (pour le Local)
load_dotenv()

# Ajustement du chemin pour les imports (Crucial pour le Cloud)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="AssurBank Advisor", page_icon="🏦", layout="wide")

# --- DÉTECTION DU MODE ---
# Par défaut, on cherche une API locale
DEFAULT_API_URL = "http://127.0.0.1:8000/chat"
API_URL = os.getenv("API_URL", DEFAULT_API_URL)

# On décide du mode via une variable d'env, ou on teste la connexion
# Valeurs possibles pour ENV_MODE : "LOCAL" ou "CLOUD"
MODE = os.getenv("ENV_MODE", "AUTO")

# --- BARRE LATÉRALE (DASHBOARD) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=50)
    st.title("🔧 Configuration")
    
    st.markdown("---")
    
    # Indicateur de statut
    status_placeholder = st.empty()
    
    st.markdown("### 📚 Base de connaissances")
    st.info("Documents chargés : Contrats Habitation & Auto")
    
    st.markdown("---")
    st.caption(f"v1.2.0 - AssurBank Advisor")

# --- LOGIQUE DU CERVEAU (HYBRIDE) ---
def get_ai_response(user_query, user_id):
    """
    Fonction intelligente qui choisit la meilleure méthode
    pour obtenir la réponse (API ou Direct).
    """
    
    # 1. Essai via API (Priorité en Local)
    if MODE != "CLOUD":
        try:
            with st.sidebar:
                status_placeholder.success("🟢 Mode : API CONNECTÉE (Local)")
            
            response = requests.post(
                API_URL, 
                json={"query": user_query, "user_id": user_id},
                timeout=5 # On attend max 5 secondes
            )
            
            if response.status_code == 200:
                return response.json().get("answer")
            else:
                st.error(f"Erreur API ({response.status_code})")
                return None
                
        except requests.exceptions.ConnectionError:
            # Si l'API ne répond pas, on passe au plan B (sauf si on a forcé le mode LOCAL)
            if MODE == "LOCAL":
                st.error("❌ Serveur API introuvable. Veuillez lancer 'python -m app.server'")
                return "Erreur de connexion serveur."
            pass # On continue vers le mode Direct

    # 2. Mode Direct / Cloud (Fallback)
    # C'est ici que l'application charge l'agent en mémoire interne
    try:
        with st.sidebar:
            status_placeholder.info("☁️ Mode : CLOUD (Autonome)")
            
        # Import Lazy : On n'importe l'agent que si on en a besoin (économie de mémoire)
        from app.agent import get_agent_executor
        from langchain_core.messages import HumanMessage
        
        # Cache pour éviter de recharger le modèle à chaque clic
        if "agent_executor" not in st.session_state:
            with st.spinner("Initialisation du cerveau IA en cours..."):
                st.session_state.agent_executor = get_agent_executor()
        
        # Invocation directe
        response = st.session_state.agent_executor.invoke(
            {"messages": [HumanMessage(content=user_query)]}
        )
        return response["messages"][-1].content
        
    except Exception as e:
        st.sidebar.error("❌ Erreur Critique")
        return f"Désolé, une erreur interne est survenue : {str(e)}"

# --- INTERFACE PRINCIPALE ---
st.title("🏦 AssurBank Advisor")
st.markdown("""
Bonjour ! Je suis votre assistant bancaire et assurance.  
*Posez-moi des questions sur vos comptes ou vos contrats.*
""")

# Gestion de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Message de bienvenue
    st.session_state.messages.append({"role": "assistant", "content": "Bonjour Alice 👋 ! Comment puis-je vous aider aujourd'hui ?"})

# Affichage des messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Zone de saisie
if prompt := st.chat_input("Ex: Quel est mon solde ? / Franchise bris de glace ?"):
    
    # 1. Afficher la question utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Obtenir et afficher la réponse
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ *Analyse en cours...*")
        
        response = get_ai_response(prompt, "Alice")
        
        if response:
            message_placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            message_placeholder.markdown("⚠️ *Pas de réponse disponible.*")