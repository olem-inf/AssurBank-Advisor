import os
from dotenv import load_dotenv
import google.generativeai as genai

# Charger la clé
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Erreur : Clé API non trouvée dans le fichier .env")
else:
    print(f"✅ Clé trouvée : {api_key[:5]}...*****")
    
    # Configuration
    genai.configure(api_key=api_key)
    
    print("\n🔍 Recherche des modèles disponibles pour votre clé...")
    try:
        models = list(genai.list_models())
        found = False
        for m in models:
            # On cherche les modèles qui peuvent "generateContent" (les Chatbots)
            if 'generateContent' in m.supported_generation_methods:
                print(f"   - {m.name}")
                found = True
        
        if not found:
            print("❌ Aucun modèle de chat trouvé. Votre clé a peut-être des restrictions.")
            
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")