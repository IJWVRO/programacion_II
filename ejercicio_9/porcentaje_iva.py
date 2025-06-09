def calcular_total_factura(importe_sin_iva, porcentaje_iva=21):
    return importe_sin_iva * (1 + porcentaje_iva / 100)

def aplicar_descuento(importe_con_iva, porcentaje_descuento):
    return importe_con_iva * (1 - porcentaje_descuento / 100)


importe = float(input("Introduce el importe del producto (sin IVA): "))

usar_iva_personalizado = input("¿Quieres ingresar un porcentaje de IVA personalizado? (s/n): ")
if usar_iva_personalizado.lower() == 's':
    iva = float(input("Introduce el porcentaje de IVA: "))
    total_con_iva = calcular_total_factura(importe, iva)
else:
    total_con_iva = calcular_total_factura(importe) 

descuento = float(input("Introduce el porcentaje de descuento: "))
precio_final = aplicar_descuento(total_con_iva, descuento)

print("Importe sin IVA:", importe)
print("Total con IVA:", round(total_con_iva, 2))
print("Precio final con descuento:", round(precio_final,2))
