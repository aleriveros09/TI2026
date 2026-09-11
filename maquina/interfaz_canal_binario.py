import math
import tkinter as tk
from tkinter import ttk, messagebox


# -----------------------------------------------------------------------------
# 1. LÓGICA DE TEORÍA DE LA INFORMACIÓN (CANAL 2x4)
# -----------------------------------------------------------------------------
def calcular_entropia_vector(probabilidades: list[float]) -> float:
    """Calcula H(V) = -sum(p * log2(p)) para p > 0."""
    return -sum(p * math.log2(p) for p in probabilidades if p > 0)


def resolver_capacidad_canal_2x4(matriz_p_y_x: list[list[float]], paso: float = 0.01) -> dict:
    """
    Entrada: Matriz de transición P(Y|X) de dimensiones 2x4.
    Paso: Incremento para el barrido de P(X=0).
    Retorna un diccionario con la Capacidad C, P(X) óptima y vectores asociados.
    """
    max_i_xy = -1.0
    px0_optimo = 0.0
    px1_optimo = 0.0
    hy_optima = 0.0
    hy_x_optima = 0.0
    py_optima = []

    # Búsqueda exhaustiva evaluando P(X=0) de 0.00 a 1.00 en incrementos de 0.01
    pasos_totales = int(round(1.0 / paso))
    for i in range(pasos_totales + 1):
        px0 = i * paso
        px1 = 1.0 - px0

        px = [px0, px1]

        # 1. Probabilidades de salida P(Y_j) usando Probabilidad Total
        # P(Y_j) = P(X=0)*P(Y_j|X=0) + P(X=1)*P(Y_j|X=1)
        py = [
            px0 * matriz_p_y_x[0][j] + px1 * matriz_p_y_x[1][j]
            for j in range(4)
        ]

        # 2. Entropía de la salida H(Y)
        h_y = calcular_entropia_vector(py)

        # 3. Entropía Condicional / Ruido de Canal H(Y|X)
        # H(Y|X) = sum_i P(X_i) * H(Y|X=X_i)
        h_y_dado_x0 = calcular_entropia_vector(matriz_p_y_x[0])
        h_y_dado_x1 = calcular_entropia_vector(matriz_p_y_x[1])
        h_y_x = px0 * h_y_dado_x0 + px1 * h_y_dado_x1

        # 4. Información Mutua I(X;Y) = H(Y) - H(Y|X)
        i_xy = h_y - h_y_x

        # 5. Maximización (Búsqueda del valor pico)
        if i_xy > max_i_xy:
            max_i_xy = i_xy
            px0_optimo = px0
            px1_optimo = px1
            hy_optima = h_y
            hy_x_optima = h_y_x
            py_optima = py

    return {
        "capacidad_C": max_i_xy,
        "px0_optimo": px0_optimo,
        "px1_optimo": px1_optimo,
        "hy": hy_optima,
        "hy_x": hy_x_optima,
        "py_optimo": py_optima
    }


