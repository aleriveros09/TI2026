# Análisis de Entropía y Cabecera de Audio (WAV vs. MP3) — TDI 2026

Aplicación de escritorio en Python desarrollada para el análisis estadístico de señales de audio, comparación de entropía de Shannon ($H(X)$) y evaluación del nivel de redundancia entre formatos de audio sin compresión (**WAV**) y comprimidos con pérdida (**MP3**).

---

## 🎯 Descripción y Funcionalidades

* **Análisis de Cabecera RIFF/WAVE:** Decodificación byte a byte de los primeros 44 bytes estándar para extraer canales, frecuencia de muestreo, tasa de bytes y profundidad de bits.
* **Cálculo de Entropía de Shannon:** Procesamiento de la distribución de probabilidades de la fuente $P(X)$ sobre el alfabeto de bytes ($0 \text{ a } 255$) para calcular $H(X)$ en bits/byte y su redundancia porcentual asociada.
* **Visualización de Histogramas:** Gráficas comparativas e interactivas empotradas en la interfaz mediante Matplotlib.

---

## 🛠️ Requisitos del Sistema y Dependencias

El programa requiere **Python 3.10** o superior y las siguientes librerías:

### 1. Módulos Estándar (Incluidos en Python)
* **`struct`**: Unpacking binario de los 36/44 bytes de la cabecera RIFF[cite: 4].
* **`pathlib`**: Gestión de rutas del sistema de archivos[cite: 4].
* **`tkinter`**: Framework base de la interfaz gráfica y selección de archivos[cite: 4].

### 2. Librerías Externas
* **`numpy`**: Procesamiento vectorizado de bytes (`np.bincount`, `np.fromfile`)[cite: 4].
* **`matplotlib`**: Generación y renderizado de histogramas ($P_i$ vs $S_i$)[cite: 4].

---

## 🚀 Guía de Instalación y Ejecución en Ubuntu / Debian

### 1. Instalar el soporte de Tkinter en Ubuntu
En distribuciones basadas en Debian/Ubuntu, el motor GUI de Tkinter debe instalarse desde los repositorios del sistema:

```bash
sudo apt update
sudo apt install -y python3-tk