def cifrado_cesar(mensaje, desplazamiento):
    resultado = ""
    for caracter in mensaje:
        if caracter.isalpha():
            base=ord('A') if caracter.isupper() else ord('a')
            nueva_pos=(ord(caracter)-base+desplazamiento) % 26
            resultado+=chr(base+nueva_pos)
        else:
            resultado+=caracter
    return resultado

mensaje = input("Ingrese el mensaje: ")
desplazamiento=int(input("Ingrese el desplazamiento (positivo para cifrar, negativo para descifrar): "))
resultado = cifrado_cesar(mensaje, desplazamiento)
print("Resultado:", resultado)
