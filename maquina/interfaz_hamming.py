import unicodedata
import tkinter as tk
from tkinter import messagebox, ttk


# -----------------------------------------------------------------------------
# 1. ALGORITMOS DE DISTANCIA DE CADENAS
# -----------------------------------------------------------------------------
def calcular_distancia_hamming(cad1: str, cad2: str) -> int:
    """
    Calcula la Distancia de Hamming (diferencias posición a posición).
    Solo es aplicable si len(cad1) == len(cad2).
    """
    if len(cad1) != len(cad2):
        raise ValueError(
            f"Hamming requiere cadenas de igual longitud. "
            f"Longitudes actuales: {len(cad1)} y {len(cad2)}."
        )

    return sum(ch1 != ch2 for ch1, ch2 in zip(cad1, cad2))


def calcular_distancia_levenshtein(cad1: str, cad2: str) -> tuple[int, list[list[int]]]:
    """
    Calcula la Distancia de Levenshtein mediante Programación Dinámica O(M*N).
    Retorna la distancia mínima de edición y la matriz calculada.
    """
    m, n = len(cad1), len(cad2)
    matriz = [[0] * (n + 1) for _ in range(m + 1)]

    # Casos base: transformar desde/hacia la cadena vacía
    for i in range(m + 1):
        matriz[i][0] = i
    for j in range(n + 1):
        matriz[0][j] = j

    # Llenado de la matriz mediante transiciones de costo
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            costo = 0 if cad1[i - 1] == cad2[j - 1] else 1
            matriz[i][j] = min(
                matriz[i - 1][j] + 1,       # Eliminación
                matriz[i][j - 1] + 1,       # Inserción
                matriz[i - 1][j - 1] + costo # Sustitución
            )

    return matriz[m][n], matriz


# -----------------------------------------------------------------------------
# 2. HEURÍSTICA Y NORMALIZACIÓN DE TEXTO
# -----------------------------------------------------------------------------
def normalizar_texto(texto: str) -> str:
    """
    Normaliza el texto para eliminar ruido arbitrario antes de comparar:
    - Convierte a minúsculas.
    - Remueve diacríticos y tildes (NFD Unicodedata).
    - Elimina espacios extra en los extremos y dobles espacios.
    """
    texto = texto.lower().strip()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(texto.split())


def heuristica_similitud(cad1: str, cad2: str) -> tuple[float, int, str]:
    """
    Proceso Heurístico Propuesto:
    1. Normalización de cadenas.
    2. Cálculo de Levenshtein sobre cadenas limpias.
    3. Ratio de Similitud (%) relativo a la longitud máxima de las cadenas.
    """
    norm1 = normalizar_texto(cad1)
    norm2 = normalizar_texto(cad2)

    distancia, _ = calcular_distancia_levenshtein(norm1, norm2)
    max_len = max(len(norm1), len(norm2))

    if max_len == 0:
        similitud_pct = 100.0
    else:
        similitud_pct = (1.0 - (distancia / max_len)) * 100.0

    info_normalizada = f"'{norm1}' vs '{norm2}'"
    return similitud_pct, distancia, info_normalizada


