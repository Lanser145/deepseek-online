import streamlit as st
from huggingface_hub import InferenceClient
import json
import os
import time
from datetime import datetime

# ======================
# 1. CONFIGURACIÓN INICIAL
# ======================
st.set_page_config(
    page_title="Chatbot Profesional",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ======================
# 2. VERIFICACIÓN DE CLAVE API
# ======================
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    st.error("❌ ERROR: No se encontró la clave de Hugging Face. Sigue estas instrucciones:")
    st.markdown("""
    1. Regístrate en [huggingface.co](https://huggingface.co/join)
    2. Crea un token en [Settings → Access Tokens](https://huggingface.co/settings/tokens) (rol **Read**)
    3. En Streamlit Cloud, ve a **Settings → Secrets** y añade:
        ```toml
        [secrets]
        HF_TOKEN = "tu_token_aqui"
        ```
    """)
    st.stop()

# ======================
# 3. MODELO CONFIGURABLE
# ======================
MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"  # ✅ Modelo verificado
CONFIG = {
    "max_new_tokens": 150,
    "temperature": 0.7,
    "repetition_penalty": 1.2
}

# ======================
# 4. MANEJO DE CHATS (COMPLETO)
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
# 5. GENERACIÓN CON CONTROL DE ERRORES
# ======================
def generar_respuesta(prompt):
    client = InferenceClient(token=HF_TOKEN)
    
    try:
        response = client.text_generation(
            f"<|system|>\nEres un asistente en español. Sé conciso y profesional.</s>\n<|user|>\n{prompt}</s>\n<|assistant|>",
            model=MODEL_NAME,
            **CONFIG
        )
        return response.strip()
    except Exception as e:
        if "401" in str(e):
            st.error("🔑 Error de autenticación: Clave API inválida")
        elif "429" in str(e):
            st.error("⏳ Límite de uso alcanzado. Espera 1 minuto.")
            time.sleep(60)
            return generar_respuesta(prompt)
        else:
            st.error(f"Error técnico: {str(e)}")
        return None

# ======================
# 6. INTERFAZ COMPLETA
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
                        if st.session_state.chat_actual and st.session_state.chat_actual["id"] == chat["id"]:
                            st.session_state.chat_actual = None
                        st.session_state.chats.remove(chat)
                        guardar_chats(st.session_state.chats)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error eliminando chat: {str(e)}")

        st.markdown("---")
        st.caption(f"Modelo: {MODEL_NAME.split('/')[-1]} | v5.0")

def area_chat():
    st.title("🤖 Asistente Profesional")
    
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
        
        respuesta = generar_respuesta(prompt)
        
        if respuesta:
            with st.chat_message("assistant"):
                st.markdown(respuesta)
            
            st.session_state.chat_actual["historial"].extend([
                {"rol": "user", "contenido": prompt},
                {"rol": "assistant", "contenido": respuesta}
            ])
            
            if not guardar_chats(st.session_state.chats):
                st.error("Error guardando la conversación")

# ======================
# 7. INICIALIZACIÓN ROBUSTA
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
# 8. EJECUCIÓN
# ======================
barra_lateral()
area_chat()
