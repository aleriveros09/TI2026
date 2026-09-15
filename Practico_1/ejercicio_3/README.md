# Analizador de Entropía Condicional y Redundancia (2do Orden)

Aplicación en Python desarrollada para el análisis estadístico y la cuantificación de memoria en fuentes de información. Compara archivos de texto plano o sin comprimir contra archivos comprimidos mediante el cálculo de la **Entropía de 1er orden $H(X)$**, la **Entropía condicional de 2do orden $H(X_2|X_1)$** y la **Redundancia residual**.

---

## 🎯 Descripción y Funcionalidades

* **Modelado de Fuente con Memoria:** Transición del modelo de fuente de memoria nula a un modelo Markoviano de primer orden mediante parejas de bytes consecutivos (bigramas).
* **Procesamiento Eficiente $\mathcal{O}(N)$:** Construcción de la matriz de frecuencias conjuntas de $256 \times 256$ utilizando operaciones vectorizadas con `numpy.add.at`.
* **Cálculo de Métricas:**
  * **Entropía Marginal $H(X)$:** Medida de la incertidumbre promedio por byte individual[cite: 6].
  * **Entropía Condicional $H(X_2|X_1)$:** Medida de la incertidumbre restante sobre un byte dado el valor del byte anterior[cite: 6].
  * **Redundancia de 2do Orden:** $R = 1 - \frac{H(X_2|X_1)}{8}$[cite: 6].
* **Interfaz Gráfica e Histogramas:** Comparación visual de las distribuciones marginales $P(X)$ integrada con Matplotlib y Tkinter[cite: 6].

---

## 🛠️ Requisitos del Sistema y Dependencias

El entorno requiere **Python 3.10** o superior y las siguientes librerías:

### 1. Módulos Estándar (Incluidos en Python)
* **`pathlib`**: Manipulación de rutas en el sistema de archivos[cite: 6].
* **`tkinter`**: Módulo para la construcción de la interfaz gráfica y cuadros de diálogo[cite: 6].

### 2. Librerías de Terceros
* **`numpy`**: Procesamiento de vectores de bytes (`np.fromfile`), matriz de confusión de bigramas y cálculo de logs base 2[cite: 6].
* **`matplotlib`**: Generación de histogramas y su renderizado sobre Tkinter vía `FigureCanvasTkAgg`[cite: 6].

---

## 🚀 Guía de Instalación y Ejecución en Ubuntu / Debian

### Paso 1: Instalar la interfaz Tkinter en el sistema
En sistemas Linux basados en Debian/Ubuntu, `tkinter` debe instalarse desde los repositorios oficiales:

```bash
sudo apt update
sudo apt install -y python3-tk