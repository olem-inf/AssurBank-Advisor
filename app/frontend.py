import os
import streamlit as st
import requests

# Titre de la page
st.set_page_config(page_title="AssurBank Advisor", page_icon="🏦")
st.title("🏦 AssurBank Advisor")
st.markdown("Votre assistant intelligent pour la Banque et l'Assurance.")

# URL DYNAMIQUE : Si on est dans Docker, on utilise la variable d'env, sinon localhost
DEFAULT_API_URL = "http://127.0.0.1:8000/chat"
API_URL = os.getenv("API_URL", DEFAULT_API_URL)

# --- GESTION DE LA MÉMOIRE (Session) ---
# Pour que l'historique de chat ne disparaisse pas à chaque message
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les anciens messages à l'écran
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ZONE DE SAISIE ---
if prompt := st.chat_input("Posez votre question (ex: Solde d'Alice ? Franchise ?)..."):
    
    # 1. Afficher le message de l'utilisateur tout de suite
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # On ajoute à l'historique local
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Appeler l'API (Le Cerveau)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ *Réflexion en cours...*")
        
        try:
            # Envoi de la requête au serveur FastAPI
            payload = {"query": prompt, "user_id": "StreamlitUser"}
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                answer = response.json().get("answer", "Pas de réponse.")
                message_placeholder.markdown(answer)
                # On ajoute la réponse à l'historique
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                message_placeholder.error(f"Erreur API : {response.status_code}")
                
        except Exception as e:
            message_placeholder.error(f"Impossible de contacter le serveur : {e}")