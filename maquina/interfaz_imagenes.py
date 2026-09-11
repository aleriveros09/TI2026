import struct
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


def analizar_cabecera_bmp(path_bmp: Path) -> dict:
    """Análisis de la cabecera estándar BMP (14 bytes File Header + DIB Header)."""
    with open(path_bmp, "rb") as f:
        file_header = f.read(14)
        if len(file_header) < 14:
            raise ValueError("El archivo BMP es demasiado corto.")

        type_bytes, file_size, reserved1, reserved2, offset_bits = struct.unpack(
            "<2sIHHI", file_header
        )
        firma = type_bytes.decode("ascii", errors="ignore")

        if firma != "BM":
            raise ValueError("Firma no válida. El archivo no es un mapa de bits 'BM'.")

        dib_size_bytes = f.read(4)
        dib_header_size = struct.unpack("<I", dib_size_bytes)[0]

        dib_body = f.read(dib_header_size - 4)
        width, height, planes, bit_count = struct.unpack("<iiHH", dib_body[:12])

        return {
            "Firma del Archivo": firma,
            "Tamaño Archivo (bytes)": file_size,
            "Offset Píxeles": offset_bits,
            "Ancho (píxeles)": width,
            "Alto (píxeles)": abs(height),
            "Planos de Color": planes,
            "Profundidad (bpp)": bit_count,
        }


def calcular_distribucion_y_entropia(path_file: Path) -> tuple[np.ndarray, float, int]:
    """Cálculo de probabilidades p_i por byte (0-255) y Entropía de Shannon H(X)."""
    datos_bytes = np.fromfile(path_file, dtype=np.uint8)
    tamano_total = len(datos_bytes)

    if tamano_total == 0:
        raise ValueError("El archivo está vacío.")

    conteo = np.bincount(datos_bytes, minlength=256)
    p_i = conteo / tamano_total

    p_i_positivas = p_i[p_i > 0]
    entropia = -np.sum(p_i_positivas * np.log2(p_i_positivas))

    return p_i, entropia, tamano_total


