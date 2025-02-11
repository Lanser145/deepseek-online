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
    page_title="Chatbot Avanzado",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ======================
# MODELO PRINCIPAL (ACTUAL)
# ======================
MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"  # ⚡ Modelo moderno recomendado
HF_TOKEN = os.getenv("HF_TOKEN")

# ======================
# CONFIGURACIONES POR MODELO
# ======================
MODEL_CONFIG = {
    "HuggingFaceH4/zephyr-7b-beta": {
        "max_tokens": 512,
        "temp": 0.3,
        "rep_penalty": 1.1
    },
    "microsoft/DialoGPT-large": {"max_tokens": 150, "temp": 0.9},
    "google/flan-t5-xxl": {"max_tokens": 300, "temp": 0.3},
    "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5": {"max_tokens": 250, "temp": 0.7}
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
# FUNCIÓN DE GENERACIÓN MEJORADA
# ======================
def generar_respuesta(prompt):
    client = InferenceClient(token=HF_TOKEN)
    
    # Preprocesamiento del input
    prompt = prompt.strip().replace("\n", " ")
    if not prompt:
        return ""
    
    # Construcción del contexto
    historial = st.session_state.chat_actual.get("historial", [])
    
    # Detección de idioma
    if any(char in prompt for char in "áéíóúñ¿¡"):
        lang_instruction = "Responde en español de manera natural y coloquial."
    else:
        lang_instruction = "Respond in natural, conversational English."
    
    messages = [{
        "role": "system",
        "content": f"Eres un asistente IA útil. {lang_instruction} Sé conciso pero informativo."
    }]
    
    # Agregar historial reciente (últimos 6 intercambios)
    for msg in historial[-6:]:
        messages.append({
            "role": "user" if msg["rol"] == "user" else "assistant",
            "content": msg["contenido"]
        })
    
    messages.append({"role": "user", "content": prompt})
    
    try:
        config = MODEL_CONFIG.get(MODEL_NAME, {"max_tokens": 512, "temp": 0.3})
        response = client.chat_completion(
            messages=messages,
            model=MODEL_NAME,
            max_tokens=config["max_tokens"],
            temperature=config["temp"],
            repetition_penalty=config.get("rep_penalty", 1.1)
        )
        return response.choices[0].message.content
    
    except Exception as e:
        if "429" in str(e):
            st.error("⚠️ Límite de solicitudes alcanzado. Espera 30 segundos...")
            time.sleep(30)
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
        st.caption(f"Modelo: {MODEL_NAME.split('/')[-1]} | v5.1")

def area_chat():
    st.title("🤖 Asistente AI Avanzado")
    
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
# ESTILOS MEJORADOS
# ======================
st.markdown("""
<style>
    [data-testid="stChatMessage"] {
        padding: 1.2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        background: #1a1d24;
        border: 1px solid #2b313e;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: transform 0.2s ease;
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateX(5px);
    }
    
    .stButton>button {
        transition: all 0.3s ease;
        border: 1px solid #3b4252 !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        background: #2b313e !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .stSpinner>div {
        border-color: #4c566a transparent transparent transparent !important;
    }
</style>
""", unsafe_allow_html=True)