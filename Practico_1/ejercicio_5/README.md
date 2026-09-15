# Gestión de Almacenamiento: Bitwise (Bit-Packing) vs. CSV

Aplicación de escritorio en Python desarrollada para demostrar la optimización de almacenamiento en bases de datos mediante empaquetado a nivel de bits (**Bitwise Bit-Packing**) en registros de longitud fija frente a formatos de texto tradicional (**CSV**).

---

## 🎯 Descripción y Funcionalidades

* **Empaquetado de Booleanos (Bit-Packing):** Consolida 8 banderas booleanas (atributos como estudios, vivienda, obra social, etc.) en **1 solo byte** ($8\text{ bits}$) utilizando operaciones de desplazamiento y máscaras de bits (`OR` / `AND` bitwise).
* **Estructura Binaria de Longitud Fija:** Utiliza el módulo `struct` para empaquetar registros binarios de exactamente **133 bytes** por persona (60B nombre + 64B dirección + 8B DNI + 1B banderas).
* **Acceso Aleatorio $\mathcal{O}(1)$:** Permite indexar y acceder a cualquier registro en disco mediante cálculo directo de offset (`Posición = Índice × 133`).
* **Persistencia y Comparación:** Genera, guarda y lee archivos `.csv` y `.bin` calculando el porcentaje de ahorro de espacio e impactando los datos decodificados en una tabla interactiva (`ttk.Treeview`)[cite: 8].
* **Módulo de Análisis a Alta Escala:** Incluye un panel teórico donde se simula y cuantifica el impacto en I/O y espacio en disco al escalar la solución a 100 millones de registros[cite: 8].

---

## 🛠️ Requisitos del Sistema y Dependencias

El programa requiere **Python 3.10** o superior[cite: 8].

### Módulos Estándar Utilizados (Incluidos en Python)
No requiere la instalación de librerías de terceros externas (como `pip install`)[cite: 8]. Utiliza exclusivamente la biblioteca estándar de Python:
* **`struct`**: Empaquetado y desempaquetado de estructuras binarias C[cite: 8].
* **`csv`**: Lectura y escritura de archivos en formato CSV[cite: 8].
* **`pathlib`**: Manipulación e inspección de archivos en el sistema[cite: 8].
* **`tkinter` / `ttk`**: Construcción de la interfaz gráfica de usuario y visor de registros[cite: 8].

---

## 🚀 Guía de Instalación y Ejecución en Ubuntu / Debian

### Paso 1: Instalar el soporte de Tkinter en Ubuntu
En distribuciones basadas en Ubuntu o Debian, el paquete de Tkinter debe instalarse desde el gestor de paquetes del sistema operativo (`apt`):

```bash
sudo apt update
sudo apt install -y python3-tk