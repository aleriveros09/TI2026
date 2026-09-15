# Validador de CUIT/CUIL - Algoritmo Módulo 11

Aplicación de escritorio en Python para la verificación y validación de claves tributarias e identificaciones laborales (CUIT/CUIL en Argentina) mediante la aplicación del algoritmo de **Checksum Módulo 11**.

---

## 🎯 Descripción y Funcionalidades

* **Sanitización de Entrada:** Acepta cadenas numéricas directamente o con formato de guiones y espacios (ej. `20-32986417-8` o `20329864178`).
* **Validación de Checksum (Módulo 11):** Implementa la serie de pesos $[5, 4, 3, 2, 7, 6, 5, 4, 3, 2]$ sobre los primeros 10 dígitos para calcular el dígito verificador esperable ($11 - \text{resto}$) y contempla las excepciones normativas (resto $0$ y resto $1$).
* **Desglose Algorítmico Detallado:** Muestra paso a paso el cálculo matemático ejecutado (productos ponderados, suma acumulada, operación residuo y comparación de dígitos)[cite: 10].
* **Interfaz Interactiva:** Construida sobre Tkinter con resaltado de estado y panel de reporte detallado[cite: 10].

---

## 🛠️ Requisitos del Sistema y Dependencias

El programa requiere **Python 3.10** o superior[cite: 10].

### Módulos Estándar Utilizados (Incluidos en Python)
No requiere la instalación de librerías de terceros externas (sin necesidad de `pip install`)[cite: 10]. Utiliza exclusivamente la biblioteca estándar:
* **`tkinter` / `ttk`**: Construcción de la interfaz gráfica de usuario y elementos de formulario[cite: 10].

---

## 🚀 Guía de Instalación y Ejecución en Ubuntu / Debian

### Paso 1: Instalar el soporte de Tkinter en Ubuntu
En distribuciones basadas en Ubuntu o Debian, el paquete de Tkinter debe instalarse desde el gestor de paquetes del sistema (`apt`):

```bash
sudo apt update
sudo apt install -y python3-tk