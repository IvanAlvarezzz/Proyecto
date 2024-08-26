from tkinter import *
import os
import cv2
from matplotlib import pyplot
from mtcnn.mtcnn import MTCNN
import numpy as np
from cryptography.fernet import Fernet
import base64

# Directorio donde se guardarán los usuarios
USUARIOS_DIR = "Usuarios"

# Crear la carpeta "Usuarios" si no existe
if not os.path.exists(USUARIOS_DIR):
    os.makedirs(USUARIOS_DIR)

# Generar una clave y guardarla en un archivo si no existe
if not os.path.exists("secret.key"):
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
else:
    with open("secret.key", "rb") as key_file:
        key = key_file.read()

cipher_suite = Fernet(key)

def encrypt_password(password):
    return cipher_suite.encrypt(password.encode())

def decrypt_password(encrypted_password):
    return cipher_suite.decrypt(encrypted_password).decode()

def registrar_usuario():
    usuario_info = usuario.get()
    contra_info = contra.get()

    contra_info_encrypted = encrypt_password(contra_info)

    usuario_file = os.path.join(USUARIOS_DIR, usuario_info)
    with open(usuario_file, "wb") as archivo:
        archivo.write(usuario_info.encode() + b"\n")
        archivo.write(contra_info_encrypted)

    usuario_entrada.delete(0, END)
    contra_entrada.delete(0, END)

    Label(pantalla1, text="Registro Convencional Exitoso", fg="green", font=("Calibri", 11)).pack()

