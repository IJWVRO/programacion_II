from datetime import datetime
fechaA=input("Ingrese la fecha de nacimiento (la fecha es: año-mes-dia) : ")
fecha_de_nacimiento=datetime.strptime(fechaA,"%Y-%m-%d")
timestamp=int(fecha_de_nacimiento.timestamp())
print("la edad en formato epoch ",timestamp)
fechaB=input("ingrese la fecha actual (la fecha es: año-mes-dia) : ")
fecha_actual=datetime.strptime(fechaB,"%Y-%m-%d")
anios = fecha_actual.year - fecha_de_nacimiento.year
meses = fecha_actual.month - fecha_de_nacimiento.month
dias = fecha_actual.day - fecha_de_nacimiento.day

if dias < 0:
    meses -= 1
    mes_anterior = fecha_actual.month - 1 or 12
    anio_anterior = fecha_actual.year if fecha_actual.month != 1 else fecha_actual.year - 1
    dias += (datetime(anio_anterior, mes_anterior + 1, 1) - datetime(anio_anterior, mes_anterior, 1)).days

if meses < 0:
    anios -= 1
    meses += 12

print(f"B) Edad en años, meses y días: {anios} años, {meses} meses, {dias} días")