# -----------------------------------------------------------------------------
# 3. INTERFAZ GRÁFICA CON TKINTER
# -----------------------------------------------------------------------------
class AppComparadorCadenas(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Medición de Distancia y Similitud entre Cadenas")
        self.geometry("900x700")

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Panel Superior: Entrada de Cadenas
        frame_entradas = ttk.LabelFrame(self, text=" Cadenas a Comparar ", padding=10)
        frame_entradas.pack(fill=tk.X, padx=15, pady=10)

        ttk.Label(frame_entradas, text="Cadena A (Original / Fuente):").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.entry_cad1 = ttk.Entry(frame_entradas, width=50)
        self.entry_cad1.grid(row=0, column=1, padx=5, pady=5)
        self.entry_cad1.insert(0, "Horacio López")

        ttk.Label(frame_entradas, text="Cadena B (Recibida / Editada):").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.entry_cad2 = ttk.Entry(frame_entradas, width=50)
        self.entry_cad2.grid(row=1, column=1, padx=5, pady=5)
        self.entry_cad2.insert(0, "Oracio López")

        btn_evaluar = ttk.Button(
            frame_entradas, text="Calcular Distancias", command=self._procesar_comparacion
        )
        btn_evaluar.grid(row=0, column=2, rowspan=2, padx=15, sticky=tk.NSEW)

        # Panel Central: Resultados Numéricos
        frame_resultados = ttk.LabelFrame(self, text=" Resultados de Métricas ", padding=10)
        frame_resultados.pack(fill=tk.X, padx=15, pady=5)

        self.txt_resultados = tk.Text(
            frame_resultados, height=8, font=("Consolas", 10), state=tk.DISABLED
        )
        self.txt_resultados.pack(fill=tk.BOTH, expand=True)

        # Notebook: Pestañas con la Matriz de Levenshtein y la Propuesta Teórica
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Tab 1: Matriz de Programación Dinámica
        frame_matriz = ttk.Frame(notebook)
        notebook.add(frame_matriz, text=" Matriz Levenshtein ")

        self.txt_matriz = tk.Text(frame_matriz, font=("Consolas", 9), wrap=tk.NONE)
        scrollbar_y = ttk.Scrollbar(frame_matriz, orient=tk.VERTICAL, command=self.txt_matriz.yview)
        scrollbar_x = ttk.Scrollbar(frame_matriz, orient=tk.HORIZONTAL, command=self.txt_matriz.xview)
        self.txt_matriz.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_matriz.pack(fill=tk.BOTH, expand=True)

        # Tab 2: Explicación de la Heurística Propuesta
        frame_teoria = ttk.Frame(notebook)
        notebook.add(frame_teoria, text=" Propuesta de Proceso / Heurística ")

        txt_teoria = tk.Text(frame_teoria, font=("Calibri", 11), wrap=tk.WORD, padx=10, pady=10)
        txt_teoria.pack(fill=tk.BOTH, expand=True)

        propuesta_texto = (
            "HEURÍSTICA Y PROCESO PROPUESTO PARA COMPARACIÓN DE TEXTO\n"
            "========================================================================\n\n"
            "1. POR QUÉ FALLA HAMMING ANTE DESFASES:\n"
            "   La Distancia de Hamming compara únicamente posición a posición (i-ésimo elemento con i-ésimo).\n"
            "   Si ocurre un desfase por inserción o eliminación de 1 carácter (ej. 'Juan Perez' [10 B] vs\n"
            "   'Jaun Perez' [10 B] o 'Juan Perez' vs 'JuanPerez' [9 B]), una única mutación desplaza todos\n"
            "   los índices posteriores, causando que la Distancia de Hamming marque error en casi toda la cadena,\n"
            "   incluso cuando el contenido es un 90% idéntico.\n\n"
            "2. PROCESO OPTIMIZADO PROPUESTO:\n"
            "   Para lograr una comparación insensible a tildes, mayúsculas o espacios duplicados, se sugiere:\n"
            "   a) Normalización Unicode (NFD): Elimina marcas diacríticas/tildes y unifica a minúsculas.\n"
            "   b) Levenshtein Ajustado: Se ejecuta sobre el texto limpio para medir costo real de edición.\n"
            "   c) Ratio de Similitud Relativo (%): Convierte la distancia absoluta en un porcentaje intuitivo:\n\n"
            "          Similitud (%) = (1 - (Distancia_Levenshtein / Longitud_Máxima)) * 100\n\n"
            "3. MEJORAS AVANZADAS PARA PRODUCCIÓN:\n"
            "   - Algoritmo Damerau-Levenshtein: Extiende Levenshtein añadiendo la operación de TRANSPOSICIÓN\n"
            "     (intercambio de 2 caracteres adyacentes, ej. 'ab' -> 'ba' con costo 1 en vez de 2).\n"
            "   - Token Sorting (Jaccard / Cosine): Para comparar nombres sin importar el orden de las palabras\n"
            "     (ej. 'Perez, Juan' vs 'Juan Perez')."
        )
        txt_teoria.insert(tk.END, propuesta_texto)
        txt_teoria.config(state=tk.DISABLED)

    def _procesar_comparacion(self):
        c1 = self.entry_cad1.get()
        c2 = self.entry_cad2.get()

        res_txt = ""

        # a) Intento de Cálculo de Hamming
        try:
            dist_hamming = calcular_distancia_hamming(c1, c2)
            res_txt += f"• Distancia de Hamming: {dist_hamming} diferencias posición a posición.\n"
        except ValueError as err:
            res_txt += f"• Distancia de Hamming: NO APLICABLE\n  [Causa]: {err}\n"

        # b) y c) Levenshtein Directo
        dist_lev, matriz = calcular_distancia_levenshtein(c1, c2)
        res_txt += f"\n• Distancia de Levenshtein Directa: {dist_lev} operaciones mínimas (ediciones).\n"

        # d) Heurística de Normalización y Porcentaje
        sim_pct, dist_norm, texto_norm = heuristica_similitud(c1, c2)
        res_txt += (
            f"\n• HEURÍSTICA Y NORMALIZACIÓN PROPUESTA:\n"
            f"  - Cadenas Normalizadas: {texto_norm}\n"
            f"  - Distancia Levenshtein en Normalizado: {dist_norm}\n"
            f"  - Grado de Similitud Algorítmica: {sim_pct:.2f}%\n"
        )

        self.txt_resultados.config(state=tk.NORMAL)
        self.txt_resultados.delete("1.0", tk.END)
        self.txt_resultados.insert(tk.END, res_txt)
        self.txt_resultados.config(state=tk.DISABLED)

        # Renderizar la Matriz de Levenshtein
        self._renderizar_matriz(c1, c2, matriz)

    def _renderizar_matriz(self, c1: str, c2: str, matriz: list[list[int]]):
        self.txt_matriz.config(state=tk.NORMAL)
        self.txt_matriz.delete("1.0", tk.END)

        header = "      Ø  " + "  ".join(f"{ch:>2}" for ch in c2) + "\n"
        self.txt_matriz.insert(tk.END, header)
        self.txt_matriz.insert(tk.END, "   " + "---" * (len(c2) + 2) + "\n")

        filas_labels = ["Ø"] + list(c1)
        for idx, fila in enumerate(matriz):
            lbl = filas_labels[idx]
            vals = "  ".join(f"{val:>2}" for val in fila)
            self.txt_matriz.insert(tk.END, f"{lbl:>2} | {vals}\n")

        self.txt_matriz.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = AppComparadorCadenas()
    app.mainloop()