# -----------------------------------------------------------------------------
# 2. INTERFAZ GRÁFICA TKINTER
# -----------------------------------------------------------------------------
class AppCapacidadCanal(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Capacidad de Canal (2x4) - Búsqueda Exhaustiva")
        self.geometry("820x650")

        self.entries_matriz = []
        self._crear_interfaz()

    def _crear_interfaz(self):
        # Panel Superior: Entrada de la Matriz P(Y|X)
        frame_matriz = ttk.LabelFrame(self, text=" Matriz de Transición P(Y|X) [2 Filas x 4 Columnas] ", padding=10)
        frame_matriz.pack(fill=tk.X, padx=15, pady=10)

        # Encabezados de Columnas Y0, Y1, Y2, Y3
        ttk.Label(frame_matriz, text="X \\ Y", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=5, pady=5)
        for j in range(4):
            ttk.Label(frame_matriz, text=f"P(Y={j}|X)", font=("Segoe UI", 9, "bold")).grid(row=0, column=j+1, padx=5, pady=5)

        # Valores por defecto para prueba (Canal de 2 a 4 símbolos)
        valores_defecto = [
            [0.40, 0.30, 0.20, 0.10],  # Fila X=0
            [0.10, 0.20, 0.30, 0.40]   # Fila X=1
        ]

        # Entradas numéricas para la matriz
        for i in range(2):
            ttk.Label(frame_matriz, text=f"P(Y|X={i}):", font=("Segoe UI", 9, "bold")).grid(row=i+1, column=0, padx=5, pady=5)
            fila_entries = []
            for j in range(4):
                entry = ttk.Entry(frame_matriz, width=12, justify="center")
                entry.grid(row=i+1, column=j+1, padx=5, pady=5)
                entry.insert(0, str(valores_defecto[i][j]))
                fila_entries.append(entry)
            self.entries_matriz.append(fila_entries)

        btn_calcular = ttk.Button(
            self, text="Calcular Capacidad de Canal (C)", command=self._procesar_calculo
        )
        btn_calcular.pack(pady=10)

        # Panel de Resultados
        frame_resultados = ttk.LabelFrame(self, text=" Resultados de la Maximización ", padding=10)
        frame_resultados.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.txt_resultados = tk.Text(frame_resultados, font=("Consolas", 10), wrap=tk.WORD)
        self.txt_resultados.pack(fill=tk.BOTH, expand=True)

    def _procesar_calculo(self):
        matriz_p_y_x = []

        # a) Lectura y Validación Matemática de la Matriz
        for i in range(2):
            fila = []
            for j in range(4):
                val_str = self.entries_matriz[i][j].get()
                try:
                    val = float(val_str)
                    if val < 0.0 or val > 1.0:
                        messagebox.showerror("Error de Rango", f"El valor P(Y={j}|X={i}) debe estar entre 0.0 y 1.0.")
                        return
                    fila.append(val)
                except ValueError:
                    messagebox.showerror("Error de Tipo", f"Valor no válido en P(Y={j}|X={i}). Ingrese un número flotante.")
                    return

            # Validación de suma estricta de la fila = 1.0
            suma_fila = sum(fila)
            if not math.isclose(suma_fila, 1.0, abs_tol=1e-5):
                messagebox.showerror(
                    "Error de Validación Probabilística",
                    f"La suma de probabilidades de la fila X={i} es {suma_fila:.4f}.\n"
                    f"Debe ser estrictamente igual a 1.0."
                )
                return

            matriz_p_y_x.append(fila)

        # b, c, d, e) Ejecución del Barrido Exhaustivo y Maximización
        res = resolver_capacidad_canal_2x4(matriz_p_y_x, paso=0.01)

        # Formateo de salida
        py_str = ", ".join([f"P(Y={j}) = {val:.4f}" for j, val in enumerate(res['py_optimo'])])

        informe = (
            "========================================================================\n"
            "                 CAPACIDAD DEL CANAL (C) OBTENIDA                       \n"
            "========================================================================\n\n"
            f"• CAPACIDAD DE CANAL (C):  {res['capacidad_C']:.6f} bits/símbolo\n\n"
            "DISTRIBUCIÓN DE ENTRADA ÓPTIMA P(X):\n"
            f"  - P(X = 0) = {res['px0_optimo']:.2f}\n"
            f"  - P(X = 1) = {res['px1_optimo']:.2f}\n\n"
            "MÉTRICAS EN LA CAPACIDAD:\n"
            f"  - Entropía de Salida H(Y):       {res['hy']:.6f} bits/símbolo\n"
            f"  - Ruido del Canal H(Y|X):         {res['hy_x']:.6f} bits/símbolo\n"
            f"  - Información Mutua I(X;Y):      {res['capacidad_C']:.6f} bits/símbolo\n\n"
            f"DISTRIBUCIÓN DE SALIDA RESULTANTE P(Y):\n"
            f"  - {py_str}\n\n"
            "DETALLES DE LA BÚSQUEDA EXHAUSTIVA:\n"
            "  - Muestras evaluadas: 101 iteraciones (paso = 0.01).\n"
            "  - Algoritmo: Maximización por Fuerza Bruta sobre P(X=0) ∈ [0.00, 1.00]."
        )

        self.txt_resultados.config(state=tk.NORMAL)
        self.txt_resultados.delete("1.0", tk.END)
        self.txt_resultados.insert(tk.END, informe)
        self.txt_resultados.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = AppCapacidadCanal()
    app.mainloop()
