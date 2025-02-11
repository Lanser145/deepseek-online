import streamlit as st
from huggingface_hub import InferenceClient
import json
import os
import time
from datetime import datetime

# ======================
# CONFIGURACIÓN INICIAL
# ======================
st.set_page_config(
    page_title="Chatbot Estable",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ======================
# MODELO MEJORADO
# ======================
MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"  # Modelo más estable
HF_TOKEN = os.getenv("HF_TOKEN")

# ======================
# CONFIGURACIÓN AVANZADA
# ======================
CONFIG = {
    "max_new_tokens": 120,  # Más corto para mejor coherencia
    "temperature": 0.5,     # Menos aleatoriedad
    "repetition_penalty": 1.2
}

# ======================
# MANEJO DE CHATS
# ======================
CHATS_FILE = "chats_db.json"

def cargar_chats():
    try:
        if os.path.exists(CHATS_FILE):
            with open(CHATS_FILE, "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error cargando chats: {str(e)}")
        return []

def guardar_chats(chats):
    try:
        with open(CHATS_FILE, "w") as f:
            json.dump(chats, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error guardando chats: {str(e)}")
        return False

# ======================
# GENERACIÓN MEJORADA
# ======================
def generar_respuesta(prompt):
    client = InferenceClient(token=HF_TOKEN)
    
    try:
        response = client.text_generation(
            f"<|system|>\nEres un asistente útil en español</s>\n<|user|>\n{prompt}</s>\n<|assistant|>",
            model=MODEL_NAME,
            **CONFIG
        )
        return response.strip()
    except Exception as e:
        if "429" in str(e):
            for i in range(3, 0, -1):
                st.warning(f"⏳ Límite de uso alcanzado. Reintentando en {i}...")
                time.sleep(1)
            return generar_respuesta(prompt)
        return "⚠️ Error temporal. Intenta de nuevo en 1 minuto."

# ======================
# INTERFAZ DE USUARIO
# ======================
def barra_lateral():
    with st.sidebar:
        st.header("Gestión de Chats")
        
        # ... (igual que tu versión anterior)

def area_chat():
    st.title("🤖 Asistente AI Estable")
    
    # ... (igual que tu versión anterior pero con mejoras)

# ======================
# INICIALIZACIÓN
# ======================
if "chats" not in st.session_state:
    st.session_state.chats = cargar_chats()

if not st.session_state.get("chat_actual"):
    if st.session_state.chats:
        st.session_state.chat_actual = st.session_state.chats[0]
    else:
        nuevo_chat = {
            "id": str(time.time()),
            "titulo": "Chat 1",
            "historial": []
        }
        st.session_state.chats.append(nuevo_chat)
        st.session_state.chat_actual = nuevo_chat
        guardar_chats(st.session_state.chats)

# ======================
# EJECUCIÓN
# ======================
barra_lateral()
area_chat()

# ======================
# ESTILOS
# ======================
st.markdown("""
<style>
    /* ... (tus estilos actuales) */
    [data-testid="stSpinner"] {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)