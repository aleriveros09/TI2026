import struct
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


def validar_archivos(ruta_wav: str, ruta_mp3: str) -> tuple[Path, Path]:
    """Punto a) Carga y Validación de extensiones."""
    path_wav = Path(ruta_wav)
    path_mp3 = Path(ruta_mp3)

    if not path_wav.is_file() or path_wav.suffix.lower() != ".wav":
        raise ValueError(
            f"El archivo '{ruta_wav}' no existe o no es un archivo .wav válido."
        )

    if not path_mp3.is_file() or path_mp3.suffix.lower() != ".mp3":
        raise ValueError(
            f"El archivo '{ruta_mp3}' no existe o no es un archivo .mp3 válido."
        )

    return path_wav, path_mp3


def analizar_cabecera_wav(path_wav: Path) -> dict:
    """Punto b) Análisis dinámico de cabecera RIFF/WAVE para prevenir errores de tamaño de chunk."""
    with open(path_wav, "rb") as f:
        # Validar identificador RIFF principal
        riff_header = f.read(12)
        if len(riff_header) < 12:
            raise ValueError("El archivo es demasiado corto para ser un WAV válido.")

        riff, chunk_size, wave = struct.unpack("<4sI4s", riff_header)
        if riff != b"RIFF" or wave != b"WAVE":
            raise ValueError("El archivo no posee un formato RIFF/WAVE válido.")

        datos_cabecera = {
            "RIFF Header": riff.decode("ascii", errors="ignore"),
            "Tamaño Archivo (bytes)": chunk_size + 8,
            "WAVE Header": wave.decode("ascii", errors="ignore"),
        }

        # Recorrer subchunks dinámicamente hasta encontrar 'fmt '
        while True:
            chunk_hdr = f.read(8)
            if len(chunk_hdr) < 8:
                break
            
            subchunk_id, subchunk_size = struct.unpack("<4sI", chunk_hdr)
            
            if subchunk_id == b"fmt ":
                fmt_data = f.read(subchunk_size)
                # Extraer los primeros 16 bytes esenciales del formato PCM
                audio_fmt, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack(
                    "<HHIIHH", fmt_data[:16]
                )
                datos_cabecera.update({
                    "Formato Audio (1=PCM)": audio_fmt,
                    "Número de Canales": num_channels,
                    "Frecuencia de Muestreo (Hz)": sample_rate,
                    "Byte Rate": byte_rate,
                    "Alineación de Bloque": block_align,
                    "Bits por Muestra": bits_per_sample,
                })
                break
            else:
                # Omitir chunks desconocidos o metadatos (LIST, JUNK, etc.)
                f.seek(subchunk_size, 1)

    print("\n" + "=" * 45)
    print("      DATOS DE LA CABECERA WAV (RIFF/WAVE)   ")
    print("=" * 45)
    for clave, valor in datos_cabecera.items():
        print(f"  {clave:<28}: {valor}")
    print("=" * 45 + "\n")

    return datos_cabecera

def calcular_distribucion_y_entropia(path_file: Path) -> tuple[np.ndarray, float]:
    """Puntos c) y e) Cálculo de probabilidades p_i por byte (0-255) y Entropía de Shannon."""
    # Lectura del archivo como un arreglo de bytes (0 a 255)
    datos_bytes = np.fromfile(path_file, dtype=np.uint8)

    # Conteo de frecuencia absoluta de cada símbolo (0..255)
    conteo = np.bincount(datos_bytes, minlength=256)

    # Distribución de probabilidad p_i
    p_i = conteo / len(datos_bytes)

    # Filtrar probabilidades mayor a cero para evitar log2(0)
    p_i_positivas = p_i[p_i > 0]

    # Cálculo de la Entropía de Shannon: H = - sum(p_i * log2(p_i))
    entropia = -np.sum(p_i_positivas * np.log2(p_i_positivas))

    return p_i, entropia


def graficar_histogramas(
    p_wav: np.ndarray,
    h_wav: float,
    p_mp3: np.ndarray,
    h_mp3: float,
) -> None:
    """Punto d) Generación e inspección visual de los histogramas de frecuencia."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    simbolos = np.arange(256)

    # Histograma WAV
    axes[0].bar(simbolos, p_wav, color="royalblue", width=1.0)
    axes[0].set_title(f"Audio WAV (Sin Compresión)\nEntropía H = {h_wav:.4f} bits/byte")
    axes[0].set_xlabel("Símbolo (Byte: 0 - 255)")
    axes[0].set_ylabel("Probabilidad (p_i)")
    axes[0].grid(True, linestyle="--", alpha=0.5)

    # Histograma MP3
    axes[1].bar(simbolos, p_mp3, color="crimson", width=1.0)
    axes[1].set_title(f"Audio MP3 (Comprimido)\nEntropía H = {h_mp3:.4f} bits/byte")
    axes[1].set_xlabel("Símbolo (Byte: 0 - 255)")
    axes[1].grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.show()


# Pipeline Principal
if __name__ == "__main__":
    # Ingrese las rutas de sus archivos locales para ejecutar
    ruta_wav = input("Ingrese la ruta del archivo .wav: ").strip('"')
    ruta_mp3 = input("Ingrese la ruta del archivo .mp3: ").strip('"')

    try:
        # a) Validación
        p_wav, p_mp3 = validar_archivos(ruta_wav, ruta_mp3)

        # b) Cabecera WAV
        analizar_cabecera_wav(p_wav)

        # c) y e) Distribución y Entropía
        prob_wav, h_wav = calcular_distribucion_y_entropia(p_wav)
        prob_mp3, h_mp3 = calcular_distribucion_y_entropia(p_mp3)

        print(f"Entropía del archivo WAV: {h_wav:.4f} bits/byte")
        print(f"Entropía del archivo MP3: {h_mp3:.4f} bits/byte")

        # d) Graficar
        graficar_histogramas(prob_wav, h_wav, prob_mp3, h_mp3)

    except Exception as e:
        print(f"\n[ERROR]: {e}")
