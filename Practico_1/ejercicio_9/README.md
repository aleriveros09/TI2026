# Simulación y Análisis Teórico de Canal Binario Simétrico (BSC)

Sistema cliente-servidor multihilo en Python para la simulación, estimación empírica de tasa de error de bit (BER) y modelado matemático de la Capacidad de Canal en un **Canal Binario Simétrico (BSC)** sin memoria[cite: 12, 13].

---

## 🎯 Descripción y Funcionalidades

* **Servidor BSC (`servidor_bsc.py`):**
  * Modela un canal BSC determinista de probabilidad de error oculta ($p$) basada en semilla maestra.
  * Arquitectura concurrente multihilo para atender múltiples clientes en simultáneo[cite: 13].
  * Protocolo de enmarcado sobre TCP con encabezados de 4 bytes (Big-Endian) para evitar la fragmentación de mensajes[cite: 13].
* **Cliente BSC (`cliente_bsc.py`):**
  * **Fase 1 (Prueba Empírica):** Envío de tramas sintéticas ($100$, $10.000$ y $1.000.000$ de bits) para demostrar la convergencia del BER empírico hacia la probabilidad $p$ real según la Ley de los Grandes Números.
  * **Demostración Práctica:** Conversión de texto ASCII a binario y reconstrucción tras el paso por el canal ruidoso.
  * **Fase 2 (Modelado Teórico):** Reconstrucción de la matriz de transición $P(Y|X)$, cálculo de la Entropía de Salida $H(Y)$, la Entropía Condicional $H(Y|X)$, la Información Mutua $I(X;Y)$ y la Capacidad Teórica del Canal ($C = 1 - H(p)$).

---

## 🛠️ Requisitos del Sistema y Dependencias

El sistema requiere **Python 3.10** o superior[cite: 12, 13].

### Módulos Estándar Utilizados (Incluidos en Python)
No requiere la instalación de ningún paquete de terceros vía `pip`[cite: 12, 13]. Hace uso exclusivo de la librería estándar de Python:
* **`socket`**: Comunicación de red bajo protocolo TCP/IP[cite: 12, 13].
* **`struct`**: Empaquetado y desempaquetado de encabezados de longitud de 32 bits (`!I`)[cite: 12, 13].
* **`threading`**: Manejo de hilos concurrentes para la atención de clientes en el servidor[cite: 13].
* **`math`**: Funciones matemáticas para el cálculo de entropías ($\log_2$).
* **`random`**: Generación de secuencias aleatorias sintéticas y simulación del ruido[cite: 12, 13].

---

## 🚀 Guía de Instalación y Ejecución en Ubuntu / Debian

No se requieren paquetes adicionales del sistema operativo ya que los módulos pertenecen al *core* de Python[cite: 12, 13].

### Paso 1: Crear y activar un entorno virtual (Opcional)
```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate

### Paso 2: Ejecutar el servidor
```bash
python3 servidor_bsc.py
