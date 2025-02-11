import streamlit as st
import requests
import json
import os
from datetime import datetime

# ======================
# CONFIGURACIÓN INICIAL
# ======================
st.set_page_config(
    page_title="DeepSeek Cloud",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ======================
# SECRETOS Y API
# ======================
API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Configurar en secrets del despliegue
API_URL = "https://api.deepseek.com/v1/chat/completions"  # Verificar endpoint real

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
# FUNCIONES DE LA API
# ======================
def generar_respuesta(prompt):
    """Envía la solicitud a la API de DeepSeek"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-r1-8b-chat",  # Modelo específico para chat
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        respuesta = requests.post(API_URL, headers=headers, json=payload, timeout=25)
        respuesta.raise_for_status()
        return respuesta.json()['choices'][0]['message']['content']
        
    except requests.exceptions.HTTPError as e:
        return f"Error API: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# ======================
# INTERFAZ DE USUARIO
# ======================
def barra_lateral():
    """Construye la barra lateral de gestión de chats"""
    with st.sidebar:
        st.header("Gestión de Chats")
        
        # Botón nuevo chat
        if st.button("✨ Nuevo Chat", use_container_width=True):
            nuevo_chat = {
                "id": str(datetime.now().timestamp()),
                "titulo": "Nuevo Chat",
                "historial": []
            }
            st.session_state.chats.append(nuevo_chat)
            st.session_state.chat_actual = nuevo_chat
            guardar_chats(st.session_state.chats)
        
        # Lista de chats
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
        st.caption("v1.0 | Desarrollado por [Tu Nombre]")

def area_chat():
    """Construye el área principal del chat"""
    st.title("DeepSeek Cloud Assistant")
    st.caption("Conectado a la API oficial de DeepSeek")
    
    if st.session_state.chat_actual:
        for mensaje in st.session_state.chat_actual["historial"]:
            with st.chat_message(mensaje["rol"]):
                st.markdown(mensaje["contenido"])
    
    if prompt := st.chat_input("Escribe tu mensaje..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("Procesando..."):
            respuesta_api = generar_respuesta(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(respuesta_api)
            
            # Actualizar historial
            st.session_state.chat_actual["historial"].extend([
                {"rol": "user", "contenido": prompt},
                {"rol": "assistant", "contenido": respuesta_api}
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
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        background: #1a1d24;
        border: 1px solid #2b313e;
    }
    
    textarea {
        background: #1a1d24 !important;
        border: 1px solid #2b313e !important;
    }
    
    .stButton button {
        transition: transform 0.2s !important;
    }
    
    .stButton button:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)