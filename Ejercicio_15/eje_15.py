from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

def rgb_to_grayscale(img_array):
    R=img_array[:, :, 0]
    G=img_array[:, :, 1]
    B=img_array[:, :, 2]
    gray=R*0.2989 + G*0.5870 + B*0.1140
    gray=gray.astype(np.uint8)
    return gray

imagen_color=Image.open("gato_negro_II.jpeg")
img_array=np.array(imagen_color)

plt.subplot(1, 2, 1)
plt.title("Imagen a color")
plt.imshow(img_array)

imagen_gris=rgb_to_grayscale(img_array)

plt.subplot(1, 2, 2)
plt.title("Escala de grises")
plt.imshow(imagen_gris, cmap="gray")

plt.show()