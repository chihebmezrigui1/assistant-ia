import streamlit as st
import requests


st.set_page_config(
    page_title="Assistant Intelligent",
    layout="centered"
)

st.title("Assistant Intelligent")
st.caption("Une intelligence artificielle contextuelle, pilotée par vos documents.")

st.markdown("""
**Comment ça fonctionne ?**  
Cette interface permet d’interroger une base de connaissances via une architecture **RAG (Retrieval-Augmented Generation)**.  

L’assistant analyse les documents fournis, récupère les informations pertinentes, puis génère des réponses fiables et contextualisées.  

Il peut être intégré dans **tout type d’application**, quel que soit le domaine : juridique, RH, technique, éducation, support client, e-commerce, etc.
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

# AFFICHAGE DE L'HISTORIQUE
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ZONE DE SAISIE
if question := st.chat_input("Posez votre question …"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Loaading..."):
            try:
                # On utilise 'assistant_backend' car c'est le container_name dans votre compose
                BACKEND_URL = "http://assistant_backend:8000/ask"
                
                response = requests.post(
                    BACKEND_URL, 
                    json={"query": question.strip()}, 
                    timeout=150 # Augmenté car Mistral peut être lent au premier lancement
                )

                if response.status_code == 200:
                    data = response.json()
                    st.markdown(data["answer"])            
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": data["answer"], 
                    })
                else:
                    st.error(f"Le backend a renvoyé une erreur {response.status_code}")

            except requests.exceptions.RequestException as e:
                st.error(f"Erreur de connexion : Impossible de joindre 'assistant_backend'.")
                st.caption(f"Détail technique : {e}")
                
st.markdown("---")
st.caption("⚡ Powered by Chihab • One brain, every app")
