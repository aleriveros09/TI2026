# Cálculo de Capacidad de Canal Discreto ($2 \times 4$)

Aplicación de escritorio en Python desarrollada para el análisis de canales de comunicación discretos con entrada binaria y salida cuaternaria ($2 \times 4$). Realiza la estimación de la **Capacidad de Canal ($C$)** y la **Distribución Óptima de la Fuente ($P(X)$)** mediante el algoritmo de **búsqueda exhaustiva** sobre la Información Mutua ($I(X;Y)$).

---

## 🎯 Descripción y Funcionalidades

* **Matriz de Transición Configurable $P(Y|X)$:** Entrada de probabilidades condicionales para un canal de $2$ entradas ($X \in \{0, 1\}$) y $4$ salidas ($Y \in \{0, 1, 2, 3\}$).
* **Validación Estricta de Probabilidades:** Verifica que cada entrada se encuentre en el rango $[0, 1]$ y que la suma por fila sea exactamente $1.0$ ($\sum_j P(Y_j|X_i) = 1.0$).
* **Algoritmo de Optimización por Búsqueda Exhaustiva:** Barre $P(X=0)$ en el rango $[0.00, 1.00]$ con un paso discreto de $0.01$ para encontrar el máximo global de la Información Mutua:
  $$C = \max_{P(X)} I(X;Y) = \max_{P(X)} [H(Y) - H(Y|X)]$$[cite: 11]
* **Desglose de Métricas de la Información:** Muestra en tiempo real la capacidad alcanzada (en bits/símbolo), las probabilidades de salida $P(Y)$, la entropía de salida $H(Y)$ y la entropía condicional o ruido del canal $H(Y|X)$[cite: 11].

---

## 🛠️ Requisitos del Sistema y Dependencias

El programa requiere **Python 3.10** o superior[cite: 11].

### Módulos Estándar Utilizados (Incluidos en Python)
No requiere la instalación de librerías de terceros (sin necesidad de `pip install`)[cite: 11]. Utiliza exclusivamente la biblioteca estándar de Python:
* **`math`**: Operaciones de logaritmo en base 2 (`math.log2`) y comparaciones flotantes (`math.isclose`)[cite: 11].
* **`tkinter` / `ttk`**: Interfaz gráfica de usuario, grilla de entradas y cuadros de diálogo interactivos[cite: 11].

---

## 🚀 Guía de Instalación y Ejecución en Ubuntu / Debian

### Paso 1: Instalar el soporte de Tkinter en el sistema
En distribuciones basadas en Ubuntu o Debian, el motor GUI para Python debe instalarse mediante el gestor de paquetes del sistema (`apt`):

```bash
sudo apt update
sudo apt install -y python3-tk