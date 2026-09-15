# Analizador de Entropía y Cabecera de Imágenes (BMP vs. JPG)

Aplicación de escritorio en Python para el análisis de fuentes de información y entropía de Shannon ($H(X)$) en archivos de imagen, comparando formatos sin compresión (**BMP**) contra formatos comprimidos (**JPG/JPEG**).

---

## 🎯 Descripción y Funcionalidades

* **Análisis de Cabecera BMP:** Decodificación directa del *File Header* (14 bytes) y el *DIB Header* para obtener la firma del archivo, tamaño total, offset de datos, dimensiones ($Ancho \times Alto$) y profundidad de color (bpp).
* **Cálculo de Entropía de Shannon:** Procesa el arreglo de bytes del archivo completo para generar el histograma de frecuencias, la distribución de probabilidades $P(X)$ sobre el alfabeto $\{0, 1, \dots, 255\}$ y la entropía $H(X)$ en bits/byte.
* **Visualización Gráfica:** Renderizado interactivo mediante Matplotlib empaquetado en la interfaz para comparar la distribución de bytes entre ambos formatos.

---

## 🛠️ Requisitos del Sistema y Dependencias

El proyecto requiere **Python 3.10** o superior y las siguientes librerías:

### 1. Módulos Estándar (Incluidos en Python)
* **`struct`**: Lectura y desempaquetado de las estructuras binarias del encabezado BMP[cite: 5].
* **`pathlib`**: Gestión e inspección de rutas en el sistema de archivos[cite: 5].
* **`tkinter`**: Creación de la interfaz gráfica de usuario (GUI)[cite: 5].

### 2. Librerías de Terceros
* **`numpy`**: Lectura eficiente de vectores de bytes (`np.fromfile`) y cómputo de histogramas (`np.bincount`)[cite: 5].
* **`matplotlib`**: Generación de gráficos e integración con Tkinter (`FigureCanvasTkAgg`)[cite: 5].

---

## 🚀 Guía de Instalación y Ejecución en Ubuntu / Debian

### Paso 1: Instalar la interfaz Tkinter en el sistema
En Ubuntu/Debian, el módulo `tkinter` requiere instalar un paquete del sistema operativo:

```bash
sudo apt update
sudo apt install -y python3-tk