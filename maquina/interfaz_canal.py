import math
import tkinter as tk
from tkinter import messagebox, ttk


def log2(x: float) -> float:
    """Calcula log2 evitando log2(0) retornado 0 por definición de entropía (0 * log2(0) = 0)."""
    return math.log2(x) if x > 0 else 0.0


def calcular_capacidad_canal_exhaustiva(matriz_p_yx: list[list[float]], paso: float = 0.01):
    """
    Realiza una búsqueda exhaustiva sobre P(X=0) desde 0.00 hasta 1.00 con incremento 'paso'.
    Calcula P(Y), H(Y), H(Y|X) e I(X;Y) para determinar la Capacidad C y la P(X) óptima.
    """
    max_i = -1.0
    px_optima = None
    desglose_iteraciones = []

    # Iterar sobre P(X=0) de 0.0 a 1.0
    pasos_totales = int(round(1.0 / paso)) + 1

    for idx in range(pasos_totales):
        p_x0 = idx * paso
        if p_x0 > 1.0:
            p_x0 = 1.0
        p_x1 = 1.0 - p_x0

        px = [p_x0, p_x1]

        # 1. Probabilidades de salida P(Y) vía Teorema de Probabilidad Total
        # P(Y_j) = sum_i P(X_i) * P(Y_j | X_i)
        py = [0.0] * 4
        for j in range(4):
            py[j] = px[0] * matriz_p_yx[0][j] + px[1] * matriz_p_yx[1][j]

        # 2. Entropía de Salida H(Y) = - sum_j P(Y_j) * log2(P(Y_j))
        h_y = -sum(p * log2(p) for p in py)

        # 3. Entropía Condicional / Ruido de Canal H(Y|X) = sum_i P(X_i) * H(Y|X_i)
        # H(Y|X_i) = - sum_j P(Y_j|X_i) * log2(P(Y_j|X_i))
        h_y_dada_x0 = -sum(matriz_p_yx[0][j] * log2(matriz_p_yx[0][j]) for j in range(4))
        h_y_dada_x1 = -sum(matriz_p_yx[1][j] * log2(matriz_p_yx[1][j]) for j in range(4))

        h_yx = px[0] * h_y_dada_x0 + px[1] * h_y_dada_x1

        # 4. Información Mutua I(X;Y) = H(Y) - H(Y|X)
        i_xy = h_y - h_yx

        desglose_iteraciones.append((p_x0, p_x1, py, h_y, h_yx, i_xy))

        # 5. Maximización (Búsqueda de la Capacidad)
        if i_xy > max_i:
            max_i = i_xy
            px_optima = (p_x0, p_x1)

    return max_i, px_optima, desglose_iteraciones


class AppCapacidadCanal(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Capacidad de Canal (2x4) - Búsqueda Exhaustiva")
        self.geometry("800x650")

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Panel Superior: Entrada de la Matriz P(Y|X)
        frame_matriz = ttk.LabelFrame(self, text=" Matriz de Canal P(Y|X) [2 Entradas x 4 Salidas] ", padding=10)
        frame_matriz.pack(fill=tk.X, padx=15, pady=10)

        self.entries = []
        # Valores por defecto para prueba rápida
        valores_defecto = [
            [0.5, 0.5, 0.0, 0.0],  # P(Y|X=0)
            [0.0, 0.0, 0.5, 0.5]   # P(Y|X=1)
        ]

        for i in range(2):
            ttk.Label(frame_matriz, text=f"P(Y|X={i}):").grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            fila_entries = []
            for j in range(4):
                ttk.Label(frame_matriz, text=f"y{j}:").grid(row=i, column=2 * j + 1, padx=2, pady=5)
                entry = ttk.Entry(frame_matriz, width=8)
                entry.grid(row=i, column=2 * j + 2, padx=4, pady=5)
                entry.insert(0, str(valores_defecto[i][j]))
                fila_entries.append(entry)
            self.entries.append(fila_entries)

        btn_calcular = ttk.Button(frame_matriz, text="Calcular Capacidad", command=self._procesar_calculo)
        btn_calcular.grid(row=2, column=0, columnspan=9, pady=10)

        # Panel de Resultados Principales
        frame_resultados = ttk.LabelFrame(self, text=" Resultados de Maximización ", padding=10)
        frame_resultados.pack(fill=tk.X, padx=15, pady=5)

        self.lbl_capacidad = ttk.Label(frame_resultados, text="Capacidad C: -", font=("Segoe UI", 11, "bold"))
        self.lbl_capacidad.pack(anchor=tk.W, pady=2)

        self.lbl_px_opt = ttk.Label(frame_resultados, text="Distribución Óptima P(X): -", font=("Segoe UI", 10))
        self.lbl_px_opt.pack(anchor=tk.W, pady=2)

        # Tabla / Area de Texto con el Barrido
        frame_barrido = ttk.LabelFrame(self, text=" Registro de Búsqueda Exhaustiva (Paso 0.01) ", padding=10)
        frame_barrido.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.txt_log = tk.Text(frame_barrido, font=("Consolas", 9), wrap=tk.NONE)
        scrollbar_y = ttk.Scrollbar(frame_barrido, orient=tk.VERTICAL, command=self.txt_log.yview)
        scrollbar_x = ttk.Scrollbar(frame_barrido, orient=tk.HORIZONTAL, command=self.txt_log.xview)
        self.txt_log.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def _procesar_calculo(self):
        # 1. Lectura y Validación de Matriz
        matriz_p_yx = []
        try:
            for i in range(2):
                fila = []
                for j in range(4):
                    val = float(self.entries[i][j].get())
                    if not (0.0 <= val <= 1.0):
                        raise ValueError(f"Las probabilidades deben estar entre 0 y 1. Error en P(Y={j}|X={i}).")
                    fila.append(val)

                if not math.isclose(sum(fila), 1.0, abs_tol=1e-4):
                    raise ValueError(f"La suma de las probabilidades para P(Y|X={i}) debe ser 1.0 (Suma actual: {sum(fila):.4f}).")

                matriz_p_yx.append(fila)
        except ValueError as err:
            messagebox.showerror("Error de Entrada", str(err))
            return

        # 2. Búsqueda Exhaustiva
        capacidad, px_opt, historial = calcular_capacidad_canal_exhaustiva(matriz_p_yx, paso=0.01)

        # 3. Mostrar Resultados
        self.lbl_capacidad.config(text=f"Capacidad del Canal (C): {capacidad:.6f} bits/símbolo")
        self.lbl_px_opt.config(text=f"Distribución Óptima: P(X=0) = {px_opt[0]:.2f} | P(X=1) = {px_opt[1]:.2f}")

        # Renderizar Barrido Completo en la Caja de Texto
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.delete("1.0", tk.END)

        header = f"{'P(X=0)':<8} | {'P(X=1)':<8} | {'H(Y)':<10} | {'H(Y|X)':<10} | {'I(X;Y)':<12} | {'P(Y_0, Y_1, Y_2, Y_3)':<30}\n"
        self.txt_log.insert(tk.END, header)
        self.txt_log.insert(tk.END, "-" * 90 + "\n")

        for p0, p1, py, hy, hyx, i_xy in historial:
            py_str = f"[{py[0]:.3f}, {py[1]:.3f}, {py[2]:.3f}, {py[3]:.3f}]"
            linea = f"{p0:<8.2f} | {p1:<8.2f} | {hy:<10.5f} | {hyx:<10.5f} | {i_xy:<12.6f} | {py_str}\n"
            self.txt_log.insert(tk.END, linea)

        self.txt_log.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = AppCapacidadCanal()
    app.mainloop()
