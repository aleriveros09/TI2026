import math
import tkinter as tk
from tkinter import messagebox, ttk


# ==============================================================================
# MÓDULO DE LÓGICA MATEMÁTICA Y TEORÍA DE LA INFORMACIÓN
# ==============================================================================

def calcular_entropia_shannon(vector_probabilidades):
    """
    Calcula la Entropía de Shannon H(V) = - sum(p_i * log2(p_i))
    filtrando los términos donde p_i = 0 para evitar log2(0).
    """
    entropia = 0.0
    for p in vector_probabilidades:
        if p > 0.0:
            entropia -= p * math.log2(p)
    return entropia


def calcular_capacidad_busqueda_exhaustiva(matriz_P_Y_dado_X):
    """
    Realiza la Búsqueda Exhaustiva (fuerza bruta) barriendo P(X=0) desde 0.00 a 1.00
    con un paso discreto de 0.01 para encontrar la Capacidad del Canal C = max I(X;Y).
    """
    capacidad_maxima = -1.0
    mejor_px0 = 0.0
    mejor_px1 = 0.0
    mejor_py = []
    mejor_h_y = 0.0
    mejor_h_y_dado_x = 0.0

    # b) Búsqueda Exhaustiva: Barrido iterativo de P(X=0) con paso 0.01
    # Usamos enteros de 0 a 100 para evitar imprecisiones de coma flotante en los bucles
    for i in range(101):
        px0 = i / 100.0
        px1 = 1.0 - px0
        P_X = [px0, px1]

        # c) Cálculo de probabilidades de salida P(Y) vía Teorema de la Probabilidad Total:
        # P(Y_j) = sum_i P(X_i) * P(Y_j | X_i)
        P_Y = [0.0, 0.0, 0.0, 0.0]
        for j in range(4):
            P_Y[j] = (P_X[0] * matriz_P_Y_dado_X[0][j]) + (P_X[1] * matriz_P_Y_dado_X[1][j])

        # c) Entropía de la salida H(Y)
        H_Y = calcular_entropia_shannon(P_Y)

        # c) Entropía Condicional (Ruido del Canal) H(Y|X) = sum_i P(X_i) * H(Y | X = x_i)
        H_Y_dado_X0 = calcular_entropia_shannon(matriz_P_Y_dado_X[0])
        H_Y_dado_X1 = calcular_entropia_shannon(matriz_P_Y_dado_X[1])
        H_Y_dado_X = (P_X[0] * H_Y_dado_X0) + (P_X[1] * H_Y_dado_X1)

        # c) Información Mutua I(X;Y) = H(Y) - H(Y|X)
        informacion_mutua = H_Y - H_Y_dado_X

        # d) Maximización: Comparación e identificación del valor máximo registrado
        if informacion_mutua > capacidad_maxima:
            capacidad_maxima = informacion_mutua
            mejor_px0 = px0
            mejor_px1 = px1
            mejor_py = P_Y
            mejor_h_y = H_Y
            mejor_h_y_dado_x = H_Y_dado_X

    return {
        "C": capacidad_maxima,
        "P_X0": mejor_px0,
        "P_X1": mejor_px1,
        "P_Y": mejor_py,
        "H_Y": mejor_h_y,
        "H_Y_dado_X": mejor_h_y_dado_x,
    }


# ==============================================================================
# MÓDULO DE INTERFAZ GRÁFICA DE USUARIO (GUI - Tkinter)
# ==============================================================================

