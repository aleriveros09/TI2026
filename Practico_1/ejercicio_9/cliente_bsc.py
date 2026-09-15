# cliente_bsc.py
#
# Cliente TCP para Simulación y Análisis Teórico de un Canal Binario Simétrico (BSC).
# Implementa enmarcado de mensajes con encabezados de 4 bytes (longitud), batería
# de pruebas empíricas para estimar BER, transmisión de texto y análisis teórico de información.

import math  # Módulo para funciones matemáticas (log2, etc.)
import random  # Módulo para generación de secuencias de bits sintéticas aleatorias
import socket  # Módulo para la comunicación por red mediante sockets TCP
import struct  # Módulo para empaquetar/desempaquetar encabezados binarios en formato Big-Endian


# =====================================================================
# CONFIGURACIÓN DE CONEXIÓN RED
# =====================================================================
HOST = "127.0.0.1"  # Dirección IP del servidor BSC (Localhost)
PUERTO = 5555  # Puerto TCP en el que escucha el servidor BSC


# =====================================================================
# FUNCIONES DE PROTOCOLO TCP (ENMARCADO DE MENSAJES DE LONGITUD FIJA)
# =====================================================================
def recibir_exactamente(sock, cantidad):
    """
    Garantiza la lectura exacta de N bytes de la red TCP.
    Dado que TCP es un flujo de bytes continuo sin límites de mensaje,
    se itera iterativamente hasta completar el buffer de la longitud solicitada.
    """
    datos = bytearray()  # Arreglo mutable para acumular los bytes recibidos
    while len(datos) < cantidad:  # Continuar hasta reunir exactamente 'cantidad' bytes
        bloque = sock.recv(cantidad - len(datos))  # Leer el remanente disponible en el socket
        if not bloque:  # Si el socket devuelve un bloque vacío, la conexión se interrumpió
            raise ConnectionError("La conexión fue cerrada por el servidor.")  # Lanzar excepción
        datos.extend(bloque)  # Anexar los bytes recién leídos al acumulador
    return bytes(datos)  # Retornar el buffer completo convertido a bytes inmutables


def recibir_mensaje(sock):
    """
    Desempaqueta y recibe un mensaje del servidor siguiendo el protocolo:
    1. Lee 4 bytes de encabezado que indican la longitud M del mensaje (Entero de 32 bits sin signo).
    2. Lee exactamente M bytes correspondientes al cuerpo del mensaje.
    """
    encabezado = recibir_exactamente(sock, 4)  # Leer exactamente los 4 bytes del encabezado
    longitud = struct.unpack("!I", encabezado)[0]  # Desempaquetar el entero de 32 bits en Big-Endian (!I)
    datos = recibir_exactamente(sock, longitud)  # Leer la cantidad exacta de bytes declarada
    return datos.decode("ascii")  # Decodificar el flujo de bytes ASCII a una cadena binaria de caracteres '0' y '1'


def enviar_mensaje(sock, mensaje):
    """
    Empaqueta y envía un mensaje al servidor respetando el protocolo de red:
    1. Codifica la cadena de caracteres '0' y '1' a bytes ASCII.
    2. Antepone un encabezado de 4 bytes con la longitud total del payload.
    """
    datos = mensaje.encode("ascii")  # Convertir la cadena de texto '0'/'1' a formato de bytes ASCII
    encabezado = struct.pack("!I", len(datos))  # Crear el encabezado de 4 bytes Big-Endian (!I) con la longitud
    sock.sendall(encabezado + datos)  # Enviar en un único paquete completo el encabezado concatenado con los datos


# =====================================================================
# FUNCIONES AUXILIARES DE CONVERSIÓN Y PROCESAMIENTO
# =====================================================================
def texto_a_binario(texto):
    """
    Convierte una cadena de texto arbitraria a su representación binaria de 8 bits por carácter.
    Ejemplo: 'A' -> ASCII 65 -> '01000001'
    """
    cadena_binaria = []  # Lista temporal para acumular los bloques binarios de cada carácter
    for caracter in texto:  # Iterar carácter por carácter de la frase ingresada
        codigo_ascii = ord(caracter)  # Obtener el código numérico ASCII del carácter
        binario_8bits = format(codigo_ascii, '08b')  # Convertir el entero a una cadena binaria de 8 bits con ceros a la izquierda
        cadena_binaria.append(binario_8bits)  # Agregar la secuencia de 8 bits a la lista
    return "".join(cadena_binaria)  # Unir y retornar todos los bloques en una sola cadena de bits continua


