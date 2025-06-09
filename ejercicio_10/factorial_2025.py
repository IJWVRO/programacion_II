def factorial_del_numero(num):
    if num < 0:
        return("no hay numeros negativos")
    resultado=1

    for i in range(1,num+1):
        resultado*=i
        return resultado

num=int(input("Ingrese el numero "))
print("el numero ",num, "factorisado es ",resultado)
        