class AppAnalizadorImagenes(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Análisis de Entropía y Cabecera BMP vs. JPG")
        self.geometry("1100x820")

        self.path_bmp = None
        self.path_jpg = None

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Panel Superior: Selección de Archivos
        frame_controles = ttk.LabelFrame(self, text=" Selección de Imágenes ", padding=10)
        frame_controles.pack(fill=tk.X, padx=15, pady=10)

        # Controles BMP
        ttk.Label(frame_controles, text="Imagen BMP (.bmp):").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.entry_bmp = ttk.Entry(frame_controles, width=55)
        self.entry_bmp.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(
            frame_controles, text="Buscar BMP...", command=self._seleccionar_bmp
        ).grid(row=0, column=2, padx=5, pady=5)

        # Controles JPG
        ttk.Label(frame_controles, text="Imagen JPG (.jpg/.jpeg):").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.entry_jpg = ttk.Entry(frame_controles, width=55)
        self.entry_jpg.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(
            frame_controles, text="Buscar JPG...", command=self._seleccionar_jpg
        ).grid(row=1, column=2, padx=5, pady=5)

        # Botón Ejecutar Análisis
        btn_procesar = ttk.Button(
            frame_controles, text="Analizar Imágenes", command=self._procesar_imagenes
        )
        btn_procesar.grid(row=0, column=3, rowspan=2, padx=15, sticky=tk.NSEW)

        # Panel Medio: Datos de Cabecera y Resultados de Entropía
        frame_info = ttk.Frame(self)
        frame_info.pack(fill=tk.X, padx=15, pady=5)

        # Cuadro de Cabecera BMP
        self.frame_cabecera = ttk.LabelFrame(frame_info, text=" Cabecera BMP ", padding=10)
        self.frame_cabecera.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.txt_cabecera = tk.Text(
            self.frame_cabecera, height=6, font=("Consolas", 9), state=tk.DISABLED
        )
        self.txt_cabecera.pack(fill=tk.BOTH, expand=True)

        # Cuadro de Métricas de Entropía
        self.frame_entropia = ttk.LabelFrame(frame_info, text=" Entropía de Shannon ", padding=10)
        self.frame_entropia.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.lbl_h_bmp = ttk.Label(
            self.frame_entropia, text="BMP: Esperando análisis...", font=("Consolas", 10)
        )
        self.lbl_h_bmp.pack(anchor=tk.W, pady=4)

        self.lbl_h_jpg = ttk.Label(
            self.frame_entropia, text="JPG: Esperando análisis...", font=("Consolas", 10)
        )
        self.lbl_h_jpg.pack(anchor=tk.W, pady=4)

        # Panel Inferior: Canvas para Histogramas
        self.frame_grafico = ttk.Frame(self)
        self.frame_grafico.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.fig, self.axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _seleccionar_bmp(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Imagen BMP",
            filetypes=[("Mapa de bits BMP", "*.bmp"), ("Todos los Archivos", "*.*")],
        )
        if filename:
            self.path_bmp = Path(filename)
            self.entry_bmp.delete(0, tk.END)
            self.entry_bmp.insert(0, filename)

    def _seleccionar_jpg(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Imagen JPG",
            filetypes=[("Imagen JPG", "*.jpg *.jpeg"), ("Todos los Archivos", "*.*")],
        )
        if filename:
            self.path_jpg = Path(filename)
            self.entry_jpg.delete(0, tk.END)
            self.entry_jpg.insert(0, filename)

    def _procesar_imagenes(self):
        ruta_bmp = Path(self.entry_bmp.get().strip('"'))
        ruta_jpg = Path(self.entry_jpg.get().strip('"'))

        # Validación básica de existencia y extensión
        if not ruta_bmp.is_file() or ruta_bmp.suffix.lower() != ".bmp":
            messagebox.showerror("Error de Entrada", "Seleccione un archivo .bmp válido.")
            return

        if not ruta_jpg.is_file() or ruta_jpg.suffix.lower() not in [".jpg", ".jpeg"]:
            messagebox.showerror("Error de Entrada", "Seleccione un archivo .jpg/.jpeg válido.")
            return

        try:
            # 1. Parsear Cabecera BMP
            info_bmp = analizar_cabecera_bmp(ruta_bmp)
            self.txt_cabecera.config(state=tk.NORMAL)
            self.txt_cabecera.delete("1.0", tk.END)
            for k, v in info_bmp.items():
                self.txt_cabecera.insert(tk.END, f"{k:<25}: {v}\n")
            self.txt_cabecera.config(state=tk.DISABLED)

            # 2. Calcular Entropías
            p_bmp, h_bmp, sz_bmp = calcular_distribucion_y_entropia(ruta_bmp)
            p_jpg, h_jpg, sz_jpg = calcular_distribucion_y_entropia(ruta_jpg)

            self.lbl_h_bmp.config(
                text=f"BMP [{sz_bmp} bytes] -> Entropía H = {h_bmp:.4f} bits/byte"
            )
            self.lbl_h_jpg.config(
                text=f"JPG [{sz_jpg} bytes] -> Entropía H = {h_jpg:.4f} bits/byte"
            )

            # 3. Dibujar Histogramas
            self.axes[0].clear()
            self.axes[1].clear()
            simbolos = np.arange(256)

            self.axes[0].bar(simbolos, p_bmp, color="darkgreen", width=1.0)
            self.axes[0].set_title(f"BMP (Sin Compresión Espacial)\nH = {h_bmp:.4f} bits/byte")
            self.axes[0].set_xlabel("Símbolo (Byte: 0 - 255)")
            self.axes[0].set_ylabel("Probabilidad (p_i)")
            self.axes[0].grid(True, linestyle="--", alpha=0.5)

            self.axes[1].bar(simbolos, p_jpg, color="darkorange", width=1.0)
            self.axes[1].set_title(f"JPG (Comprimida DCT + Huffman)\nH = {h_jpg:.4f} bits/byte")
            self.axes[1].set_xlabel("Símbolo (Byte: 0 - 255)")
            self.axes[1].grid(True, linestyle="--", alpha=0.5)

            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error al Procesar", str(e))


if __name__ == "__main__":
    app = AppAnalizadorImagenes()
    app.mainloop()
