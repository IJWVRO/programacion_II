import tkinter as tk
import random

num_adivinar = random.randint(1, 20)
intentos = 0
limite_intentos = 6

def comprobar():
    global intentos, num_adivinar

    try:
        num_usuario = int(entry.get())
    except ValueError:
        resultado.config(text="Ingresa un número válido.")
        return

    intentos += 1

    if num_usuario == num_adivinar:
        resultado.config(text=f"¡Adivinaste! El número era {num_adivinar}")
        boton.config(state="disabled")
    elif intentos >= limite_intentos:
        resultado.config(text=f"Te quedaste sin intentos. El número era {num_adivinar}")
        boton.config(state="disabled")
    else:
        if num_usuario < num_adivinar:
            pista = "El número es más grande."
        else:
            pista = "El número es más pequeño."
        resultado.config(text=f"No es correcto. {pista}\nIntentos: {intentos}/{limite_intentos}")

    entry.delete(0, tk.END)

def reiniciar():
    global num_adivinar, intentos
    num_adivinar = random.randint(1, 20)
    intentos = 0
    resultado.config(text="")
    boton.config(state="normal")
    entry.delete(0, tk.END)

# Interfaz
app = tk.Tk()
app.geometry("500x300")
app.configure(background="black")
app.title("Adivinar un Número")

titulo = tk.Label(app, text="Adivina el número (1 al 20)", font=("Courier", 16), bg="black", fg="orange")  # 👈 Color naranja
titulo.pack(pady=10)

entry = tk.Entry(app, font=("Courier", 14))
entry.pack(pady=10)

boton = tk.Button(app, text="Comprobar", font=("Courier", 14), command=comprobar, bg="#00FF00")
boton.pack(pady=10)

resultado = tk.Label(app, text="", font=("Courier", 14), bg="black", fg="white")
resultado.pack(pady=10)

reiniciar_btn = tk.Button(app, text="Reiniciar", font=("Courier", 12), command=reiniciar, bg="#DAF106")
reiniciar_btn.pack(pady=10)

app.mainloop()



