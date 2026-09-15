# Analizador de Entropía, Redundancia e Índice de Coincidencia (TXT vs. ZIP)

Aplicación de escritorio en Python orientada al análisis de la información y criptoanálisis estadístico. Permite comparar las propiedades de un archivo de texto plano (`.txt`) contra un archivo comprimido (`.zip`, `.rar`, etc.) evaluando la **Entropía de Shannon ($H$)**, la **Redundancia ($R$)** y el **Índice de Coincidencia de Friedman ($IC$)**.

---

## 🎯 Descripción y Funcionalidades

* **Cálculo Eficiente en $\mathcal{O}(N)$:** Lectura directa del flujo de bytes con `numpy` para procesar archivos de gran tamaño rápidamente.
* **Métricas Calculadas:**
  * **Entropía de Shannon ($H(X)$):** Medida en bits/byte sobre el alfabeto de bytes ($0 \text{ a } 255$)[cite: 7].
  * **Redundancia Porcentual ($R$):** Porcentaje de información superflua respecto a la entropía máxima ($H_{max} = 8\text{ bits/byte}$)[cite: 7].
  * **Índice de Coincidencia ($IC$):** Probabilidad de que dos bytes elegidos al azar en el archivo sean idénticos ($IC = \frac{\sum f_i(f_i-1)}{N(N-1)}$)[cite: 7].
* **Tabla Comparativa y Histogramas:** Presentación tabular de métricas e histogramas de probabilidad $P_i$ embebidos en la interfaz[cite: 7].

---

## 🛠️ Requisitos del Sistema y Dependencias

El programa requiere **Python 3.10** o superior[cite: 7].

### 1. Módulos Estándar (Incluidos en Python)
* **`math`**: Operaciones matemáticas base[cite: 7].
* **`pathlib`**: Gestión de rutas del sistema de archivos[cite: 7].
* **`tkinter`**: Creación de la interfaz gráfica de usuario y selección de archivos[cite: 7].

### 2. Librerías de Terceros (Requeridas)
* **`numpy`**: Lectura binaria optimizada (`np.fromfile`) y conteo de frecuencias (`np.bincount`)[cite: 7].
* **`matplotlib`**: Representación gráfica de las distribuciones de probabilidad e integración con Tkinter (`FigureCanvasTkAgg`)[cite: 7].

---

## 🚀 Guía de Instalación y Ejecución en Ubuntu / Debian

### Paso 1: Instalar soporte para Tkinter
En distribuciones basadas en Ubuntu/Debian, `tkinter` debe instalarse desde los repositorios del sistema:

```bash
sudo apt update
sudo apt install -y python3-tk