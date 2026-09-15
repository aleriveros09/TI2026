import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


def analizar_archivo(path_file: Path) -> tuple[np.ndarray, float, float, float, int]:
    """
    Procesa un archivo byte a byte en O(N):
    - Frecuencia relativa p_i (0..255)
    - Entropia de Shannon H(X)
    - Redundancia R (%)
    - Indice de Coincidencia (IC)
    """
    datos_bytes = np.fromfile(path_file, dtype=np.uint8)
    N = len(datos_bytes)

    if N == 0:
        raise ValueError("El archivo está vacío.")

    # Conteo de ocurrencias de cada byte (0 a 255)
    frecuencias = np.bincount(datos_bytes, minlength=256)
    p_i = frecuencias / N

    # 1. Entropía de Shannon: H(X) = - sum(p_i * log2(p_i))
    p_i_pos = p_i[p_i > 0]
    entropia = -np.sum(p_i_pos * np.log2(p_i_pos))

    # 2. Redundancia: R = 1 - (H / H_max) donde H_max = 8 bits/byte
    redundancia = (1.0 - (entropia / 8.0)) * 100.0

    # 3. Índice de Coincidencia (IC): IC = sum(f_i * (f_i - 1)) / (N * (N - 1))
    if N > 1:
        ic = np.sum(frecuencias * (frecuencias - 1)) / (N * (N - 1))
    else:
        ic = 0.0

    return p_i, entropia, redundancia, ic, N


class AppAnalizadorTextoZip(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Analizador de Entropía, Redundancia e Índice de Coincidencia")
        self.geometry("1100x860")

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Frame Superior: Selección de Archivos
        frame_controles = ttk.LabelFrame(
            self, text=" Selección de Archivos ", padding=10
        )
        frame_controles.pack(fill=tk.X, padx=15, pady=10)

        # Archivo Texto (.txt)
        ttk.Label(frame_controles, text="Archivo Texto (.txt):").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.entry_txt = ttk.Entry(frame_controles, width=55)
        self.entry_txt.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(
            frame_controles, text="Buscar TXT...", command=self._seleccionar_txt
        ).grid(row=0, column=2, padx=5, pady=5)

        # Archivo Comprimido (.zip / .rar)
        ttk.Label(frame_controles, text="Archivo Comprimido (.zip/.rar):").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.entry_zip = ttk.Entry(frame_controles, width=55)
        self.entry_zip.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(
            frame_controles, text="Buscar ZIP...", command=self._seleccionar_zip
        ).grid(row=1, column=2, padx=5, pady=5)

        # Botón Procesar
        btn_procesar = ttk.Button(
            frame_controles, text="Analizar Archivos", command=self._procesar_archivos
        )
        btn_procesar.grid(row=0, column=3, rowspan=2, padx=15, sticky=tk.NSEW)

        # Frame Medio: Resultados Numéricos
        frame_resultados = ttk.LabelFrame(
            self, text=" Comparativa de Métricas ", padding=10
        )
        frame_resultados.pack(fill=tk.X, padx=15, pady=5)

        self.txt_resultados = tk.Text(
            frame_resultados, height=6, font=("Consolas", 10), state=tk.DISABLED
        )
        self.txt_resultados.pack(fill=tk.BOTH, expand=True)

        # Frame Inferior: Gráficos de Matplotlib
        self.frame_grafico = ttk.Frame(self)
        self.frame_grafico.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.fig, self.axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _seleccionar_txt(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Archivo de Texto",
            filetypes=[("Texto Plano", "*.txt"), ("Todos los Archivos", "*.*")],
        )
        if filename:
            self.entry_txt.delete(0, tk.END)
            self.entry_txt.insert(0, filename)

    def _seleccionar_zip(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Archivo Comprimido",
            filetypes=[
                ("Archivos Comprimidos", "*.zip *.rar *.7z"),
                ("Todos los Archivos", "*.*"),
            ],
        )
        if filename:
            self.entry_zip.delete(0, tk.END)
            self.entry_zip.insert(0, filename)

    def _procesar_archivos(self):
        path_txt = Path(self.entry_txt.get().strip('"'))
        path_zip = Path(self.entry_zip.get().strip('"'))

        if not path_txt.is_file():
            messagebox.showerror("Error", "Seleccione un archivo .txt válido.")
            return

        if not path_zip.is_file():
            messagebox.showerror("Error", "Seleccione un archivo comprimido válido.")
            return

        try:
            p_txt, h_txt, r_txt, ic_txt, n_txt = analizar_archivo(path_txt)
            p_zip, h_zip, r_zip, ic_zip, n_zip = analizar_archivo(path_zip)

            # Mostrar Resultados
            res_str = (
                f"{'Métrica / Archivo':<25} | {'TEXTO PURO (.txt)':<30} | {'COMPRIMIDO (.zip/.rar)':<30}\n"
                f"{'-'*90}\n"
                f"{'Tamaño Total':<25} | {n_txt:<30} bytes | {n_zip:<30} bytes\n"
                f"{'Entropía H(X)':<25} | {h_txt:<30.4f} bits/byte | {h_zip:<30.4f} bits/byte\n"
                f"{'Redundancia (R)':<25} | {r_txt:<30.2f} %         | {r_zip:<30.2f} %\n"
                f"{'Índice Coincidencia (IC)':<25} | {ic_txt:<30.6f}           | {ic_zip:<30.6f}\n"
            )

            self.txt_resultados.config(state=tk.NORMAL)
            self.txt_resultados.delete("1.0", tk.END)
            self.txt_resultados.insert(tk.END, res_str)
            self.txt_resultados.config(state=tk.DISABLED)

            # Graficar
            self.axes[0].clear()
            self.axes[1].clear()
            simbolos = np.arange(256)

            self.axes[0].bar(simbolos, p_txt, color="teal", width=1.0)
            self.axes[0].set_title(
                f"Texto Plano (.txt)\nH = {h_txt:.4f} b/B | IC = {ic_txt:.5f}"
            )
            self.axes[0].set_xlabel("Símbolo (Byte: 0 - 255)")
            self.axes[0].set_ylabel("Probabilidad (p_i)")
            self.axes[0].grid(True, linestyle="--", alpha=0.5)

            self.axes[1].bar(simbolos, p_zip, color="darkred", width=1.0)
            self.axes[1].set_title(
                f"Comprimido (.zip/.rar)\nH = {h_zip:.4f} b/B | IC = {ic_zip:.5f}"
            )
            self.axes[1].set_xlabel("Símbolo (Byte: 0 - 255)")
            self.axes[1].grid(True, linestyle="--", alpha=0.5)

            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error al Procesar", str(e))


if __name__ == "__main__":
    app = AppAnalizadorTextoZip()
    app.mainloop()
