import math
import random
import socket
import struct


# -----------------------------------------------------------------------------
# PROTOCOLO DE RED (Compatible con el enmarcado de 4 bytes del servidor)
# -----------------------------------------------------------------------------
def recibir_exactamente(sock, cantidad):
    datos = bytearray()
    while len(datos) < cantidad:
        bloque = sock.recv(cantidad - len(datos))
        if not bloque:
            raise ConnectionError("Conexión cerrada por el servidor.")
        datos.extend(bloque)
    return bytes(datos)


def recibir_mensaje(sock):
    encabezado = recibir_exactamente(sock, 4)
    longitud = struct.unpack("!I", encabezado)[0]
    datos = recibir_exactamente(sock, longitud)
    return datos.decode("ascii")


def enviar_mensaje(sock, mensaje):
    datos = mensaje.encode("ascii")
    encabezado = struct.pack("!I", len(datos))
    sock.sendall(encabezado + datos)


# -----------------------------------------------------------------------------
# HERRAMIENTAS DE CONVERSIÓN Y TEORÍA DE LA INFORMACIÓN
# -----------------------------------------------------------------------------
def texto_a_binario(texto: str) -> str:
    return "".join(f"{ord(c):08b}" for c in texto)


def binario_a_texto(binario: str) -> str:
    caracteres = []
    for i in range(0, len(binario), 8):
        byte = binario[i : i + 8]
        if len(byte) == 8:
            caracteres.append(chr(int(byte, 2)))
    return "".join(caracteres)


def calcular_entropia_binaria(p: float) -> float:
    if p == 0.0 or p == 1.0:
        return 0.0
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)


def analizar_fase2(p_error: float, trama_enviada: str, trama_recibida: str):
    print("\n" + "=" * 60)
    print(" FASE 2: MODELADO MATEMÁTICO Y CAPACIDAD DEL CANAL")
    print("=" * 60)

    # 1. Matriz del Canal P(Y_j | X_i)
    print("\n1. MATRIZ DE TRANSICIÓN DEL CANAL P(Y|X):")
    print(
        f"   P(Y=0|X=0) = {1 - p_error:.6f}    P(Y=1|X=0) = {p_error:.6f}"
    )
    print(
        f"   P(Y=0|X=1) = {p_error:.6f}    P(Y=1|X=1) = {1 - p_error:.6f}"
    )

    # 2. Probabilidades de la Fuente P(X=0) y P(X=1)
    n = len(trama_enviada)
    cero_count = trama_enviada.count("0")
    uno_count = trama_enviada.count("1")

    p_x0 = cero_count / n
    p_x1 = uno_count / n

    print("\n2. PROBABILIDADES DE LA FUENTE (Trama enviada):")
    print(f"   P(X=0) = {p_x0:.6f} ({cero_count}/{n})")
    print(f"   P(X=1) = {p_x1:.6f} ({uno_count}/{n})")

    # 3. Información Mutua I(X;Y) = H(Y) - H(Y|X)
    # P(Y=0) = P(X=0)P(Y=0|X=0) + P(X=1)P(Y=0|X=1)
    p_y0 = p_x0 * (1 - p_error) + p_x1 * p_error
    p_y1 = p_x0 * p_error + p_x1 * (1 - p_error)

    h_y = calcular_entropia_binaria(p_y0)
    h_y_x = calcular_entropia_binaria(p_error)  # H(p) para BSC
    i_xy = h_y - h_y_x

    print("\n3. INFORMACIÓN MUTUA I(X;Y):")
    print(f"   Entropía de la salida H(Y) = {h_y:.6f} bits/símbolo")
    print(f"   Ruido del canal H(Y|X)     = {h_y_x:.6f} bits/símbolo")
    print(f"   Información Mutua I(X;Y)   = {i_xy:.6f} bits/símbolo")

    # 4. Capacidad del Canal C = 1 - H(p)
    capacidad = 1.0 - h_y_x
    print("\n4. CAPACIDAD DEL CANAL C:")
    print(f"   Capacidad Máxima C = 1 - H(p) = {capacidad:.6f} bits/símbolo")

    # 5. Análisis de Maximización
    porcentaje_max = (i_xy / capacidad * 100) if capacidad > 0 else 0
    print("\n5. ANÁLISIS DE MAXIMIZACIÓN:")
    print(
        f"   Se alcanzó el {porcentaje_max:.2f}% de la capacidad del canal."
    )


# -----------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------------------------------------
def ejecutar_cliente(host="127.0.0.1", puerto=5555):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, puerto))
    print(f"[+] Conectado al servidor BSC en {host}:{puerto}")

    try:
        # ---------------------------------------------------------------------
        # FASE 1: Transmisión y Tasa de Error Empírica (BER)
        # ---------------------------------------------------------------------
        print("\n" + "=" * 60)
        print(" FASE 1: BATERÍA DE PRUEBAS DE BER EMPÍRICO")
        print("=" * 60)

        tamaños_prueba = [100, 10000, 1000000]
        ber_calculados = []

        for N in tamaños_prueba:
            trama_orig = "".join(random.choice("01") for _ in range(N))
            enviar_mensaje(sock, trama_orig)
            trama_recibida = recibir_mensaje(sock)

            # Conteo de errores
            errores = sum(1 for a, b in zip(trama_orig, trama_recibida) if a != b)
            ber = errores / N
            ber_calculados.append(ber)

            print(
                f"• Trama de {N:>7} bits | Errores: {errores:>6} | BER Empírico: {ber:.6f}"
            )

        # El BER obtenido con 1.000.000 bits converge a la probabilidad p real
        p_estimada = ber_calculados[-1]
        print(f"\n[->] Probabilidad de Error 'p' descubierta: ~{p_estimada:.4f}")

        # Prueba de Transmisión de Texto
        frase = "Redes de Datos - Canal Binario Simetrico BSC 2026"
        bin_orig = texto_a_binario(frase)
        enviar_mensaje(sock, bin_orig)
        bin_recibido = recibir_mensaje(sock)
        texto_alterado = binario_a_texto(bin_recibido)

        print("\nEFECTO VISUAL DEL RUIDO EN TEXTO:")
        print(f"  Original: '{frase}'")
        print(f"  Recibido: '{texto_alterado}'")

        # ---------------------------------------------------------------------
        # FASE 2: Modelado Matemático con la trama más grande
        # ---------------------------------------------------------------------
        analizar_fase2(p_estimada, trama_orig, trama_recibida)

        # Finalizar sesión
        enviar_mensaje(sock, "SALIR")

    finally:
        sock.close()


if __name__ == "__main__":
    ejecutar_cliente()