def registro_facial():
    cap = cv2.VideoCapture(0)
    while(True):
        ret, frame = cap.read()
        cv2.imshow('Registro Facial', frame)
        if cv2.waitKey(1) == 27:
            break
    usuario_img = usuario.get()
    cv2.imwrite(usuario_img + ".jpg", frame)
    cap.release()
    cv2.destroyAllWindows()

    usuario_entrada.delete(0, END)
    contra_entrada.delete(0, END)
    Label(pantalla1, text="Registro Facial Exitoso", fg="green", font=("Calibri", 11)).pack()

    def reg_rostro(img, lista_resultados):
        data = pyplot.imread(img)
        for i in range(len(lista_resultados)):
            x1, y1, ancho, alto = lista_resultados[i]['box']
            x2, y2 = x1 + ancho, y1 + alto
            pyplot.subplot(1, len(lista_resultados), i + 1)
            pyplot.axis('off')
            cara_reg = data[y1:y2, x1:x2]
            cara_reg = cv2.resize(cara_reg, (150, 200), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(usuario_img + ".jpg", cara_reg)
            return pyplot.imshow(data[y1:y2, x1:x2])
        pyplot.show()

    img = usuario_img + ".jpg"
    pixeles = pyplot.imread(img)
    detector = MTCNN()
    caras = detector.detect_faces(pixeles)
    reg_rostro(img, caras)

def registro():
    global usuario
    global contra
    global usuario_entrada
    global contra_entrada
    global pantalla1

    pantalla1 = Toplevel(pantalla)
    pantalla1.title("Registro")
    pantalla1.geometry("720x360")

    usuario = StringVar()
    contra = StringVar()

    Label(pantalla1, text="Registro facial: debe de asignar un usuario:").pack()
    Label(pantalla1, text="Registro tradicional: debe asignar usuario y contraseña:").pack()
    Label(pantalla1, text="").pack()
    Label(pantalla1, text="Usuario * ").pack()

    usuario_entrada = Entry(pantalla1, textvariable=usuario, width=40)
    usuario_entrada.pack()

    Label(pantalla1, text="Contraseña * ").pack()

    contra_entrada = Entry(pantalla1, textvariable=contra, width=40)
    contra_entrada.pack()

    Label(pantalla1, text="").pack()

    Button(pantalla1, text="Registro Tradicional", width=30, height=2, command=registrar_usuario).pack()
    Label(pantalla1, text="").pack()
    Button(pantalla1, text="Registro Facial", width=30, height=2, command=registro_facial).pack()

def verificacion_login():
    for widget in pantalla2.winfo_children():
        if isinstance(widget, Label) and widget.cget("text") in ["Inicio de Sesion Exitoso", "Contraseña Incorrecta", "Usuario no encontrado"]:
            widget.destroy()
    log_usuario = verificacion_usuario.get()
    log_contra = verificacion_contra.get()

    usuario_entrada2.delete(0, END)
    contra_entrada2.delete(0, END)

    usuario_file = os.path.join(USUARIOS_DIR, log_usuario)
    if os.path.exists(usuario_file):
        with open(usuario_file, "rb") as archivo2:
            verificacion = archivo2.read().splitlines()
            stored_password_encrypted = verificacion[1]
            stored_password = decrypt_password(stored_password_encrypted)

        if log_contra == stored_password:
            print("Inicio de sesion exitoso")
            Label(pantalla2, text="Inicio de Sesion Exitoso", fg="green", font=("Calibri", 11)).pack()
        else:
            print("Contraseña incorrecta, ingrese de nuevo")
            Label(pantalla2, text="Contraseña Incorrecta", fg="red", font=("Calibri", 11)).pack()
    else:
        print("Usuario no encontrado")
        Label(pantalla2, text="Usuario no encontrado", fg="red", font=("Calibri", 11)).pack()
    
def login_facial():
    cap = cv2.VideoCapture(0)
    while(True):
        ret, frame = cap.read()
        cv2.imshow('Login Facial', frame)
        if cv2.waitKey(1) == 27:
            break
    usuario_login = verificacion_usuario.get()
    cv2.imwrite(usuario_login + "LOG.jpg", frame)
    cap.release()
    cv2.destroyAllWindows()

    usuario_entrada2.delete(0, END)
    contra_entrada2.delete(0, END)

    def log_rostro(img, lista_resultados):
        data = pyplot.imread(img)
        for i in range(len(lista_resultados)):
            x1, y1, ancho, alto = lista_resultados[i]['box']
            x2, y2 = x1 + ancho, y1 + alto
            pyplot.subplot(1, len(lista_resultados), i + 1)
            pyplot.axis('off')
            cara_reg = data[y1:y2, x1:x2]
            cara_reg = cv2.resize(cara_reg, (150, 200), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(usuario_login + "LOG.jpg", cara_reg)
            return pyplot.imshow(data[y1:y2, x1:x2])
        pyplot.show()

    img = usuario_login + "LOG.jpg"
    pixeles = pyplot.imread(img)
    detector = MTCNN()
    caras = detector.detect_faces(pixeles)
    log_rostro(img, caras)

    def orb_sim(img1, img2):
        orb = cv2.ORB_create()

        kpa, descr_a = orb.detectAndCompute(img1, None)
        kpb, descr_b = orb.detectAndCompute(img2, None)

        comp = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        matches = comp.match(descr_a, descr_b)

        regiones_similares = [i for i in matches if i.distance < 70]
        if len(matches) == 0:
            return 0
        return len(regiones_similares) / len(matches)

    im_archivos = os.listdir()
    if usuario_login + ".jpg" in im_archivos:
        rostro_reg = cv2.imread(usuario_login + ".jpg", 0)
        rostro_log = cv2.imread(usuario_login + "LOG.jpg", 0)
        similitud = orb_sim(rostro_reg, rostro_log)
        if similitud >= 0.98:
            Label(pantalla2, text="Inicio de Sesion Exitoso", fg="green", font=("Calibri", 11)).pack()
            print("Bienvenido al sistema usuario: ", usuario_login)
            print("Compatibilidad con la foto del registro: ", similitud)
        else:
            print("Rostro incorrecto, Verifique su usuario")
            print("Compatibilidad con la foto del registro: ", similitud)
            Label(pantalla2, text="Incompatibilidad de rostros", fg="red", font=("Calibri", 11)).pack()
    else:
        print("Usuario no encontrado")
        Label(pantalla2, text="Usuario no encontrado", fg="red", font=("Calibri", 11)).pack()

def login():
    global pantalla2
    global verificacion_usuario
    global verificacion_contra
    global usuario_entrada2
    global contra_entrada2

    pantalla2 = Toplevel(pantalla)
    pantalla2.title("Login")
    pantalla2.geometry("720x450")
    Label(pantalla2, text="Login facial: debe de asignar un usuario:").pack(pady=10)
    Label(pantalla2, text="Login tradicional: debe asignar usuario y contraseña:").pack(pady=10)
    Label(pantalla2, text="").pack()

    verificacion_usuario = StringVar()
    verificacion_contra = StringVar()

    Label(pantalla2, text="Usuario * ").pack(pady=5)
    usuario_entrada2 = Entry(pantalla2, textvariable=verificacion_usuario, width=40, font=('Helvetica', 14))
    usuario_entrada2.pack(pady=5)

    Label(pantalla2, text="Contraseña * ").pack(pady=5)
    contra_entrada2 = Entry(pantalla2, textvariable=verificacion_contra, show='*', width=40, font=('Helvetica', 14))
    contra_entrada2.pack(pady=5)

    Label(pantalla2, text="").pack(pady=5)
    Button(pantalla2, text="Inicio de Sesion Tradicional", width=30, height=2, command=verificacion_login).pack(pady=5)
    Label(pantalla2, text="").pack(pady=5)
    Button(pantalla2, text="Inicio de Sesion Facial", width=30, height=2, command=login_facial).pack(pady=5)

def pantalla_principal():
    global pantalla
    pantalla = Tk()
    pantalla.geometry("800x400")
    pantalla.title("Servicio Biometrico")
    
    pantalla.configure(bg="#121212")

    header_frame = Frame(pantalla, bg="#1F1F1F")
    header_frame.pack(fill='x')

    Label(
        header_frame,
        text="PPtino Software", 
        bg="#1F1F1F", 
        fg="#FFFFFF",
        width="300", 
        height="2", 
        font=("Verdana", 16)
    ).pack(pady=10)

    Label(pantalla, text="", bg="#121212").pack()

    Button(
        pantalla,
        text="Iniciar Sesion", 
        height="2", 
        width="40", 
        command=login,
        bg="#3A3A3A",
        fg="#FFFFFF",
        highlightbackground="#3A3A3A",
        highlightcolor="#3A3A3A",
        bd=0,
        activebackground="#5A5A5A",
        activeforeground="#FFFFFF"
    ).pack(pady=10)

    Label(pantalla, text="", bg="#121212").pack()

    Button(
        pantalla,
        text="Registro", 
        height="2", 
        width="40", 
        command=registro,
        bg="#3A3A3A",
        fg="#FFFFFF",
        highlightbackground="#3A3A3A",
        highlightcolor="#3A3A3A",
        bd=0,
        activebackground="#5A5A5A",
        activeforeground="#FFFFFF"
    ).pack(pady=10)

    pantalla.mainloop()

pantalla_principal()
