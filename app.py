import streamlit as st
import datetime
from database import DatabaseManager
from models import Sunset, TipoEntrada, Cliente
import urllib.parse
import requests

db = DatabaseManager()

st.set_page_config(page_title="MANSO SUNSET | Tickets & Traslados", page_icon="🍷", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .brand-title {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            font-size: 38px;
            color: #FFAD60;
            letter-spacing: -0.5px;
            margin: 0;
        }
        .stApp { background-color: #121212; }
        div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
            background-color: #1A1A1A;
            border: 1px solid #2C2C2C;
            border-radius: 12px;
            padding: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE SESIÓN DE USUARIO ---
if 'usuario_logueado' not in st.session_state:
    st.session_state['usuario_logueado'] = None

if 'nombre_usuario_logueado' not in st.session_state:
    st.session_state['nombre_usuario_logueado'] = ""

if 'db_usuarios_registrados' not in st.session_state:
    st.session_state['db_usuarios_registrados'] = {
        "anahisaida@gmail.com": {"nombre": "Anahí Zelaya", "pass": "1234"}
    }

# Credenciales de Google Console (leídas de manera segura)
CLIENT_ID = st.secrets["google"]["client_id"]
CLIENT_SECRET = st.secrets["google"]["client_secret"]
REDIRECT_URI = st.secrets["google"]["redirect_uri"]

# Capturamos código de Google OAuth y pedimos los datos reales
query_params = st.query_params
if "code" in query_params and not st.session_state['usuario_logueado']:
    code = query_params["code"]
    
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    try:
        token_res = requests.post(token_url, data=token_data).json()
        if "access_token" in token_res:
            access_token = token_res["access_token"]
            user_info_res = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            ).json()
            
            if "email" in user_info_res:
                st.session_state['usuario_logueado'] = user_info_res["email"]
                st.session_state['nombre_usuario_logueado'] = user_info_res.get("name", "Usuario Google")
    except Exception:
        st.session_state['usuario_logueado'] = "usuario@gmail.com"
        st.session_state['nombre_usuario_logueado'] = "Usuario Google"
        
    st.query_params.clear()
    st.rerun()

if "pago" in query_params and query_params["pago"] == "exitoso":
    st.session_state['pago_completado'] = True

nav_col1, nav_col2, nav_col3 = st.columns([1.5, 2, 1.5])

with nav_col1:
    st.markdown('<p class="brand-title">MANSO SUNSET</p>', unsafe_allow_html=True)

with nav_col2:
    busqueda = st.text_input("Busqueda", label_visibility="collapsed", placeholder="Buscar bodega o zona...")

with nav_col3:
    if st.session_state['usuario_logueado']:
        nombre_mostrar = st.session_state.get('nombre_usuario_logueado') or st.session_state['usuario_logueado']
        st.write(f"Hola, **{nombre_mostrar}**")
        if st.button("Cerrar Sesion", use_container_width=True):
            st.session_state['usuario_logueado'] = None
            st.session_state['nombre_usuario_logueado'] = ""
            st.rerun()
    else:
        with st.popover("Mi Cuenta"):
            tab_login, tab_registro = st.tabs(["Iniciar Sesion", "Registrarse"])
            
            with tab_login:
                st.markdown("##### Acceso con Google")
                google_auth_url = (
                    f"https://accounts.google.com/o/oauth2/v2/auth?"
                    f"client_id={CLIENT_ID}&"
                    f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
                    f"response_type=code&"
                    f"scope=openid%20email%20profile"
                )
                
                st.markdown(f"""
                    <a href="{google_auth_url}" target="_self">
                        <button style="background-color:white;color:black;padding:10px 15px;border:1px solid #ccc;border-radius:8px;font-weight:bold;cursor:pointer;width:100%;display:flex;align-items:center;justify-content:center;gap:10px;">
                            <img src="https://www.svgrepo.com/show/475656/google-color.svg" width="18px"> Continuar con Google
                        </button>
                    </a>
                """, unsafe_allow_html=True)
                
                st.divider()
                st.markdown("##### O con correo y contraseña")
                email_login = st.text_input("Correo electronico", key="log_email")
                pass_login = st.text_input("Contraseña", type="password", key="log_pass")
                if st.button("Entrar con Email", use_container_width=True):
                    if email_login in st.session_state['db_usuarios_registrados']:
                        st.session_state['usuario_logueado'] = email_login
                        st.session_state['nombre_usuario_logueado'] = st.session_state['db_usuarios_registrados'][email_login]["nombre"]
                        st.success("Bienvenido de vuelta.")
                        st.rerun()
                    else:
                        st.error("Correo o contraseña incorrectos.")
                        
            with tab_registro:
                st.markdown("##### Crear una cuenta nueva")
                nombre_reg = st.text_input("Nombre y Apellido", key="reg_nombre")
                email_reg = st.text_input("Correo electronico", key="reg_email")
                
                fecha_nacimiento = st.date_input(
                    "Fecha de nacimiento", 
                    value=datetime.date(2000, 1, 1),
                    min_value=datetime.date(1920, 1, 1),
                    max_value=datetime.date.today(),
                    key="reg_fnac"
                )
                
                pass_reg = st.text_input("Contraseña", type="password", key="reg_pass")
                
                if st.button("Registrarse", use_container_width=True):
                    hoy = datetime.date.today()
                    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
                    
                    if not email_reg or not nombre_reg or not pass_reg:
                        st.error("Por favor completa todos los campos.")
                    elif edad < 18:
                        st.error("Debes ser mayor de 18 años para registrarte y comprar en Manso Sunset (eventos con alcohol).")
                    elif email_reg in st.session_state['db_usuarios_registrados']:
                        st.error("Mail registrado. Este correo ya se encuentra asociado a una cuenta.")
                    else:
                        st.session_state['db_usuarios_registrados'][email_reg] = {"nombre": nombre_reg, "pass": pass_reg}
                        st.session_state['usuario_logueado'] = email_reg
                        st.session_state['nombre_usuario_logueado'] = nombre_reg
                        st.success("Cuenta creada con éxito. Ya podés comprar tus entradas.")
                        st.rerun()

st.divider()

menu_app = st.radio("Navegacion", ["Explorar Sunsets", "Mis Entradas"], horizontal=True, label_visibility="collapsed")

if menu_app == "Mis Entradas":
    st.subheader("Mis Entradas y Reservas")
    if not st.session_state['usuario_logueado']:
        st.warning("Debes iniciar sesión con tu cuenta para ver tus entradas compradas.")
    else:
        st.info(f"Mostrando entradas asociadas a: **{st.session_state['usuario_logueado']}**")
        with st.container(border=True):
            st.write("Orden #4703879")
            st.write("**Experiencia:** Finca Bandini [Acceso + 2 Copas de Vino]")
            st.write("**Estado del QR:** Se habilitará 24hs antes del evento por motivos de seguridad.")
            st.caption("Estado del pago: Aprobado")
else:
    eventos = db.obtener_eventos()

    if not eventos:
        eventos = [
            Sunset(
                id_evento="bandini",
                nombre="Finca Bandini",
                fecha=datetime.date(2026, 9, 12),
                fecha_str="Sáb 12/09",
                lugar="Las Compuertas",
                img="https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=500&auto=format&fit=crop&q=60",
                opciones_entradas=[
                    TipoEntrada("Solo Acceso", 25000),
                    TipoEntrada("Acceso + 2 Copas de Vino", 32000),
                    TipoEntrada("Experiencia Completa (Sánguche + 1 Copa)", 38000)
                ]
            ),
            Sunset(
                id_evento="maal",
                nombre="Maal Wines",
                fecha=datetime.date(2026, 9, 13),
                fecha_str="Dom 13/09",
                lugar="Las Compuertas",
                img="https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=500&auto=format&fit=crop&q=60",
                opciones_entradas=[
                    TipoEntrada("Solo Acceso", 28000),
                    TipoEntrada("Acceso + 2 Copas de Vino", 35000)
                ]
            )
        ]

    eventos_a_mostrar = eventos
    titulo_seccion = "Destacados de esta semana"

    if busqueda:
        eventos_a_mostrar = [e for e in eventos_a_mostrar if busqueda.lower() in e.nombre.lower() or busqueda.lower() in e.lugar.lower()]
        titulo_seccion = f"Resultados para: '{busqueda}'"

    st.markdown(
        """
        <div style='background: linear-gradient(135deg, #2D0A31 0%, #161616 100%); padding: 45px; border-radius: 14px; text-align: center; margin-bottom: 30px; border: 1px solid #3A0B3F;'>
            <h1 style='font-family: "Inter", sans-serif; color: #FFAD60; margin:0; font-weight: 700; font-size: 38px;'>Toda la magia del atardecer</h1>
            <p style='color: #CCCCCC; font-size: 16px; margin-top: 10px; font-weight: 300;'>Entradas oficiales + Traslados seguros en Mendoza</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.subheader(titulo_seccion)

    if not eventos_a_mostrar:
        st.info("No encontramos sunsets que coincidan con tu búsqueda.")
    else:
        cols = st.columns(3)
        for i, evento in enumerate(eventos_a_mostrar):
            with cols[i % 3]:
                with st.container(border=True):
                    img_url_limpia = evento.img.strip("[]'\"")
                    st.markdown(f'<img src="{img_url_limpia}" style="width:100%; height:160px; object-fit:cover; border-radius:8px; margin-bottom:10px;">', unsafe_allow_html=True)
                    
                    st.markdown(f"#### {evento.nombre}")
                    st.caption(f"Fecha: {evento.fecha_str} | Ubicación: {evento.lugar}")
                    
                    precio_min = min([op.precio for op in evento.opciones_entradas]) if evento.opciones_entradas else 0
                    st.markdown(f"**Desde ${precio_min:,}** (+ service charge)")
                    
                    if st.button("Ver Opciones & Traslados", key=f"btn_{evento.id_evento}", use_container_width=True):
                        st.session_state['sunset_elegido_obj'] = evento
                        st.session_state['sunset_elegido'] = evento.nombre
                        st.session_state['fecha_sunset'] = evento.fecha_str
                        st.session_state['pago_completado'] = False

    st.divider()

    if 'sunset_elegido' in st.session_state and not st.session_state.get('pago_completado', False):
        st.subheader(f"Seleccionaste: {st.session_state['sunset_elegido']}")
        
        evento_obj = st.session_state.get('sunset_elegido_obj')
        
        with st.container(border=True):
            col_izq, col_der = st.columns(2)
            
            with col_izq:
                st.markdown("#### 1. Datos de Contacto y Tipo de Entrada")
                email_defecto = st.session_state.get('usuario_logueado', '')
                
                nombre_usuario = st.text_input("Nombre", placeholder="Ej: Anahí")
                apellido_usuario = st.text_input("Apellido", placeholder="Ej: Zelaya")
                email_usuario = st.text_input("Correo Electronico", value=email_defecto, placeholder="tucorreo@email.com")
                celular_usuario = st.text_input("Celular / WhatsApp", placeholder="Ej: 2615000000")
                
                nombres_opciones = [f"{op.nombre_opcion} (${op.precio:,})" for op in evento_obj.opciones_entradas]
                opcion_seleccionada_str = st.selectbox("Elegi el tipo de entrada:", nombres_opciones)
                indice_opcion = nombres_opciones.index(opcion_seleccionada_str)
                nombre_opcion_elegida = evento_obj.opciones_entradas[indice_opcion].nombre_opcion
                
                cantidad = st.number_input("Cantidad de entradas", min_value=1, max_value=10, value=2)
                
            with col_der:
                st.markdown("#### 2. Seleccion de Traslado y Total")
                zona_traslado = st.radio(
                    "Agrega tu traslado seguro (Ida y Vuelta):",
                    [
                        "Sin traslado",
                        "Ciudad / Godoy Cruz - $80.000",
                        "Luján de Cuyo - $50.000",
                        "Maipú - $100.000",
                        "Otra ubicacion / Grupo (+4 personas) - A coordinar"
                    ]
                )
                
                precio_tickets = evento_obj.calcular_subtotal(indice_opcion, cantidad)
                
                if "Sin traslado" in zona_traslado:
                    service_charge = 0
                    costo_traslado = 0
                    total_general = 0
                else:
                    service_charge = int(precio_tickets * 0.15)
                    costo_traslado = 0
                    if "Ciudad / Godoy Cruz" in zona_traslado:
                        costo_traslado = 80000
                    elif "Luján de Cuyo" in zona_traslado:
                        costo_traslado = 50000
                    elif "Maipú" in zona_traslado:
                        costo_traslado = 100000
                    total_general = precio_tickets + service_charge + costo_traslado
                
                if "Sin traslado" not in zona_traslado:
                    st.write(f"**Opcion:** {nombre_opcion_elegida}")
                    st.write(f"**Entradas:** ${precio_tickets:,}")
                    st.write(f"**Service Charge (15%):** ${service_charge:,}")
                    if costo_traslado > 0:
                        st.write(f"**Traslado:** ${costo_traslado:,}")
                    st.markdown(f"### Total: ${total_general:,}")
                else:
                    st.info("Para adquirir unicamente las entradas sin traslado, te derivamos al canal oficial de la bodega.")

            if "Sin traslado" in zona_traslado:
                st.markdown("""
                    <a href="https://www.instagram.com" target="_blank">
                        <button style="background-color:#E1306C;color:white;padding:12px 20px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;width:100%;">
                            Ir a la Ticketera / Canal Oficial de la Bodega
                        </button>
                    </a>
                """, unsafe_allow_html=True)
            else:
                if st.button("Continuar al Pago", type="primary", use_container_width=True):
                    cliente = Cliente(nombre_usuario, apellido_usuario, email_usuario, celular_usuario)
                    valido, mensaje_error = cliente.es_valido()

                    if not valido:
                        st.error(mensaje_error)
                    elif not st.session_state.get('usuario_logueado'):
                        st.warning("Debes iniciar sesión con Google o registrarte arriba a la derecha para completar la compra.")
                    elif "Otra ubicacion" in zona_traslado:
                        st.warning("Seleccionaste cotizacion personalizada.")
                        st.markdown("[Clic aqui para coordinar por WhatsApp](https://wa.me/5492615000000?text=Hola!%20Quiero%20coordinar%20un%20traslado%20grupal%20para%20Manso%20Sunset)")
                    else:
                        detalle_sunset = f"{st.session_state.get('sunset_elegido')} [{nombre_opcion_elegida}]"
                        st.session_state['detalle_experiencia_final'] = detalle_sunset
                        
                        reserva_data = {
                            "nombre": cliente.nombre,
                            "apellido": cliente.apellido,
                            "email": cliente.email,
                            "celular": cliente.celular,
                            "sunset": detalle_sunset,
                            "fecha_sunset": st.session_state.get('fecha_sunset', 'Fecha a confirmar'),
                            "cantidad": str(cantidad),
                            "zona_traslado": zona_traslado,
                            "total": total_general
                        }
                        db.guardar_reserva(reserva_data, estado_pago="Pendiente de Pago")
                        st.success("Reserva iniciada correctamente. Selecciona abajo para completar el pago.")
                        st.session_state['mostrar_simulador_pago'] = True

                if st.session_state.get('mostrar_simulador_pago', False):
                    st.info("Redirigiendo a pasarela segura...")
                    if st.button("Abonar en Mercado Pago", type="secondary", use_container_width=True):
                        st.session_state['pago_completado'] = True
                        st.session_state['mostrar_simulador_pago'] = False
                        st.rerun()

    if st.session_state.get('pago_completado', False):
        with st.container(border=True):
            st.success("Compra exitosa. Tus entradas ya están cargadas en tu cuenta y podés verlas desde la sección 'Mis Entradas'.")
            st.markdown("### Resumen de tu Experiencia - MANSO SUNSET")
            
            experiencia_resumen = st.session_state.get('detalle_experiencia_final', st.session_state.get('sunset_elegido'))
            st.write(f"**Experiencia:** {experiencia_resumen}")
            st.write(f"**Fecha:** {st.session_state.get('fecha_sunset', 'Fecha a confirmar')}")
            st.caption("Por motivos de seguridad, los QR para ingresar se habilitarán cerca de la fecha del evento.")
            
            if st.button("Realizar otra reserva", use_container_width=True):
                st.session_state.clear()
                st.query_params.clear()
                st.rerun()