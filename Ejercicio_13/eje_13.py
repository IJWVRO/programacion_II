import numpy as np

matriz=np.arange(1, 17).reshape(4, 4)
diag_principal=np.diag(matriz)
contra_diag=np.diag(np.fliplr(matriz))

suma_principal=np.sum(diag_principal)
mult_principal=np.prod(diag_principal)

suma_contra=np.sum(contra_diag)
mult_contra=np.prod(contra_diag)

print("Matriz:")
print(matriz)
print("\nDiagonal principal:", diag_principal)
print("Suma diagonal principal:", suma_principal)
print("Multiplicación diagonal principal:", mult_principal)

print("\nContra diagonal:", contra_diag)
print("Suma contra diagonal:", suma_contra)
print("Multiplicación contra diagonal:", mult_contra)
