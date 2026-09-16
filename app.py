import streamlit as st
import pandas as pd
from database import DatabaseManager

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Manso Sunset - Entradas y Traslados",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS (Diseño oscuro/naranja moderno) ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTextInput > div > div > input, .stSelectbox > div > div > select {
        background-color: #1f2937;
        color: white;
        border-radius: 8px;
        border: 1px solid #374151;
    }
    .css-1544g2n {padding-top: 2rem;}
    h1, h2, h3 {
        color: #f97316 !important;
    }
    .card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAR BASE DE DATOS ---
# (Asegurate de poner el nombre exacto de tu planilla de Google Sheets aquí abajo)
db = DatabaseManager(spreadsheet_name="MansoSunsetDB")

# --- ENCABEZADO ---
st.title("🌅 MANSO SUNSET")
st.markdown("### Entradas oficiales + Traslados seguros en Mendoza")
st.write("Disfruta de los mejores atardeceres en bodegas. Elegí tu experiencia, comprá tu entrada o coordiná tu traslado directo con nosotros.")

st.divider()

# --- CARGAR EVENTOS DESDE GOOGLE SHEETS ---
try:
    eventos = db.obtener_eventos()
except Exception:
    eventos = []

# Datos de prueba por si la planilla todavía está vacía o cargando
if not eventos:
    eventos = [
        {
            "id": 1,
            "nombre": "Sunset Finca Bandini",
            "bodega": "Finca Bandini",
            "zona": "Luján de Cuyo",
            "fecha": "2026-10-15",
            "link_entrada": "https://www.passline.com",
            "imagen": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600"
        },
        {
            "id": 2,
            "nombre": "Atardecer en Maal Wines",
            "bodega": "Maal Wines",
            "zona": "Vistalba",
            "fecha": "2026-10-22",
            "link_entrada": "https://www.eventbrite.com",
            "imagen": "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=600"
        },
        {
            "id": 3,
            "nombre": "Sesión Acústica Martino",
            "bodega": "Martino Wines",
            "zona": "Agrelo",
            "fecha": "2026-10-29",
            "link_entrada": "https://www.passline.com",
            "imagen": "https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=600"
        }
    ]

# --- BARRA DE BÚSQUEDA Y FILTROS POR CATEGORÍA/ZONA ---
col_busq, col_zona = st.columns([2, 1])
with col_busq:
    busqueda = st.text_input("🔍 Buscar bodega o nombre del sunset...", "")

zonas_disponibles = ["Todas"] + list(set([e.get("zona", "") for e in eventos if e.get("zona")]))
with col_zona:
    zona_seleccionada = st.selectbox("Filtrar por Zona", zonas_disponibles)

# Filtrar eventos
eventos_filtrados = eventos
if busqueda:
    eventos_filtrados = [e for e in eventos_filtrados if busqueda.lower() in e.get("nombre", "").lower() or busqueda.lower() in e.get("bodega", "").lower()]
if zona_seleccionada != "Todas":
    eventos_filtrados = [e for e in eventos_filtrados if e.get("zona") == zona_seleccionada]

st.divider()

# --- MOSTRAR SUNSETS EN TARJETAS MODERNAS ---
if not eventos_filtrados:
    st.info("No se encontraron sunsets con esos filtros.")
else:
    for evento in eventos_filtrados:
        with st.container():
            st.markdown(f'<div class="card">', unsafe_allow_html=True)
            col_img, col_info = st.columns([1, 2])
            
            with col_img:
                img_url = evento.get("imagen", "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600")
                st.image(img_url, use_column_width=True)
                
            with col_info:
                st.subheader(evento.get("nombre"))
                st.write(f"📍 **Bodega:** {evento.get('bodega')} ({evento.get('zona')})")
                st.write(f"📅 **Fecha:** {evento.get('fecha')}")
                
                # Opciones de compra o traslado
                st.markdown("---")
                tipo_experiencia = st.radio(
                    "¿Cómo querés ir?", 
                    ["Solo Entrada (Link oficial)", "Con Traslado (Coordinar por WhatsApp)"], 
                    key=f"exp_{evento.get('id')}"
                )
                
                if "Solo Entrada" in tipo_experiencia:
                    link = evento.get("link_entrada", "#")
                    st.markdown(f'<a href="{link}" target="_blank"><button style="background-color:#f97316; color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:bold; cursor:pointer;">Comprar Entrada Oficial 🎟️</button></a>', unsafe_allow_html=True)
                else:
                    with st.form(key=f"form_wpp_{evento.get('id')}"):
                        st.write("🚗 **Coordinar Traslado Privado**")
                        nombre_persona = st.text_input("Tu Nombre y Apellido", key=f"nombre_{evento.get('id')}")
                        cant_personas = st.number_input("Cantidad de personas", min_value=1, max_value=10, value=2, key=f"cant_{evento.get('id')}")
                        ubicacion_salida = st.text_input("¿De dónde nos salimos a buscar? (Dirección / Hotel)", key=f"ubi_{evento.get('id')}")
                        
                        enviar_wpp = st.form_submit_button("Enviar consulta por WhatsApp 💬")
                        
                        if enviar_wpp:
                            if not nombre_persona or not ubicacion_salida:
                                st.warning("Por favor, completá tu nombre y tu ubicación.")
                            else:
                                # Armar mensaje automático para WhatsApp (Reemplazá el 549261... con tu número real)
                                telefono_destino = "5492613358860" 
                                texto_mensaje = (
                                    f"¡Hola! 👋 Me interesa el traslado para el sunset *{evento.get('nombre')}* ({evento.get('bodega')}).\n\n"
                                    f"👤 *Nombre:* {nombre_persona}\n"
                                    f"👥 *Cantidad:* {cant_personas} personas\n"
                                    f"📍 *Ubicación de salida:* {ubicacion_salida}"
                                )
                                import urllib.parse
                                mensaje_codificado = urllib.parse.quote(texto_mensaje)
                                url_whatsapp = f"https://wa.me/{telefono_destino}?text={mensaje_codificado}"
                                
                                st.markdown(f'<a href="{url_whatsapp}" target="_blank"><button style="background-color:#25d366; color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:bold; cursor:pointer;">Hacer clic para abrir WhatsApp 🚀</button></a>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True) 