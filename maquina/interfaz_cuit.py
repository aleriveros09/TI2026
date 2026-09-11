import tkinter as tk
from tkinter import ttk, messagebox


# -----------------------------------------------------------------------------
# LÓGICA DE VALIDACIÓN (MÓDULO 11)
# -----------------------------------------------------------------------------
def validar_cuit_cuil(cuit_input: str) -> dict:
    """
    Aplica el algoritmo de Módulo 11 para validar un CUIT/CUIL de 11 dígitos.
    Soporta entradas con o sin guiones/espacios.
    """
    # Sanitización: extraer solo caracteres numéricos
    solo_numeros = "".join(c for c in cuit_input if c.isdigit())

    if len(solo_numeros) != 11:
        return {
            "valido": False,
            "digito_esperado": None,
            "digito_ingresado": None,
            "mensaje": f"Longitud incorrecta ({len(solo_numeros)} dígitos). Debe tener 11 dígitos.",
            "detalle_calculo": ""
        }

    primeros_10 = [int(d) for d in solo_numeros[:10]]
    digito_ingresado = int(solo_numeros[10])
    pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    # 1. Suma Ponderada
    productos = [d * p for d, p in zip(primeros_10, pesos)]
    suma_total = sum(productos)

    # 2. Módulo 11
    resto = suma_total % 11

    # 3. Determinación del dígito de control esperable
    if resto == 0:
        digito_esperado = 0
    elif resto == 1:
        # En la normativa AFIP/ANSES, un resto 1 fuerza a reasignar el prefijo
        digito_esperado = -1  # Invalidador directo sin cambio de prefijo
    else:
        digito_esperado = 11 - resto

    es_valido = (digito_ingresado == digito_esperado)

    # Generación del informe técnico detallado
    detalle = (
        f"CÁLCULO DEL DÍGITO DE CONTROL (MÓDULO 11)\n"
        f"-----------------------------------------\n"
        f"Cadena ingresada:  {solo_numeros[:2]}-{solo_numeros[2:10]}-{solo_numeros[10]}\n"
        f"Primeros 10 dítigos: {primeros_10}\n"
        f"Pesos de serie:     {pesos}\n"
        f"Productos:          {productos}\n"
        f"Suma Ponderada (S): {suma_total}\n"
        f"Resto (S % 11):     {resto}\n"
        f"Dígito Esperado:    {digito_esperado if digito_esperado != -1 else 'Caso Especial (Invalidador)'}\n"
        f"Dígito Ingresado:   {digito_ingresado}\n"
    )

    if es_valido:
        msg = f"✓ CUIT/CUIL VÁLIDO. El dígito verificador {digito_ingresado} es correcto."
    else:
        msg = f"✗ CUIT/CUIL INVÁLIDO. Se esperaba {digito_esperado} pero se ingresó {digito_ingresado}."

    return {
        "valido": es_valido,
        "digito_esperado": digito_esperado,
        "digito_ingresado": digito_ingresado,
        "mensaje": msg,
        "detalle_calculo": detalle
    }


# -----------------------------------------------------------------------------
# INTERFAZ GRÁFICA TKINTER
# -----------------------------------------------------------------------------
class AppValidadorCUIT(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Validador CUIT/CUIL - Checksum Módulo 11")
        self.geometry("650x520")

        self._crear_componentes()

    def _crear_componentes(self):
        # Frame de Entrada
        frame_input = ttk.LabelFrame(self, text=" Entrada de Datos ", padding=15)
        frame_input.pack(fill=tk.X, padx=15, pady=10)

        ttk.Label(frame_input, text="Número de CUIT/CUIL (11 dígitos):").pack(side=tk.LEFT, padx=5)

        self.entry_cuit = ttk.Entry(frame_input, font=("Consolas", 11), width=22)
        self.entry_cuit.pack(side=tk.LEFT, padx=5)
        self.entry_cuit.insert(0, "20-32986417-8")

        btn_validar = ttk.Button(frame_input, text="Validar CUIT", command=self._ejecutar_validacion)
        btn_validar.pack(side=tk.LEFT, padx=10)

        # Estado/Resultado destacado
        self.lbl_resultado = ttk.Label(
            self, text="Ingrese un CUIT para verificar.", font=("Segoe UI", 11, "bold")
        )
        self.lbl_resultado.pack(pady=5)

        # Panel de Informe / Desglose del Algoritmo
        frame_reporte = ttk.LabelFrame(self, text=" Desglose Algorítmico Módulo 11 ", padding=10)
        frame_reporte.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.txt_reporte = tk.Text(frame_reporte, font=("Consolas", 9), wrap=tk.WORD)
        self.txt_reporte.pack(fill=tk.BOTH, expand=True)

    def _ejecutar_validacion(self):
        entrada = self.entry_cuit.get()
        res = validar_cuit_cuil(entrada)

        if res["valido"]:
            self.lbl_resultado.config(text=res["mensaje"], foreground="green")
        else:
            self.lbl_resultado.config(text=res["mensaje"], foreground="red")

        self.txt_reporte.delete("1.0", tk.END)
        self.txt_reporte.insert(tk.END, res["detalle_calculo"])


if __name__ == "__main__":
    app = AppValidadorCUIT()
    app.mainloop()
