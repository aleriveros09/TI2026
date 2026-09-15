import csv
import json
import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path


# -----------------------------------------------------------------------------
# ESTRUCTURA DE DATOS Y BITWISE (8 BOOLEANOS EN 1 BYTE)
# -----------------------------------------------------------------------------
# Definición de bits para cada bandera booleana (Bitmask)
BIT_PRIMARIA     = 1 << 0  # 00000001 (1)
BIT_SECUNDARIA   = 1 << 1  # 00000010 (2)
BIT_UNIVERSIDAD  = 1 << 2  # 00000100 (4)
BIT_VIVIENDA     = 1 << 3  # 00001000 (8)
BIT_OBRA_SOCIAL  = 1 << 4  # 00010000 (16)
BIT_TRABAJA      = 1 << 5  # 00100000 (32)
BIT_VEHICULO     = 1 << 6  # 01000000 (64)
BIT_LICENCIA     = 1 << 7  # 10000000 (128)

CAMPOS_BOOL = [
    ("Estudios Primarios", BIT_PRIMARIA),
    ("Estudios Secundarios", BIT_SECUNDARIA),
    ("Estudios Universitarios", BIT_UNIVERSIDAD),
    ("Vivienda Propia", BIT_VIVIENDA),
    ("Obra Social", BIT_OBRA_SOCIAL),
    ("Trabaja Activo", BIT_TRABAJA),
    ("Vehículo Propio", BIT_VEHICULO),
    ("Licencia Conducir", BIT_LICENCIA),
]

# Formato del struct binario de longitud fija (Exactamente 133 bytes por registro):
# - Nombre Completo: 60 bytes (string UTF-8 rellenado con nulos)
# - Dirección:       64 bytes (string UTF-8 rellenado con nulos)
# - DNI:             8 bytes (entero de 64 bits sin signo, uint64_t)
# - Banderas Bitwise: 1 byte (unsigned char, uint8_t)
# Total: 60 + 64 + 8 + 1 = 133 bytes por persona
FORMATO_BINARIO = "<60s64sQB"
TAMANO_REGISTRO_BIN = struct.calcsize(FORMATO_BINARIO)


def empaquetar_booleans(flags_dict: dict) -> int:
    """Empaqueta 8 valores booleanos en un único byte (0 a 255) mediante operacion OR bitwise."""
    byte_resultado = 0
    for clave, bitmask in CAMPOS_BOOL:
        if flags_dict.get(clave, False):
            byte_resultado |= bitmask  # Enciende el bit correspondiente
    return byte_resultado


def desempaquetar_booleans(byte_flags: int) -> dict:
    """Desempaqueta un byte en 8 valores booleanos usando la operación AND bitwise."""
    flags_dict = {}
    for clave, bitmask in CAMPOS_BOOL:
        flags_dict[clave] = bool(byte_flags & bitmask)  # Evalúa si el bit está encendido
    return flags_dict


def generar_datos_ejemplo() -> list[dict]:
    """Genera una lista con 20 personas de prueba."""
    personas = []
    for i in range(1, 21):
        personas.append({
            "nombre": f"Persona Ejemplo NombreLargo {i}",
            "direccion": f"Calle Av. Libertador General San Martin Nro {1000 + i*15}",
            "dni": 30000000 + i * 1234,
            "flags": {
                "Estudios Primarios": True,
                "Estudios Secundarios": (i % 2 == 0),
                "Estudios Universitarios": (i % 3 == 0),
                "Vivienda Propia": (i % 4 == 0),
                "Obra Social": (i % 2 != 0),
                "Trabaja Activo": True,
                "Vehículo Propio": (i % 5 == 0),
                "Licencia Conducir": (i % 2 == 0),
            }
        })
    return personas


