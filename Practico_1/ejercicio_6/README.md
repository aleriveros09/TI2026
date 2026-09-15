# Medición de Distancia y Similitud entre Cadenas (Hamming vs. Levenshtein)

Aplicación de escritorio en Python desarrollada para la comparación algorítmica de cadenas de texto. Implementa el cálculo estricto de la **Distancia de Hamming**, la matriz de programación dinámica de la **Distancia de Levenshtein** y un proceso **heurístico de normalización** para la medición del porcentaje de similitud entre textos.

---

## 🎯 Descripción y Funcionalidades

* **Distancia de Hamming:** Evaluación posición a posición ($i$-ésimo elemento) para cadenas de igual longitud. Manejo de excepciones en caso de desfase en la cantidad de caracteres.
* **Distancia de Levenshtein ($\mathcal{O}(M \times N)$):** Matriz de programación dinámica para obtener el costo mínimo de edición mediante operaciones de inserción, eliminación y sustitución.
* **Renderizado de Matriz:** Visualización tabular e interactiva de la matriz de costos de Levenshtein resultante.
* **Heurística de Normalización y Similitud:**
  * **Limpieza Unicode (NFD):** Conversión a minúsculas, remoción de tildes/diacríticos y unificación de espacios[cite: 9].
  * **Ratio Relativo de Similitud (%):** Cálculo porcentual basado en la longitud máxima de las cadenas comparadas:
    $$\text{Similitud (\%)} = \left(1 - \frac{\text{Distancia Levenshtein}}{\text{Longitud Máxima}}\right) \times 100$$[cite: 9]
* **Módulo Teórico Explicativo:** Pestaña dedicada con la justificación de por qué Hamming falla ante desfases y propuestas de producción (Damerau-Levenshtein y Token Sorting)[cite: 9].

---

## 🛠️ Requisitos del Sistema y Dependencias

El programa requiere **Python 3.10** o superior[cite: 9].

### Módulos Estándar Utilizados (Incluidos en Python)
No requiere la instalación de librerías de terceros (sin necesidad de `pip install`)[cite: 9]. Utiliza exclusivamente la biblioteca estándar:
* **`unicodedata`**: Normalización Unicode (NFD) para la eliminación de tildes y diacríticos[cite: 9].
* **`tkinter` / `ttk`**: Construcción de la interfaz gráfica de usuario, pestañas (`Notebook`) y barras de desplazamiento[cite: 9].

---

## 🚀 Guía de Instalación y Ejecución en Ubuntu / Debian

### Paso 1: Instalar el soporte de Tkinter en Ubuntu
En distribuciones basadas en Ubuntu o Debian, el paquete de Tkinter debe instalarse desde el gestor de paquetes del sistema (`apt`):

```bash
sudo apt update
sudo apt install -y python3-tk