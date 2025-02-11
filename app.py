import streamlit as st
from huggingface_hub import InferenceClient
import json
import os
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
# MODELO GRATUITO (MODIFICAR SI ES NECESARIO)
# ======================
MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"  # Modelo alternativo recomendado
HF_TOKEN = os.getenv("HF_TOKEN")  # Token de Hugging Face

# ======================
# MANEJO DE CHATS (CORREGIDO)
# ======================
def cargar_chats():
    try:
        if os.path.exists("chats_db.json"):
            with open("chats_db.json", "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error cargando chats: {str(e)}")
        return []

def guardar_chats(chats):
    try:
        with open("chats_db.json", "w") as f:
            json.dump(chats, f, indent=4)
    except Exception as e:
        st.error(f"Error guardando chats: {str(e)}")

# ======================
# FUNCIÓN DE GENERACIÓN (MEJORADA)
# ======================
def generar_respuesta(prompt):
    client = InferenceClient(token=HF_TOKEN)
    
    try:
        response = client.text_generation(
            prompt,
            model=MODEL_NAME,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            timeout=15
        )
        return response
    except Exception as e:
        return f"🚨 Error: {str(e)}"

# ======================
# INTERFAZ DE USUARIO (CORREGIDA)
# ======================
def barra_lateral():
    with st.sidebar:
        st.header("Gestión de Chats")
        
        if st.button("✨ Nuevo Chat", use_container_width=True):
            nuevo_chat = {
                "id": str(datetime.now().timestamp()),
                "titulo": f"Chat {len(st.session_state.chats) + 1}",
                "historial": []
            }
            st.session_state.chats.append(nuevo_chat)
            st.session_state.chat_actual = nuevo_chat
            guardar_chats(st.session_state.chats)
        
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
                    st.session_state.chats.remove(chat)
                    guardar_chats(st.session_state.chats)
                    st.rerun()
        
        st.markdown("---")
        st.caption("v2.1 | Chatbot Gratuito")

def area_chat():
    st.title("🤖 Asistente AI Gratuito")
    
    # Verificar si hay chat activo
    if not st.session_state.chat_actual:
        st.warning("⚠️ Selecciona o crea un nuevo chat desde la barra lateral")
        return
    
    # Mostrar historial
    for mensaje in st.session_state.chat_actual.get("historial", []):
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["contenido"])
    
    # Procesar input
    if prompt := st.chat_input("Escribe tu mensaje..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("Generando respuesta..."):
            respuesta = generar_respuesta(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(respuesta)
            
            # Verificación adicional antes de actualizar
            if st.session_state.chat_actual:
                st.session_state.chat_actual.setdefault("historial", []).extend([
                    {"rol": "user", "contenido": prompt},
                    {"rol": "assistant", "contenido": respuesta}
                ])
                guardar_chats(st.session_state.chats)
            else:
                st.error("Error: No hay chat activo")

# ======================
# INICIALIZACIÓN (CORREGIDA)
# ======================
if "chats" not in st.session_state:
    st.session_state.chats = cargar_chats()
    
if "chat_actual" not in st.session_state:
    if len(st.session_state.chats) > 0:
        st.session_state.chat_actual = st.session_state.chats[0]
    else:
        nuevo_chat = {
            "id": str(datetime.now().timestamp()),
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
# ESTILOS (IGUAL)
# ======================
st.markdown("""
<style>
    [data-testid="stChatMessage"] {
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        background: #1a1d24;
        border: 1px solid #2b313e;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    textarea {
        background: #1a1d24 !important;
        border: 1px solid #2b313e !important;
        color: white !important;
    }
    
    .stButton button {
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        transform: scale(1.05);
        background: #2b313e !important;
    }
</style>
""", unsafe_allow_html=True)