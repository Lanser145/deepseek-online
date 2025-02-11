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
# MODELO GRATUITO (ACTUALIZADO)
# ======================
MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"  # Modelo gratuito y sin restricciones
HF_TOKEN = os.getenv("HF_TOKEN")

# ======================
# MANEJO DE CHATS (MEJORADO)
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
# FUNCIÓN DE GENERACIÓN (CON CONTROL DE ERRORES)
# ======================
def generar_respuesta(prompt):
    client = InferenceClient(token=HF_TOKEN)
    
    try:
        response = client.text_generation(
            prompt,
            model=MODEL_NAME,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True,
            timeout=10
        )
        return response
    
    except Exception as e:
        if "429" in str(e):
            st.error("⚠️ Límite de solicitudes alcanzado. Espera 1 minuto.")
            time.sleep(60)
            return generar_respuesta(prompt)
        else:
            return f"🚨 Error: {str(e)}"

# ======================
# INTERFAZ DE USUARIO (CORREGIDA)
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
            if not guardar_chats(st.session_state.chats):
                st.error("Error guardando el nuevo chat")

        for chat in st.session_state.chats:
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
                        st.session_state.chats.remove(chat)
                        if not guardar_chats(st.session_state.chats):
                            st.error("Error eliminando chat")
                        st.rerun()
                    except ValueError:
                        st.error("Chat no encontrado")

        st.markdown("---")
        st.caption("v3.0 | Chatbot Estable")

def area_chat():
    st.title("🤖 Asistente AI Gratuito")
    
    if not st.session_state.get("chat_actual"):
        st.warning("Selecciona o crea un chat desde la barra lateral")
        return
    
    try:
        for mensaje in st.session_state.chat_actual["historial"]:
            with st.chat_message(mensaje["rol"]):
                st.markdown(mensaje["contenido"])
    except KeyError:
        st.session_state.chat_actual["historial"] = []
    
    if prompt := st.chat_input("Escribe tu mensaje..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        try:
            with st.spinner("Generando respuesta..."):
                respuesta = generar_respuesta(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(respuesta)
            
            nuevo_mensaje = {
                "user": prompt,
                "assistant": respuesta
            }
            
            st.session_state.chat_actual["historial"].extend([
                {"rol": "user", "contenido": prompt},
                {"rol": "assistant", "contenido": respuesta}
            ])
            
            if not guardar_chats(st.session_state.chats):
                st.error("Error guardando la conversación")
        
        except Exception as e:
            st.error(f"Error crítico: {str(e)}")

# ======================
# INICIALIZACIÓN ROBUSTA
# ======================
if "chats" not in st.session_state:
    st.session_state.chats = cargar_chats() or []

if "chat_actual" not in st.session_state:
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
# EJECUCIÓN PRINCIPAL
# ======================
barra_lateral()
area_chat()

# ======================
# ESTILOS (MEJORADOS)
# ======================
st.markdown("""
<style>
    [data-testid="stChatMessage"] {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        background: #1E1E1E;
        border: 1px solid #333;
    }
    
    .stButton>button {
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        background: #2A2A2A !important;
    }
    
    [data-testid="stStatusWidget"] {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)