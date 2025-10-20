import random
estudiantes=["Ignacio","Tomas","Lionel","Alan","Santi","Antonela","Angela","Joaquin","Javier","Jeremias"]

nombres_alatorios=random.sample(estudiantes,len(estudiantes))

print("la orden de la expocicion")

for i,estudiante in enumerate(nombres_alatorios,start=1):
    print(f"{i}.{estudiante}")
