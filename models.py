import re

class TipoEntrada:
    def __init__(self, nombre_opcion, precio):
        self.nombre_opcion = nombre_opcion
        self.precio = precio


class Sunset:
    def __init__(self, id_evento, nombre, fecha, fecha_str, lugar, img, opciones_entradas=None):
        self.id_evento = id_evento
        self.nombre = nombre
        self.fecha = fecha
        self.fecha_str = fecha_str
        self.lugar = lugar
        self.img = img
        self.opciones_entradas = opciones_entradas if opciones_entradas else []

    def calcular_subtotal(self, indice_opcion, cantidad):
        """Calcula el costo bruto según la opción de entrada elegida y la cantidad"""
        if 0 <= indice_opcion < len(self.opciones_entradas):
            precio_unitario = self.opciones_entradas[indice_opcion].precio
            return cantidad * precio_unitario
        return 0


class Cliente:
    def __init__(self, nombre, apellido, email, celular):
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.celular = celular

    def es_valido(self):
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        celular_regex = r"^\d{8,15}$"
        
        if not self.nombre or not self.apellido or not self.email or not self.celular:
            return False, "⚠️ Por favor completa todos tus datos de contacto."
        if not re.match(email_regex, self.email):
            return False, "⚠️ Por favor ingresa un correo electrónico válido."
        if not re.match(celular_regex, self.celular):
            return False, "⚠️ Por favor ingresa un número de celular válido (solo números)."
        
        return True, ""