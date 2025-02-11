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
# MODELO GRATUITO
# ======================
MODEL_NAME = "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5"  # Modelo de diálogo
HF_TOKEN = os.getenv("HF_TOKEN")  # Token gratuito de Hugging Face

# ======================
# MANEJO DE CHATS
# ======================
def cargar_chats():
    """Carga el historial de chats desde un archivo JSON"""
    try:
        if os.path.exists("chats_db.json"):
            with open("chats_db.json", "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error cargando chats: {str(e)}")
        return []

def guardar_chats(chats):
    """Guarda el historial de chats en un archivo JSON"""
    try:
        with open("chats_db.json", "w") as f:
            json.dump(chats, f, indent=4)
    except Exception as e:
        st.error(f"Error guardando chats: {str(e)}")

# ======================
# FUNCIÓN DE GENERACIÓN
# ======================
def generar_respuesta(prompt):
    """Genera respuesta usando modelo gratuito de Hugging Face"""
    client = InferenceClient(token=HF_TOKEN)
    
    try:
        response = client.text_generation(
            prompt,
            model=MODEL_NAME,
            max_new_tokens=300,
            temperature=0.8,
            do_sample=True
        )
        return response
    except Exception as e:
        return f"🚨 Error: {str(e)}"

# ======================
# INTERFAZ DE USUARIO
# ======================
def barra_lateral():
    """Construye la barra lateral de gestión de chats"""
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
        st.caption("v2.0 | Chatbot Gratuito")

def area_chat():
    """Construye el área principal del chat"""
    st.title("🤖 Asistente AI Gratuito")
    
    if st.session_state.chat_actual:
        for mensaje in st.session_state.chat_actual["historial"]:
            with st.chat_message(mensaje["rol"]):
                st.markdown(mensaje["contenido"])
    
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
            guardar_chats(st.session_state.chats)

# ======================
# INICIALIZACIÓN
# ======================
if "chats" not in st.session_state:
    st.session_state.chats = cargar_chats()
    
if "chat_actual" not in st.session_state:
    st.session_state.chat_actual = None

# ======================
# EJECUCIÓN PRINCIPAL
# ======================
barra_lateral()
area_chat()

# ======================
# ESTILOS
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