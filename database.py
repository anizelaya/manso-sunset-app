import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# --- CONEXIÓN INTELIGENTE A GOOGLE SHEETS ---
try:
    if "gcp_service_account" in st.secrets:
        credentials_dict = dict(st.secrets["gcp_service_account"])
        gc = gspread.service_account_from_dict(credentials_dict)
    else:
        gc = gspread.service_account(filename="credentials.json")
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
# ---------------------------------------------

class DatabaseManager:
    def __init__(self, spreadsheet_name="MansoSunsetDB"):
        try:
            self.gc = gc
            self.sheet = self.gc.open(spreadsheet_name)
        except Exception as e:
            st.error(f"No se pudo abrir la planilla '{spreadsheet_name}': {e}")
            self.sheet = None

    def get_worksheet(self, name):
        if not self.sheet:
            return None
        try:
            return self.sheet.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            return self.sheet.add_worksheet(title=name, rows="100", cols="20")

    def get_all_records(self, worksheet_name):
        ws = self.get_worksheet(worksheet_name)
        if ws:
            return ws.get_all_records()
        return []

    def obtener_eventos(self):
        # Trae los registros de la pestaña 'Eventos' (ajustá el nombre si tu pestaña se llama distinto)
        return self.get_all_records("Eventos")

    def add_row(self, worksheet_name, data):
        ws = self.get_worksheet(worksheet_name)
        if ws:
            ws.append_row(data)
            return True
        return False

    def update_row_by_index(self, worksheet_name, index, data):
        ws = self.get_worksheet(worksheet_name)
        if ws:
            for i, val in enumerate(data, start=1):
                ws.update_cell(index, i, val)
            return True
        return False

    def find_row_by_column_value(self, worksheet_name, column_name, value):
        ws = self.get_worksheet(worksheet_name)
        if ws:
            records = ws.get_all_records()
            for idx, record in enumerate(records, start=2):
                if str(record.get(column_name)) == str(value):
                    return idx, record
        return None, None