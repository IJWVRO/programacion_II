import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

def rotar_imagen(img, opcion):
    if opcion=="izquierda":
        return np.rot90(img, 1)
    elif opcion=="derecha":
        return np.rot90(img, -1)
    elif opcion=="180":
        return np.rot90(img, 2)
    else:
        print("Opción no válida")
        return img

imagen=mpimg.imread("gato_negro_II.jpeg")

opcion=input("¿Querés rotar la imagen 90 grados a la izquierda, a la derecha o 180 grados? (izquierda/derecha/180): ").lower()

imagen_rotada=rotar_imagen(imagen, opcion)

plt.subplot(1, 2, 1)
plt.title("Imagen original")
plt.imshow(imagen)
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title(f"Imagen rotada {opcion}")
plt.imshow(imagen_rotada)
plt.axis("off")

plt.show()