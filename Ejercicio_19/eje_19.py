import tkinter as tk

def cifrado_cesar(mensaje, desplazamiento):
    resultado = ""
    for caracter in mensaje:
        if caracter.isalpha():
            base = ord('A') if caracter.isupper() else ord('a')
            nueva_pos = (ord(caracter) - base + desplazamiento) % 26
            resultado += chr(base + nueva_pos)
        else:
            resultado += caracter
    return resultado

def cifrar():
    mensaje = entrada_mensaje.get()
    try:
        desplazamiento = int(entrada_desplazamiento.get())
    except ValueError:
        resultado_label.config(text="Desplazamiento invalido", fg="#ff0000")
        return

    resultado = cifrado_cesar(mensaje, desplazamiento)
    resultado_label.config(text=f"Resultado: {resultado}", fg="cyan")

def reiniciar():
    entrada_mensaje.delete(0, tk.END)
    entrada_desplazamiento.delete(0, tk.END)
    resultado_label.config(text="Resultado:", fg="cyan")

# ventana
app = tk.Tk()
app.geometry("550x350")
app.configure(background="black")
app.title("Cifrado Cesar")

fuente_texto = ("Arial", 16)
fuente_boton = ("Arial", 14, "bold")

# las etiquetas y los botones
tk.Label(app, text="Ingrese el mensaje:", bg="black", fg="#ff8800", font=fuente_texto).pack(pady=5)
entrada_mensaje = tk.Entry(app, width=40, font=fuente_texto)
entrada_mensaje.pack(pady=5)

tk.Label(app, text="Ingrese el desplazamiento:", bg="black", fg="white", font=fuente_texto).pack(pady=5)
entrada_desplazamiento = tk.Entry(app, width=10, font=fuente_texto)
entrada_desplazamiento.pack(pady=5)

# botones
tk.Button(app, text="Cifrar/Descifrar", command=cifrar, bg="gray", fg="white", font=fuente_boton).pack(pady=10)
tk.Button(app, text="Reiniciar", command=reiniciar, bg="red", fg="white", font=fuente_boton).pack(pady=5)

# resultado
resultado_label = tk.Label(app, text="Resultado:", bg="black", fg="cyan", font=("Arial", 16, "bold"))
resultado_label.pack(pady=22)

app.mainloop()