# -----------------------------------------------------------------------------
# FUNCIONES DE PERSISTENCIA (CSV Y BINARIO)
# -----------------------------------------------------------------------------
def guardar_csv(path_file: Path, datos: list[dict]):
    with open(path_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre", "Direccion", "DNI"] + [c[0] for c in CAMPOS_BOOL])
        for p in datos:
            row = [p["nombre"], p["direccion"], p["dni"]]
            row.extend(["True" if p["flags"][c[0]] else "False" for c in CAMPOS_BOOL])
            writer.writerow(row)


def leer_csv(path_file: Path) -> list[dict]:
    personas = []
    with open(path_file, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row:
                continue
            flags = {}
            for idx, (clave, _) in enumerate(CAMPOS_BOOL, start=3):
                flags[clave] = (row[idx] == "True")
            personas.append({
                "nombre": row[0],
                "direccion": row[1],
                "dni": int(row[2]),
                "flags": flags
            })
    return personas


def guardar_binario(path_file: Path, datos: list[dict]):
    with open(path_file, "wb") as f:
        for p in datos:
            nombre_bytes = p["nombre"].encode("utf-8")[:60].ljust(60, b"\x00")
            direccion_bytes = p["direccion"].encode("utf-8")[:64].ljust(64, b"\x00")
            dni = int(p["dni"])
            flags_byte = empaquetar_booleans(p["flags"])

            registro_empaquetado = struct.pack(
                FORMATO_BINARIO, nombre_bytes, direccion_bytes, dni, flags_byte
            )
            f.write(registro_empaquetado)


def leer_binario(path_file: Path) -> list[dict]:
    personas = []
    with open(path_file, "rb") as f:
        while True:
            chunk = f.read(TAMANO_REGISTRO_BIN)
            if len(chunk) < TAMANO_REGISTRO_BIN:
                break
            nombre_b, dir_b, dni, flags_byte = struct.unpack(FORMATO_BINARIO, chunk)
            
            nombre = nombre_b.decode("utf-8").rstrip("\x00")
            direccion = dir_b.decode("utf-8").rstrip("\x00")
            flags = desempaquetar_booleans(flags_byte)

            personas.append({
                "nombre": nombre,
                "direccion": direccion,
                "dni": dni,
                "flags": flags
            })
    return personas


# -----------------------------------------------------------------------------
# INTERFAZ GRÁFICA CON TKINTER
# -----------------------------------------------------------------------------
class AppEmpaquetadoBitwise(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Gestión de Almacenamiento: Bitwise vs CSV")
        self.geometry("1100x750")

        self.datos = generar_datos_ejemplo()
        self.path_csv = Path("personas_longitud_variable.csv")
        self.path_bin = Path("personas_fijo_bitwise.bin")

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Frame Superior: Botones de Acción
        frame_acciones = ttk.LabelFrame(self, text=" Operaciones de Persistencia ", padding=10)
        frame_acciones.pack(fill=tk.X, padx=15, pady=10)

        ttk.Button(
            frame_acciones, text="1. Generar y Guardar Archivos", command=self._generar_y_guardar
        ).grid(row=0, column=0, padx=10, pady=5)

        ttk.Button(
            frame_acciones, text="2. Abrir y Cargar CSV", command=self._cargar_csv
        ).grid(row=0, column=1, padx=10, pady=5)

        ttk.Button(
            frame_acciones, text="3. Abrir y Cargar Binario (Bitwise)", command=self._cargar_binario
        ).grid(row=0, column=2, padx=10, pady=5)

        # Frame Medio: Comparativa de Tamaños
        frame_metricas = ttk.LabelFrame(self, text=" Comparativa de Tamaño en Disco ", padding=10)
        frame_metricas.pack(fill=tk.X, padx=15, pady=5)

        self.lbl_tamanos = ttk.Label(
            frame_metricas,
            text="Haga clic en 'Generar y Guardar Archivos' para iniciar el análisis...",
            font=("Consolas", 10),
        )
        self.lbl_tamanos.pack(anchor=tk.W)

        # Notebook / Pestañas de Inspección
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Tab 1: Tabla de Datos Recuperados
        frame_tabla = ttk.Frame(notebook)
        notebook.add(frame_tabla, text=" Visualizador de Registros ")

        columnas = ("Nombre", "Direccion", "DNI", "Flags Booleanos")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        self.tree.heading("Nombre", text="Nombre y Apellido")
        self.tree.heading("Direccion", text="Dirección")
        self.tree.heading("DNI", text="DNI")
        self.tree.heading("Flags Booleanos", text="Atributos (Desempaquetados)")

        self.tree.column("Nombre", width=180)
        self.tree.column("Direccion", width=250)
        self.tree.column("DNI", width=90)
        self.tree.column("Flags Booleanos", width=500)

        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tab 2: Conclusión Teórica
        frame_teoria = ttk.Frame(notebook)
        notebook.add(frame_teoria, text=" Conclusión Teórica y Alta Escala ")

       # OPCIÓN RECOMENDADA: Usar padx y pady para el margen interno
        txt_teoria = tk.Text(frame_teoria, font=("Calibri", 11), wrap=tk.WORD, padx=10, pady=10)
        txt_teoria.pack(fill=tk.BOTH, expand=True)

        conclusion_texto = (
            "CONCLUSIÓN TEÓRICA SOBRE LA ESTRUCTURA DE CODIFICACIÓN A ALTA ESCALA\n"
            "========================================================================\n\n"
            "1. EFICIENCIA EN ESPACIO (BITPACKING):\n"
            "   - Formato Texto (CSV/JSON): Representar 8 campos booleanos como cadenas ('True'/'False') "
            "consume entre 4 y 5 bytes por cada respuesta (promedio de 36 a 40 bytes solo para las 8 banderas).\n"
            "   - Formato Binario con Bitwise: Al utilizar operaciones de empaquetado a nivel de bits "
            "(bit-packing), las 8 respuestas booleanas se consolidan en exactamente 1 BYTE (8 bits).\n"
            "   - Esto representa un ahorro superior al 97% en la representación del estado booleano.\n\n"
            "2. IMPACTO A ALTA ESCALA (SISTEMAS MASIVOS):\n"
            "   Si escalamos esta base de datos a 100 millones de usuarios:\n"
            "   - Almacenamiento Booleano en Texto (~40 B/usuario)  => ~4.00 GB de datos sólo en flags.\n"
            "   - Almacenamiento Booleano con Bitwise (1 B/usuario) => ~0.10 GB (100 MB).\n"
            "   Ahorro directo de disco e I/O de red: ~3.90 GB.\n\n"
            "3. RENDIMIENTO DE LECTURA/ESCRITURA (CPU & BUS DE MEMORIA):\n"
            "   - Los registros de longitud fija permiten acceso aleatorio indexado en tiempo O(1) mediante la "
            "fórmula: Posición = Índice * Tamaño_Registro_Fijo. No requiere parsear cadenas ni buscar delimitadores.\n"
            "   - Reducir el tamaño por registro optimiza la tasa de acierto en las memorias Caché L1/L2/L3 "
            "del procesador y disminuye la latencia de entrada/salida (Disk/Network I/O)."
        )
        txt_teoria.insert(tk.END, conclusion_texto)
        txt_teoria.config(state=tk.DISABLED)

    def _generar_y_guardar(self):
        guardar_csv(self.path_csv, self.datos)
        guardar_binario(self.path_bin, self.datos)

        size_csv = self.path_csv.stat().st_size
        size_bin = self.path_bin.stat().st_size
        ahorro = (1.0 - (size_bin / size_csv)) * 100.0

        info = (
            f"Archivo CSV (Longitud Variable): {size_csv} bytes  |  "
            f"Archivo Binario (Fijo + Bitwise): {size_bin} bytes  |  "
            f"Ahorro Total: {ahorro:.2f}%"
        )
        self.lbl_tamanos.config(text=info)
        messagebox.showinfo("Éxito", "Archivos generados y guardados correctamente.")

    def _mostrar_en_tabla(self, lista_personas: list[dict]):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in lista_personas:
            activos = [k for k, v in p["flags"].items() if v]
            flags_str = ", ".join(activos) if activos else "Ninguno"
            self.tree.insert("", tk.END, values=(p["nombre"], p["direccion"], p["dni"], flags_str))

    def _cargar_csv(self):
        if not self.path_csv.is_file():
            messagebox.showerror("Error", "Primero debe generar los archivos.")
            return
        datos = leer_csv(self.path_csv)
        self._mostrar_en_tabla(datos)

    def _cargar_binario(self):
        if not self.path_bin.is_file():
            messagebox.showerror("Error", "Primero debe generar los archivos.")
            return
        datos = leer_binario(self.path_bin)
        self._mostrar_en_tabla(datos)


if __name__ == "__main__":
    app = AppEmpaquetadoBitwise()
    app.mainloop()
