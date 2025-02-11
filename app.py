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
    page_title="Chatbot Gratuito",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ======================
# MODELO PRINCIPAL (ACTUAL)
# ======================
MODEL_NAME = "microsoft/DialoGPT-large"  # 🚀 Modelo recomendado para diálogo
HF_TOKEN = os.getenv("HF_TOKEN")

# ======================
# MODELOS ALTERNATIVOS (DESCOMENTAR PARA USAR)
# ======================
# MODEL_NAME = "google/flan-t5-xxl"          # 📚 Para preguntas técnicas
# MODEL_NAME = "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5"  # 💡 Asistencia avanzada
# MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"  # ⚡ Respuestas rápidas

# ======================
# CONFIGURACIONES POR MODELO
# ======================
MODEL_CONFIG = {
    "microsoft/DialoGPT-large": {"max_tokens": 150, "temp": 0.9},
    "google/flan-t5-xxl": {"max_tokens": 300, "temp": 0.3},
    "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5": {"max_tokens": 250, "temp": 0.7},
    "HuggingFaceH4/zephyr-7b-beta": {"max_tokens": 200, "temp": 0.6}
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
# FUNCIÓN DE GENERACIÓN
# ======================
def generar_respuesta(prompt):
    client = InferenceClient(token=HF_TOKEN)
    
    try:
        config = MODEL_CONFIG.get(MODEL_NAME, {"max_tokens": 200, "temp": 0.7})
        return client.text_generation(
            prompt,
            model=MODEL_NAME,
            max_new_tokens=config["max_tokens"],
            temperature=config["temp"],
            repetition_penalty=1.1
        )
    except Exception as e:
        if "429" in str(e):
            st.error("⚠️ Límite temporal alcanzado. Espera 1 minuto.")
            time.sleep(60)
            return generar_respuesta(prompt)
        return f"🚨 Error: {str(e)}"

# ======================
# INTERFAZ DE USUARIO
# ======================
def barra_lateral():
    with st.sidebar:
        st.header("Gestión de Chats")
        
        if st.button("✨ Nuevo Chat", use_container_width=True):
            nuevo_chat = {
                "id": str(time.time()),
                "titulo": f"Chat {len(st.session_state.chats) + 1}",
                "historial": []
            }
            st.session_state.chats.append(nuevo_chat)
            st.session_state.chat_actual = nuevo_chat
            guardar_chats(st.session_state.chats)
        
        for chat in st.session_state.chats.copy():
            cols = st.columns([8, 2])
            with cols[0]:
                if st.button(
                    f"💬 {chat['titulo']}",
                    key=f"chat_{chat['id']}",
                    help="Haz clic para abrir este chat",
                    use_container_width=True
                ):
                    st.session_state.chat_actual = chat
            with cols[1]:
                if st.button("❌", key=f"del_{chat['id']}"):
                    try:
                        if st.session_state.chat_actual and st.session_state.chat_actual["id"] == chat["id"]:
                            st.session_state.chat_actual = None
                        st.session_state.chats.remove(chat)
                        guardar_chats(st.session_state.chats)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error eliminando chat: {str(e)}")

        st.markdown("---")
        st.caption(f"Modelo: {MODEL_NAME.split('/')[-1]} | v4.0")

def area_chat():
    st.title("🤖 Asistente AI Gratuito")
    
    if not st.session_state.get("chat_actual"):
        st.warning("Selecciona o crea un chat desde la barra lateral")
        return
    
    for mensaje in st.session_state.chat_actual.get("historial", []):
        with st.chat_message(mensaje.get("rol", "user")):
            st.markdown(mensaje.get("contenido", ""))
    
    if prompt := st.chat_input("Escribe tu mensaje..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("Generando respuesta..."):
            respuesta = generar_respuesta(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(respuesta)
            
            if "historial" not in st.session_state.chat_actual:
                st.session_state.chat_actual["historial"] = []
            
            st.session_state.chat_actual["historial"].extend([
                {"rol": "user", "contenido": prompt},
                {"rol": "assistant", "contenido": respuesta}
            ])
            
            if not guardar_chats(st.session_state.chats):
                st.error("Error guardando la conversación")

# ======================
# INICIALIZACIÓN
# ======================
if "chats" not in st.session_state:
    st.session_state.chats = cargar_chats()

if not hasattr(st.session_state, "chat_actual") or not st.session_state.chat_actual:
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
    [data-testid="stChatMessage"] {
        padding: 1rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        background: #1a1d24;
        border: 1px solid #2b313e;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    
    .stButton>button {
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        background: #2b313e !important;
    }
</style>
""", unsafe_allow_html=True)