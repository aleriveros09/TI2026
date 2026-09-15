import struct
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


def analizar_cabecera_wav(path_wav: Path) -> dict:
    """Análisis de la cabecera estándar RIFF/WAVE (44 bytes)."""
    with open(path_wav, "rb") as f:
        header = f.read(44)

    if len(header) < 44:
        raise ValueError(
            "El archivo WAV es demasiado corto para contener una cabecera RIFF/WAVE válida."
        )

    # Desempaquetado exacto de los primeros 36 bytes definidos en la estructura del formato
    (
        riff,
        chunk_size,
        wave,
        fmt,
        subchunk1_size,
        audio_fmt,
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
    ) = struct.unpack("<4sI4s4sIHHIIHH", header[:36])

    return {
        "RIFF Header": riff.decode("ascii", errors="ignore"),
        "Tamaño Archivo (bytes)": chunk_size + 8,
        "WAVE Header": wave.decode("ascii", errors="ignore"),
        "Formato Audio (1=PCM)": audio_fmt,
        "Número de Canales": num_channels,
        "Frecuencia Muestreo (Hz)": sample_rate,
        "Byte Rate": byte_rate,
        "Alineación de Bloque": block_align,
        "Bits por Muestra": bits_per_sample,
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


class AppAnalizadorAudio(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Análisis de Entropía y Cabecera (WAV vs. MP3)")
        self.geometry("1100x820")

        self.path_wav = None
        self.path_mp3 = None

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Panel Superior: Selección de Archivos
        frame_controles = ttk.LabelFrame(
            self, text=" Selección de Archivos de Audio ", padding=10
        )
        frame_controles.pack(fill=tk.X, padx=15, pady=10)

        # Controles WAV
        ttk.Label(frame_controles, text="Audio WAV (.wav):").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.entry_wav = ttk.Entry(frame_controles, width=55)
        self.entry_wav.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(
            frame_controles, text="Buscar WAV...", command=self._seleccionar_wav
        ).grid(row=0, column=2, padx=5, pady=5)

        # Controles MP3
        ttk.Label(frame_controles, text="Audio MP3 (.mp3):").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.entry_mp3 = ttk.Entry(frame_controles, width=55)
        self.entry_mp3.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(
            frame_controles, text="Buscar MP3...", command=self._seleccionar_mp3
        ).grid(row=1, column=2, padx=5, pady=5)

        # Botón Ejecutar Análisis
        btn_procesar = ttk.Button(
            frame_controles, text="Analizar Audios", command=self._procesar_audios
        )
        btn_procesar.grid(row=0, column=3, rowspan=2, padx=15, sticky=tk.NSEW)

        # Panel Medio: Datos de Cabecera y Resultados de Entropía
        frame_info = ttk.Frame(self)
        frame_info.pack(fill=tk.X, padx=15, pady=5)

        # Cuadro de Cabecera WAV
        self.frame_cabecera = ttk.LabelFrame(
            frame_info, text=" Cabecera WAV (RIFF/WAVE) ", padding=10
        )
        self.frame_cabecera.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5)
        )

        self.txt_cabecera = tk.Text(
            self.frame_cabecera,
            height=7,
            font=("Consolas", 9),
            state=tk.DISABLED,
        )
        self.txt_cabecera.pack(fill=tk.BOTH, expand=True)

        # Cuadro de Métricas de Entropía
        self.frame_entropia = ttk.LabelFrame(
            frame_info, text=" Entropía de Shannon ", padding=10
        )
        self.frame_entropia.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0)
        )

        self.lbl_h_wav = ttk.Label(
            self.frame_entropia,
            text="WAV: Esperando análisis...",
            font=("Consolas", 10),
        )
        self.lbl_h_wav.pack(anchor=tk.W, pady=4)

        self.lbl_h_mp3 = ttk.Label(
            self.frame_entropia,
            text="MP3: Esperando análisis...",
            font=("Consolas", 10),
        )
        self.lbl_h_mp3.pack(anchor=tk.W, pady=4)

        # Panel Inferior: Canvas para Histogramas
        self.frame_grafico = ttk.Frame(self)
        self.frame_grafico.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.fig, self.axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _seleccionar_wav(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Archivo WAV",
            filetypes=[("Audio WAV", "*.wav"), ("Todos los Archivos", "*.*")],
        )
        if filename:
            self.path_wav = Path(filename)
            self.entry_wav.delete(0, tk.END)
            self.entry_wav.insert(0, filename)

    def _seleccionar_mp3(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Archivo MP3",
            filetypes=[("Audio MP3", "*.mp3"), ("Todos los Archivos", "*.*")],
        )
        if filename:
            self.path_mp3 = Path(filename)
            self.entry_mp3.delete(0, tk.END)
            self.entry_mp3.insert(0, filename)

    def _procesar_audios(self):
        ruta_wav = Path(self.entry_wav.get().strip('"'))
        ruta_mp3 = Path(self.entry_mp3.get().strip('"'))

        # Validación de extensiones y existencia
        if not ruta_wav.is_file() or ruta_wav.suffix.lower() != ".wav":
            messagebox.showerror(
                "Error de Entrada", "Seleccione un archivo .wav válido."
            )
            return

        if not ruta_mp3.is_file() or ruta_mp3.suffix.lower() != ".mp3":
            messagebox.showerror(
                "Error de Entrada", "Seleccione un archivo .mp3 válido."
            )
            return

        try:
            # 1. Parsear Cabecera WAV
            info_wav = analizar_cabecera_wav(ruta_wav)
            self.txt_cabecera.config(state=tk.NORMAL)
            self.txt_cabecera.delete("1.0", tk.END)
            for k, v in info_wav.items():
                self.txt_cabecera.insert(tk.END, f"{k:<26}: {v}\n")
            self.txt_cabecera.config(state=tk.DISABLED)

            # 2. Calcular Entropías
            p_wav, h_wav, sz_wav = calcular_distribucion_y_entropia(ruta_wav)
            p_mp3, h_mp3, sz_mp3 = calcular_distribucion_y_entropia(ruta_mp3)

            r_wav = (1.0 - (h_wav / 8.0)) * 100
            r_mp3 = (1.0 - (h_mp3 / 8.0)) * 100

            self.lbl_h_wav.config(
                text=f"WAV [{sz_wav} bytes] -> H = {h_wav:.4f} bits/byte | Redundancia = {r_wav:.2f}%"
            )
            self.lbl_h_mp3.config(
                text=f"MP3 [{sz_mp3} bytes] -> H = {h_mp3:.4f} bits/byte | Redundancia = {r_mp3:.2f}%"
            )

            # 3. Dibujar Histogramas
            self.axes[0].clear()
            self.axes[1].clear()
            simbolos = np.arange(256)

            self.axes[0].bar(simbolos, p_wav, color="royalblue", width=1.0)
            self.axes[0].set_title(
                f"Audio WAV (Sin Compresión)\nH = {h_wav:.4f} bits/byte"
            )
            self.axes[0].set_xlabel("Símbolo (Byte: 0 - 255)")
            self.axes[0].set_ylabel("Probabilidad (p_i)")
            self.axes[0].grid(True, linestyle="--", alpha=0.5)

            self.axes[1].bar(simbolos, p_mp3, color="crimson", width=1.0)
            self.axes[1].set_title(
                f"Audio MP3 (Comprimido)\nH = {h_mp3:.4f} bits/byte"
            )
            self.axes[1].set_xlabel("Símbolo (Byte: 0 - 255)")
            self.axes[1].grid(True, linestyle="--", alpha=0.5)

            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error al Procesar", str(e))


if __name__ == "__main__":
    app = AppAnalizadorAudio()
    app.mainloop()
