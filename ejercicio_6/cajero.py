efectivo=0
resultado1=0
resultado2=0
resultado3=0
resultado4=0
resultado5=0
resultado6=0
resfinal=0
print("ingrese cunato de efectivo quiere retirar")
efectivo=int(input())
resultado1=efectivo//1000
resultado2=efectivo%1000
resultado3=resultado2//200
print("el podemos dar de billetes de $1000 en total ",resultado1)
print("le podemos dar de billetes de $200 en total ",resultado3)
resultado4=resultado1*1000
resultado5=resultado3*200
resultado6=resultado4+resultado5
resfinal=efectivo-resultado6


print("lo que no se puede retirar por que no hay billetes es",resfinal)
