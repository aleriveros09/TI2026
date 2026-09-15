import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


def calcular_entropia_segundo_orden(
    path_archivo: Path,
) -> tuple[np.ndarray, float, float, float, int]:
    """
    Lee el archivo en O(N) y calcula:
    - Probabilidades marginales p(x_i)
    - Entropía de 1er orden H(X)
    - Entropía condicional de 2do orden H(X2|X1)
    - Redundancia basada en H(X2|X1)
    """
    datos_bytes = np.fromfile(path_archivo, dtype=np.uint8)
    tamano_total = len(datos_bytes)

    if tamano_total < 2:
        raise ValueError("El archivo debe contener al menos 2 bytes.")

    # 1. Frecuencias marginales O(N)
    conteo_1d = np.bincount(datos_bytes, minlength=256)
    p_x1 = conteo_1d / tamano_total

    # Entropía de 1er orden H(X1)
    p_x1_pos = p_x1[p_x1 > 0]
    h_1er_orden = -np.sum(p_x1_pos * np.log2(p_x1_pos))

    # 2. Bigramas consecutivos (x1, x2) O(N)
    bytes_x1 = datos_bytes[:-1]
    bytes_x2 = datos_bytes[1:]

    matriz_conjunta = np.zeros((256, 256), dtype=np.int64)
    np.add.at(matriz_conjunta, (bytes_x1, bytes_x2), 1)

    p_x1_x2 = matriz_conjunta / (tamano_total - 1)

    # 3. Entropía Condicional H(X2 | X1)
    p_x1_col = p_x1[:, np.newaxis]
    p_x2_dado_x1 = np.zeros_like(p_x1_x2)
    mask_p1 = p_x1_col > 0
    p_x2_dado_x1[mask_p1[:, 0], :] = (
        p_x1_x2[mask_p1[:, 0], :] / p_x1_col[mask_p1[:, 0]]
    )

    mask_valid = (p_x1_x2 > 0) & (p_x2_dado_x1 > 0)
    h_2do_orden = -np.sum(
        p_x1_x2[mask_valid] * np.log2(p_x2_dado_x1[mask_valid])
    )
    redundancia_2do = 1.0 - (h_2do_orden / 8.0)

    return p_x1, h_1er_orden, h_2do_orden, redundancia_2do, tamano_total


class AppEntropia(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Análisis de Entropía y Redundancia - Teoría de la Información")
        self.geometry("1100x750")

        self.path_txt = None
        self.path_zip = None

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Panel superior para controles y selección de archivos
        frame_controles = ttk.LabelFrame(self, text=" Selección de Archivos ", padding=10)
        frame_controles.pack(fill=tk.X, padx=15, pady=10)

        # Controles para Archivo 1 (Texto / Incomprimido)
        ttk.Label(frame_controles, text="Archivo 1 (.txt / raw):").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.entry_txt = ttk.Entry(frame_controles, width=60)
        self.entry_txt.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(
            frame_controles, text="Buscar...", command=self._seleccionar_txt
        ).grid(row=0, column=2, padx=5, pady=5)

        # Controles para Archivo 2 (Comprimido)
        ttk.Label(frame_controles, text="Archivo 2 (.zip / .rar):").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.entry_zip = ttk.Entry(frame_controles, width=60)
        self.entry_zip.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(
            frame_controles, text="Buscar...", command=self._seleccionar_zip
        ).grid(row=1, column=2, padx=5, pady=5)

        # Botón de Procesar
        btn_procesar = ttk.Button(
            frame_controles, text="Ejecutar Análisis", command=self._procesar_archivos
        )
        btn_procesar.grid(row=0, column=3, rowspan=2, padx=15, sticky=tk.NSEW)

        # Panel de Resultados Numéricos
        self.frame_resultados = ttk.LabelFrame(self, text=" Métricas de Entropía ", padding=10)
        self.frame_resultados.pack(fill=tk.X, padx=15, pady=5)

        self.lbl_res_txt = ttk.Label(
            self.frame_resultados, text="Archivo 1: -", font=("Consolas", 10)
        )
        self.lbl_res_txt.pack(anchor=tk.W, pady=2)

        self.lbl_res_zip = ttk.Label(
            self.frame_resultados, text="Archivo 2: -", font=("Consolas", 10)
        )
        self.lbl_res_zip.pack(anchor=tk.W, pady=2)

        # Contenedor para Gráficos
        self.frame_grafico = ttk.Frame(self)
        self.frame_grafico.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Inicialización de la figura de Matplotlib embebida
        self.fig, self.axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _seleccionar_txt(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Archivo de Texto o Sin Comprimir",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los Archivos", "*.*")],
        )
        if filename:
            self.path_txt = Path(filename)
            self.entry_txt.delete(0, tk.END)
            self.entry_txt.insert(0, filename)

    def _seleccionar_zip(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Archivo Comprimido",
            filetypes=[
                ("Archivos Comprimidos", "*.zip *.rar *.7z *.gz"),
                ("Todos los Archivos", "*.*"),
            ],
        )
        if filename:
            self.path_zip = Path(filename)
            self.entry_zip.delete(0, tk.END)
            self.entry_zip.insert(0, filename)

    def _procesar_archivos(self):
        ruta1 = self.entry_txt.get().strip('"')
        ruta2 = self.entry_zip.get().strip('"')

        if not ruta1 or not ruta2:
            messagebox.showwarning(
                "Atención", "Debe seleccionar ambos archivos antes de procesar."
            )
            return

        try:
            p_txt, h1_txt, h2_txt, r2_txt, sz_txt = (
                calcular_entropia_segundo_orden(Path(ruta1))
            )
            p_zip, h1_zip, h2_zip, r2_zip, sz_zip = (
                calcular_entropia_segundo_orden(Path(ruta2))
            )

            # Actualizar textos informativos
            self.lbl_res_txt.config(
                text=f"TXT  [{sz_txt} B] -> H(X) = {h1_txt:.4f} b/B | H(X2|X1) = {h2_txt:.4f} b/B | Redundancia 2do = {r2_txt*100:.2f}%"
            )
            self.lbl_res_zip.config(
                text=f"ZIP  [{sz_zip} B] -> H(X) = {h1_zip:.4f} b/B | H(X2|X1) = {h2_zip:.4f} b/B | Redundancia 2do = {r2_zip*100:.2f}%"
            )

            # Actualizar Gráficos
            self.axes[0].clear()
            self.axes[1].clear()
            simbolos = np.arange(256)

            self.axes[0].bar(simbolos, p_txt, color="teal", width=1.0)
            self.axes[0].set_title(
                f"Archivo 1 (.txt)\nH(X)={h1_txt:.3f} | H(X2|X1)={h2_txt:.3f} bits/byte"
            )
            self.axes[0].set_xlabel("Símbolo (Byte: 0 - 255)")
            self.axes[0].set_ylabel("Probabilidad (p_i)")
            self.axes[0].grid(True, linestyle="--", alpha=0.5)

            self.axes[1].bar(simbolos, p_zip, color="purple", width=1.0)
            self.axes[1].set_title(
                f"Archivo 2 (.zip)\nH(X)={h1_zip:.3f} | H(X2|X1)={h2_zip:.3f} bits/byte"
            )
            self.axes[1].set_xlabel("Símbolo (Byte: 0 - 255)")
            self.axes[1].grid(True, linestyle="--", alpha=0.5)

            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error de Procesamiento", str(e))


if __name__ == "__main__":
    app = AppEntropia()
    app.mainloop()
