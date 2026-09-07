import datetime
import os
import gspread
import streamlit as st
from google.oauth2 import service_account

class DatabaseManager:
    def __init__(self, credentials_file="credentials.json", sheet_name="Base de Datos - Manso Sunsets"):
        self.credentials_file = credentials_file
        self.sheet_name = sheet_name
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

    @st.cache_resource
    def _get_spreadsheet(_self):
        try:
            if os.path.exists(_self.credentials_file):
                creds = service_account.Credentials.from_service_account_file(_self.credentials_file, scopes=_self.scopes)
            elif "gcp_service_account" in st.secrets:
                creds_dict = dict(st.secrets["gcp_service_account"])
                creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=_self.scopes)
            else:
                raise FileNotFoundError("No se encontró el archivo credentials.json ni los secretos en Streamlit.")
            
            client = gspread.authorize(creds)
            return client.open(_self.sheet_name)
        except Exception as e:
            st.error(f"❌ Error al conectar con Google Sheets: {str(e)}")
            return None

    def obtener_eventos(self):
        """Lee la solapa 'Eventos' y agrupa múltiples opciones de entradas por id_evento"""
        try:
            spreadsheet = self._get_spreadsheet()
            if spreadsheet is None:
                return []
            
            try:
                sheet_eventos = spreadsheet.worksheet("Eventos")
            except:
                return []
            
            registros = sheet_eventos.get_all_records()
            eventos_dict = {}
            
            from models import Sunset, TipoEntrada
            for reg in registros:
                id_ev = str(reg["id_evento"])
                
                # Si el evento ya existe en el diccionario, solo le agregamos la nueva opción de entrada
                if id_ev in eventos_dict:
                    evento = eventos_dict[id_ev]
                    evento.opciones_entradas.append(
                        TipoEntrada(str(reg["nombre_opcion"]), int(reg["precio"]))
                    )
                else:
                    # Si es la primera vez que vemos este evento, lo creamos
                    partes_fecha = str(reg["fecha"]).split("-")
                    f_obj = datetime.date(int(partes_fecha[0]), int(partes_fecha[1]), int(partes_fecha[2]))
                    
                    opcion_inicial = TipoEntrada(str(reg["nombre_opcion"]), int(reg["precio"]))
                    
                    evento = Sunset(
                        id_evento=id_ev,
                        nombre=str(reg["nombre"]),
                        fecha=f_obj,
                        fecha_str=str(reg["fecha_str"]),
                        lugar=str(reg["lugar"]),
                        img=str(reg["img"]),
                        opciones_entradas=[opcion_inicial]
                    )
                    eventos_dict[id_ev] = evento
            
            return list(eventos_dict.values())
        except Exception as e:
            st.error(f"⚠️ Error cargando eventos desde Sheets: {str(e)}")
            return []

    def guardar_reserva(self, reserva_dict, estado_pago="Pendiente de Pago"):
        """Método para almacenar la reserva en la solapa principal"""
        try:
            spreadsheet = self._get_spreadsheet()
            if spreadsheet is None:
                return False
            
            sheet = spreadsheet.sheet1
            id_reserva = f"MS-{int(datetime.datetime.now().timestamp())}"
            fecha_compra = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            
            nueva_fila = [
                id_reserva,
                fecha_compra,
                reserva_dict["nombre"],
                reserva_dict["apellido"],
                reserva_dict["email"],
                reserva_dict["celular"],
                reserva_dict["sunset"],
                reserva_dict["fecha_sunset"],
                reserva_dict["cantidad"],
                reserva_dict["zona_traslado"],
                reserva_dict["total"],
                estado_pago,
                "Sin asignar"
            ]
            
            sheet.append_row(nueva_fila)
            return True
        except Exception as e:
            st.error(f"❌ Error detallado al guardar reserva: {str(e)}")
            return False