def binario_a_texto(cadena_binaria):
    """
    Convierte una cadena de bits continua (múltiplo de 8) de regreso a su representación de texto ASCII.
    Si la longitud no es múltiplo de 8, descarta los bits sobrantes del final.
    """
    caracteres = []  # Lista temporal para reconstruir el texto
    longitud_valida = (len(cadena_binaria) // 8) * 8  # Determinar la longitud divisible por 8 bits más cercana
    for i in range(0, longitud_valida, 8):  # Avanzar en bloques de 8 en 8 bits
        bloque_8bits = cadena_binaria[i:i + 8]  # Extraer el bloque de 8 bits actual
        codigo_ascii = int(bloque_8bits, 2)  # Convertir la cadena binaria base 2 a un número entero
        caracteres.append(chr(codigo_ascii))  # Convertir el entero ASCII a su símbolo ASCII correspondiente
    return "".join(caracteres)  # Unir la lista de caracteres en una frase de texto final


def calcular_entropia_shannon(probabilidades):
    """
    Calcula la Entropía de Shannon H(X) = - sum(p_i * log2(p_i)) bits/símbolo.
    Ignora valores de probabilidad igual a cero para evitar excepciones matematicas con log2(0).
    """
    entropia = 0.0  # Acumulador para el valor de la entropía
    for p in probabilidades:  # Iterar sobre cada probabilidad de la distribución
        if p > 0.0:  # Evaluar únicamente probabilidades mayores a cero
            entropia -= p * math.log2(p)  # Sumar el término -p_i * log2(p_i)
    return entropia  # Retornar la entropía final calculada


# =====================================================================
# PIPELINE PRINCIPAL DE EJECUCIÓN (CLIENTE)
# =====================================================================
def ejecutar_cliente():
    # 1. Establecer la conexión por socket TCP con el servidor BSC
    print("Conectando al servidor BSC en {}:{}...".format(HOST, PUERTO))
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Instanciar socket IPv4 (AF_INET) y TCP (SOCK_STREAM)
    cliente.connect((HOST, PUERTO))  # Iniciar el handshake de conexión TCP con la dirección y puerto destino
    print("[+] Conexión establecida exitosamente con el servidor.\n")

    try:
        # =================================================================
        # FASE 1: TRANSMISIÓN Y TASA DE ERROR EMPÍRICA (BER)
        # =================================================================
        print("=" * 65)
        print(" FASE 1: TRANSMISIÓN Y ESTIMACIÓN EMPÍRICA DE LA TASA DE ERROR (BER)")
        print("=" * 65)

        # Definir magnitudes de las tramas para evaluar la convergencia estadística
        magnitudes = [100, 10000, 1000000]  # Tamaños de prueba: 100 bits, 10k bits y 1M bits
        ber_estimado = 0.0  # Variable para almacenar el BER derivado de la prueba con la muestra más grande

        for N in magnitudes:  # Iterar sobre cada tamaño de prueba
            # Generar trama sintética aleatoria equiprobable de 'N' bits ('0' o '1')
            trama_original = "".join(random.choice("01") for _ in range(N))

            # Transmitir la trama al servidor a través del socket TCP
            enviar_mensaje(cliente, trama_original)

            # Recibir la trama de salida distorsionada por el ruido del canal BSC
            trama_recibida = recibir_mensaje(cliente)

            # Comparar bit a bit la trama enviada con la recibida para contar la cantidad de errores
            errores = sum(1 for tx, rx in zip(trama_original, trama_recibida) if tx != rx)

            # Calcular el BER empírico (Relación de bits erróneos sobre el total de bits transmitidos)
            ber = errores / N

            # Guardar la estimación de la muestra más grande (1M) como el valor más preciso
            if N == max(magnitudes):
                ber_estimado = ber

            # Imprimir resultados del experimento
            print("  • Trama de {:>9,d} bits | Errores detectados: {:>7,d} | BER Empírico: {:.6f}".format(N, errores, ber))

        print("\n--> Observación Ley de los Grandes Números:")
        print("    A medida que la cantidad de bits N aumenta, la variabilidad de la frecuencia")
        print("    relativa disminuye y el BER empírico converge a la probabilidad de error real 'p'.")

        # Visualización práctica del efecto del ruido sobre un mensaje de texto real
        print("\n" + "-" * 65)
        print(" DEMOSTRACIÓN VISUAL DEL RUIDO SOBRE TEXTO")
        print("-" * 65)
        frase_original = "Teoria de la Informacion 2026 - Universidad"  # Frase de prueba
        binario_frase = texto_a_binario(frase_original)  # Convertir texto a binario

        enviar_mensaje(cliente, binario_frase)  # Transmitir trama del texto al canal
        binario_ruidoso = recibir_mensaje(cliente)  # Recibir trama alterada por el canal
        frase_ruidosa = binario_a_texto(binario_ruidoso)  # Reconstruir texto a partir del binario ruidoso

        print("  • Frase Original:  \"{}\"".format(frase_original))
        print("  • Texto Ruidoso:   \"{}\"".format(frase_ruidosa))

        # =================================================================
        # FASE 2: MODELADO MATEMÁTICO Y CAPACIDAD DEL CANAL
        # =================================================================
        print("\n" + "=" * 65)
        print(" FASE 2: MODELADO MATEMÁTICO Y CAPACIDAD DEL CANAL (BSC)")
        print("=" * 65)

        # Utilizar el p_estimado (BER empírico obtenido en la muestra de 1.000.000 bits)
        p = ber_estimado

        # 1. Matriz de Transición del Canal P(Y|X)
        # En un BSC: P(Y=0|X=0) = 1-p, P(Y=1|X=0) = p, P(Y=0|X=1) = p, P(Y=1|X=1) = 1-p
        P_Y_dado_X = [
            [1 - p, p],  # Fila X=0: [P(Y=0|X=0), P(Y=1|X=0)]
            [p, 1 - p]   # Fila X=1: [P(Y=0|X=1), P(Y=1|X=1)]
        ]

        print("1. Matriz del Canal P(Y|X) [Transición de Probabilidades]:")
        print("   ┌                   ┐")
        print("   │  {:0.6f}   {:0.6f}  │  (Fila X=0)".format(P_Y_dado_X[0][0], P_Y_dado_X[0][1]))
        print("   │  {:0.6f}   {:0.6f}  │  (Fila X=1)".format(P_Y_dado_X[1][0], P_Y_dado_X[1][1]))
        print("   └                   ┘")

        # 2. Probabilidades de la Fuente P(X) a partir de la trama binaria del texto enviado
        cant_ceros = binario_frase.count('0')  # Contar ceros en el mensaje binario de texto
        cant_unos = binario_frase.count('1')  # Contar unos en el mensaje binario de texto
        total_bits_texto = len(binario_frase)  # Total de bits del mensaje

        P_X0 = cant_ceros / total_bits_texto  # Probabilidad de entrada P(X=0)
        P_X1 = cant_unos / total_bits_texto  # Probabilidad de entrada P(X=1)

        print("\n2. Probabilidades de la Fuente P(X) (Mensaje de texto enviado):")
        print("   • P(X=0) = {:.6f} (Ceros: {}/{})".format(P_X0, cant_ceros, total_bits_texto))
        print("   • P(X=1) = {:.6f} (Unos:  {}/{})".format(P_X1, cant_unos, total_bits_texto))

        # 3. Cálculo de la Información Mutua I(X;Y)
        # Paso A: Obtener P(Y) usando Teorema de la Probabilidad Total: P(Y_j) = sum_i P(X_i) * P(Y_j | X_i)
        P_Y0 = (P_X0 * P_Y_dado_X[0][0]) + (P_X1 * P_Y_dado_X[1][0])  # P(Y=0)
        P_Y1 = (P_X0 * P_Y_dado_X[0][1]) + (P_X1 * P_Y_dado_X[1][1])  # P(Y=1)

        # Paso B: Entropía de Salida H(Y)
        H_Y = calcular_entropia_shannon([P_Y0, P_Y1])

        # Paso C: Entropía Condicional (Ruido del Canal) H(Y|X)
        # Para un BSC, H(Y|X=0) = H(Y|X=1) = H(p) = -p*log2(p) - (1-p)*log2(1-p)
        H_p = calcular_entropia_shannon([p, 1 - p])  # Entropía del vector de ruido [p, 1-p]
        H_Y_dado_X = (P_X0 * H_p) + (P_X1 * H_p)  # Dado que P_X0 + P_X1 = 1, H(Y|X) = H(p)

        # Paso D: Información Mutua I(X;Y) = H(Y) - H(Y|X)
        I_XY = H_Y - H_Y_dado_X

        print("\n3. Información Mutua de la Transmisión Específica:")
        print("   • Entropía de Salida H(Y)   = {:.6f} bits/símbolo".format(H_Y))
        print("   • Ruido del Canal H(Y|X)   = {:.6f} bits/símbolo".format(H_Y_dado_X))
        print("   • Información Mutua I(X;Y) = {:.6f} bits/símbolo".format(I_XY))

        # 4. Capacidad del Canal C = 1 - H(p)
        Capacidad = 1.0 - H_p

        print("\n4. Capacidad del Canal BSC (Máximo teórico C):")
        print("   • C = 1 - H(p) = {:.6f} bits/símbolo".format(Capacidad))

        # 5. Análisis de Maximización y Comparación
        porcentaje_alcance = (I_XY / Capacidad) * 100.0 if Capacidad > 0 else 0.0

        print("\n5. Análisis de Maximización:")
        print("   • Relación I(X;Y) / C = {:.2f}%".format(porcentaje_alcance))

        # =================================================================
        # RESPUESTA TEÓRICA EN COMENTARIOS (CUESTIONARIO FASE 2.5)
        # =================================================================
        """
        ===================================================================================
        ANÁLISIS TEÓRICO: ¿Logró su mensaje maximizar la capacidad del canal?
        ===================================================================================
        RESPUESTA:
        No necesariamente (o solo parcialmente). La información mutua obtenida I(X;Y) será 
        estrictamente igual a la Capacidad del Canal C únicamente si la fuente de entrada 
        transmite símbolos de forma EQUIPROBABLE, es decir: P(X=0) = 0.5 y P(X=1) = 0.5.

        En la prueba de la frase de texto ASCII, los caracteres en texto natural no tienen 
        una distribución uniforme de ceros y unos en binario (por ejemplo, los caracteres 
        imprimibles ASCII estándar habitualmente comienzan con los bits '010...'), lo que 
        genera una distribución P(X=0) != P(X=1) (desbalanceada).

        CARACTERÍSTICAS QUE DEBERÍA TENER LA TRAMA DE BITS ENVIADA PARA QUE I(X;Y) == C:
        1. Equiprobabilidad de la Fuente: La trama transmitida debe cumplir P(X=0) = P(X=1) = 0.5.
           Esto maximiza la entropía de salida H(Y) a su límite superior absoluto de 1 bit.
        2. Independencia Estadística: Los bits de la secuencia transmitida deben ser 
           estadísticamente independientes entre sí (fuente sin memoria / nula redundancia).
        3. Compresión / Cifrado Previo: En la práctica, aplicar algoritmos de compresión 
           (como Huffman o LZW) o cifrado al mensaje previo a su envío por el canal remueve 
           la redundancia del lenguaje, logrando que el flujo binario resultante tenga una 
           distribución casi perfectamente uniforme (P(X=0) ~ 0.5), alcanzando así I(X;Y) = C.
        ===================================================================================
        """

        # Enviar comando de salida para desconectar limpiamente el socket del servidor
        enviar_mensaje(cliente, "SALIR")

    except Exception as e:
        print("\n[ERROR]: Ocurrió una anomalía durante la comunicación: {}".format(e))
    finally:
        cliente.close()  # Cerrar el socket TCP local
        print("\n[-] Socket del cliente cerrado.")


if __name__ == "__main__":
    ejecutar_cliente()