import math

def area_circulo(radio):
    return math.pi*radio**2

radio = float(input("Ingrese el valor del radio: "))
area = area_circulo(radio)
print("El área es", area)
