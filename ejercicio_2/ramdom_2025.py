import random
numusuario=0
numadivinar=0

numadivinar=random.randint(1,20)
while(numusuario != numadivinar):
    print("ingrese un numero")
    numusuario=int(input())
print("adivinaste el numero es ",numadivinar)
    
