from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import uvicorn

# On importe notre cerveau (l'agent qu'on a créé précédemment)
from app.agent import get_agent_executor

# Initialisation de l'application FastAPI
app = FastAPI(
    title="AssurBank AI API",
    description="API REST pour l'assistant bancaire intelligent (RAG + SQL)",
    version="1.0.0"
)

# --- MODÈLES DE DONNÉES (Sécurité & Validation) ---
class ChatRequest(BaseModel):
    query: str
    user_id: str = "Alice"  # Par défaut pour le PoC

class ChatResponse(BaseModel):
    answer: str
    # On pourrait ajouter ici les sources utilisées (metadata)

# --- CHARGEMENT DE L'AGENT ---
# On le charge au démarrage pour éviter de le recréer à chaque requête
try:
    agent_executor = get_agent_executor()
    print("✅ Agent IA chargé avec succès.")
except Exception as e:
    print(f"❌ Erreur critique au chargement de l'agent : {e}")

# --- ROUTES API ---

@app.get("/")
def home():
    """Vérifier que l'API est en ligne."""
    return {"status": "online", "message": "Bienvenue sur AssurBank AI"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Point d'entrée principal pour discuter avec l'IA.
    Reçoit une question JSON, renvoie une réponse JSON.
    """
    if not agent_executor:
        raise HTTPException(status_code=503, detail="L'agent IA n'est pas disponible.")

    try:
        print(f"📩 Question reçue de {request.user_id}: {request.query}")
        
        # 1. On envoie le message à LangGraph
        response = agent_executor.invoke(
            {"messages": [HumanMessage(content=request.query)]}
        )
        
        # 2. On extrait la dernière réponse de l'IA (le dernier message)
        final_answer = response["messages"][-1].content
        
        return ChatResponse(answer=final_answer)

    except Exception as e:
        print(f"❌ Erreur lors du traitement : {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- LANCEMENT (Si exécuté directement) ---
if __name__ == "__main__":
    # Lance le serveur sur le port 8000
    uvicorn.run("app.server:app", host="127.0.0.1", port=8000, reload=True)