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
# MODELO GRATUITO
# ======================
MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"
HF_TOKEN = os.getenv("HF_TOKEN")

# ======================
# MANEJO DE CHATS (CORREGIDO)
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
        return client.text_generation(
            prompt,
            model=MODEL_NAME,
            max_new_tokens=150,
            temperature=0.7,
            timeout=10
        )
    except Exception as e:
        return f"🚨 Error: {str(e)}"

# ======================
# INTERFAZ DE USUARIO (CORREGIDA)
# ======================
def barra_lateral():
    with st.sidebar:
        st.header("Gestión de Chats")
        
        # Botón nuevo chat
        if st.button("✨ Nuevo Chat", use_container_width=True):
            nuevo_chat = {
                "id": str(time.time()),
                "titulo": f"Chat {len(st.session_state.chats) + 1}",
                "historial": []
            }
            st.session_state.chats.append(nuevo_chat)
            st.session_state.chat_actual = nuevo_chat
            guardar_chats(st.session_state.chats)
        
        # Lista de chats
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
                        # Verificar si es el chat actual
                        if st.session_state.chat_actual and st.session_state.chat_actual["id"] == chat["id"]:
                            st.session_state.chat_actual = None
                        st.session_state.chats.remove(chat)
                        guardar_chats(st.session_state.chats)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error eliminando chat: {str(e)}")

        st.markdown("---")
        st.caption("v3.1 | Chatbot Estable")

def area_chat():
    st.title("🤖 Asistente AI Gratuito")
    
    # Verificación robusta del chat actual
    if not st.session_state.get("chat_actual"):
        st.warning("⚠️ Crea o selecciona un chat desde la barra lateral")
        return
    
    # Mostrar historial con verificación
    for mensaje in st.session_state.chat_actual.get("historial", []):
        with st.chat_message(mensaje.get("rol", "user")):
            st.markdown(mensaje.get("contenido", ""))
    
    # Procesar mensaje
    if prompt := st.chat_input("Escribe tu mensaje..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("Generando respuesta..."):
            respuesta = generar_respuesta(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(respuesta)
            
            # Actualizar historial con verificación
            if "historial" not in st.session_state.chat_actual:
                st.session_state.chat_actual["historial"] = []
            
            st.session_state.chat_actual["historial"].extend([
                {"rol": "user", "contenido": prompt},
                {"rol": "assistant", "contenido": respuesta}
            ])
            
            if not guardar_chats(st.session_state.chats):
                st.error("Error guardando la conversación")

# ======================
# INICIALIZACIÓN ROBUSTA (CORREGIDA)
# ======================
if "chats" not in st.session_state:
    st.session_state.chats = cargar_chats()

# Garantizar que siempre haya un chat activo
if not hasattr(st.session_state, "chat_actual") or not st.session_state.chat_actual:
    if len(st.session_state.chats) > 0:
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
# EJECUCIÓN PRINCIPAL
# ======================
barra_lateral()
area_chat()

# ======================
# ESTILOS MEJORADOS
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
        transition: transform 0.2s ease, background 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.03);
        background: #2b313e !important;
    }
</style>
""", unsafe_allow_html=True)