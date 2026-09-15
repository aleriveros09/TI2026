# Teoría de la Información — Grupo 

Licenciatura en Ciencias de la Computación, 2026.

## Ejercicios

| # | Carpeta | Tema | Dependencias |
|---|---------|------|--------------|
| 1 | [`ejercicio_1/`](ejercicio_1/) | Entropía de señales de audio (WAV vs MP3) | numpy, matplotlib, tkinter |
| 2 | [`ejercicio_2/`](ejercicio_2/) | Entropía de imágenes (BMP vs JPG) | numpy, matplotlib, tkinter |
| 3 | [`ejercicio_3/`](ejercicio_3/) | Entropía de archivos (texto vs comprimido) | numpy, tkinter|
| 4 | [`ejercicio_4/`](ejercicio_4/) | Índice de Coincidencia | numpy, tkinter|
| 5 | [`ejercicio_5/`](ejercicio_5/) | Empaquetado a nivel de bits (CSV vs binario) | stdlib, tkinter|
| 6 | [`ejercicio_6/`](ejercicio_6/) | Distancia de Hamming y Levenshtein | stdlib, tkinter|
| 7 | [`ejercicio_7/`](ejercicio_7/) | Checksum CUIT/CUIL (Módulo 11) | stdlib, tkinter |
| 8 | [`ejercicio_8/`](ejercicio_8/) | Capacidad de canal por búsqueda exhaustiva | stdlib, tkinter |
| 9 | [`ejercicio_9/`](ejercicio_9/) | Canal Binario Simétrico por sockets TCP | stdlib |

Cada carpeta incluye su código, un `README.md` con instrucciones de uso y las respuestas teóricas del enunciado.
## Requisitos

```
pip install numpy matplotlib
```

Solo hacen falta para los ejercicios 1–4; el resto usa únicamente la librería estándar.

## Uso

Desde la carpeta de cada ejercicio:

```
cd ejercicio_N
python3 ejercicio_N.py
```

Ver el `README.md` de cada carpeta para las opciones específicas. El ejercicio 9 requiere levantar `servidor_bsc.py` en una terminal antes de correr `cliente_bsc.py` en otra.
