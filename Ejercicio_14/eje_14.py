import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

imagen=Image.open("gato_negro.jpg")

matriz=np.array(imagen)

plt.imshow(matriz,cmap="gray")
plt.title("Imagen original en escala de grises")
plt.axis("off")
plt.show()

matriz_volteada=np.fliplr(matriz)
plt.imshow(matriz_volteada,cmap="gray")
plt.title("Imagen volteada horizontalmente")
plt.axis("off")
plt.show()