class AppCapacidadCanal:
    def __init__(self, root):
        self.root = root
        self.root.title("Teoría de la Información - Capacidad de Canal (2x4)")
        self.root.geometry("640x680")
        self.root.resizable(False, False)

        # Configuración de estilos visuales
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Matriz de entradas (2 filas x 4 columnas de Entry widgets)
        self.entries_matriz = []

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Título principal
        frame_titulo = ttk.Frame(self.root, padding=10)
        frame_titulo.pack(fill="x")
        lbl_titulo = ttk.Label(
            frame_titulo,
            text="Cálculo de Capacidad de Canal (Binario a Cuaternario)",
            font=("Helvetica", 13, "bold"),
        )
        lbl_titulo.pack()

        # a) Panel de Ingreso de la Matriz P(Y|X)
        frame_matriz = ttk.LabelFrame(
            self.root, text=" Matriz de Transición del Canal P(Y|X) [2x4] ", padding=15
        )
        frame_matriz.pack(fill="x", padx=15, pady=10)

        # Encabezados de columna (Salidas Y_j)
        ttk.Label(frame_matriz, text="").grid(row=0, column=0, padx=5, pady=5)
        for j in range(4):
            lbl_col = ttk.Label(
                frame_matriz, text=f"Y = {j}", font=("Helvetica", 10, "bold")
            )
            lbl_col.grid(row=0, column=j + 1, padx=10, pady=5)

        # Matriz por defecto (Ejemplo: Canal BSC extendido)
        matriz_defecto = [
            [0.70, 0.15, 0.10, 0.05],
            [0.05, 0.10, 0.15, 0.70],
        ]

        # Creación dinámica de la grilla de celdas 2x4
        for i in range(2):
            lbl_row = ttk.Label(
                frame_matriz, text=f"X = {i}:", font=("Helvetica", 10, "bold")
            )
            lbl_row.grid(row=i + 1, column=0, padx=10, pady=5, sticky="e")
            fila_entries = []
            for j in range(4):
                entry = ttk.Entry(frame_matriz, width=10, justify="center")
                entry.insert(0, str(matriz_defecto[i][j]))
                entry.grid(row=i + 1, column=j + 1, padx=5, pady=5)
                fila_entries.append(entry)
            self.entries_matriz.append(fila_entries)

        # Botón para ejecutar el cálculo
        btn_calcular = ttk.Button(
            self.root, text="⚡ Calcular Capacidad de Canal (C)", command=self._procesar_calculo
        )
        btn_calcular.pack(fill="x", padx=15, pady=10)

        # e) Panel de Resultados
        frame_resultados = ttk.LabelFrame(
            self.root, text=" Resultados de la Maximización ", padding=15
        )
        frame_resultados.pack(fill="both", expand=True, padx=15, pady=10)

        self.txt_resultados = tk.Text(
            frame_resultados,
            font=("Consolas", 10),
            bg="#F8F9FA",
            fg="#212529",
            relief="solid",
            bd=1,
            wrap="word",
        )
        self.txt_resultados.pack(fill="both", expand=True)

    def _procesar_calculo(self):
        """Valida las entradas de usuario y ejecuta el algoritmo de optimización."""
        matriz_P_Y_dado_X = []

        # a) Validación matemática de los valores ingresados
        try:
            for i in range(2):
                fila = []
                for j in range(4):
                    valor = float(self.entries_matriz[i][j].get().strip())
                    if valor < 0.0 or valor > 1.0:
                        raise ValueError(
                            f"La probabilidad P(Y={j}|X={i}) = {valor} está fuera del rango [0, 1]."
                        )
                    fila.append(valor)

                # a) Validar que la suma de cada fila sea estrictamente igual a 1
                suma_fila = sum(fila)
                if not math.isclose(suma_fila, 1.0, abs_tol=1e-5):
                    messagebox.showerror(
                        "Error de Validación",
                        f"La suma de las probabilidades de la Fila X={i} debe ser 1.0.\n"
                        f"Suma actual: {suma_fila:.5f}",
                    )
                    return
                matriz_P_Y_dado_X.append(fila)

        except ValueError as err:
            messagebox.showerror("Entrada Inválida", f"Error en las probabilidades: {err}")
            return

        # b, c, d) Ejecución de la Búsqueda Exhaustiva
        res = calcular_capacidad_busqueda_exhaustiva(matriz_P_Y_dado_X)

        # e) Formateo y visualización de resultados por pantalla
        self.txt_resultados.delete("1.0", tk.END)
        salida = (
            "==========================================================\n"
            "              CAPACIDAD DE CANAL ENCONTRADA               \n"
            "==========================================================\n\n"
            f"  • Capacidad del Canal (C): {res['C']:.6f} bits/símbolo\n\n"
            "----------------------------------------------------------\n"
            "  DISTRIBUCIÓN ÓPTIMA DE LA FUENTE P(X):\n"
            "----------------------------------------------------------\n"
            f"  • P(X = 0) = {res['P_X0']:.2f}\n"
            f"  • P(X = 1) = {res['P_X1']:.2f}\n\n"
            "----------------------------------------------------------\n"
            "  PROBABILIDADES DE SALIDA P(Y) CORRESPONDIENTES:\n"
            "----------------------------------------------------------\n"
            f"  • P(Y = 0) = {res['P_Y'][0]:.6f}\n"
            f"  • P(Y = 1) = {res['P_Y'][1]:.6f}\n"
            f"  • P(Y = 2) = {res['P_Y'][2]:.6f}\n"
            f"  • P(Y = 3) = {res['P_Y'][3]:.6f}\n\n"
            "----------------------------------------------------------\n"
            "  DESGLOSE DE ENTROPÍAS EN EL PUNTO ÓPTIMO:\n"
            "----------------------------------------------------------\n"
            f"  • Entropía de Salida H(Y)           = {res['H_Y']:.6f} bits\n"
            f"  • Ruido del Canal H(Y|X)           = {res['H_Y_dado_X']:.6f} bits\n"
            f"  • Inform. Mutua I(X;Y) = H(Y)-H(Y|X) = {res['C']:.6f} bits\n"
            "==========================================================\n"
        )
        self.txt_resultados.insert(tk.END, salida)


# Punto de entrada principal
if __name__ == "__main__":
    root = tk.Tk()
    app = AppCapacidadCanal(root)
    root.mainloop()
