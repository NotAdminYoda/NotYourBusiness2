from socket import socket
from threading import Thread
from hashlib import sha256
from time import time
from datetime import datetime
import os
BUFFER_SIZE = 1024


class ThreadServidor(Thread):
    def __init__(self, id, socket, ready):
        self.id = id
        self.socket = socket
        self.ready = ready
        self.numeroConexiones = ""
        self.nArchivo = ""
        self.hashCalculado = ""
        self.hashServidor = ""
        self.startTime = None
        self.tiempoTotal = None

    def run(self):
        while not self.ready:
            self.ready = input(
                "Ingrese cualquier caracter cuando este listo para recibir: ")
        self.socket.send("ImReadyServer".encode())
        self.id = self.socket.recv(BUFFER_SIZE).decode()
        self.numeroConexiones = self.socket.recv(BUFFER_SIZE).decode()
        self.nArchivo = self.socket.recv(BUFFER_SIZE).decode()
        self.hashServidor = self.socket.recv(BUFFER_SIZE)
        file = open(
            f"ArchivosRecibidos/Cliente{self.id}-Prueba-{self.numeroConexiones}.txt", "wb")
        print(f"Recibiendo archivo de Cliente {self.id}...")
        self.startTime = time()
        response = ""
        while True:
            chunk = self.socket.recv(BUFFER_SIZE*128)
            if len(chunk) == 0 or "ArchivoEnviado" in response:
                break
            else:
                response += chunk
        response = response.replace("ArchivoEnviado\\", '')
        self.tiempoTotal = time() - self.startTime
        file.write(response)
        print(f"Transmision y Escritura del archivo {self.nArchivo} Completa")
        file.close()
        hashCode = sha256()
        file = open(
            f"ArchivosRecibidos/Cliente{self.id}-Prueba-{self.numeroConexiones}.txt", "rb")
        hashCode.update(file.read())
        file.close()
        mensajeComprobacionHash = "La integridad del archivo es correcta" if hashCode.digest(
        ) == self.hashServidor else "La integridad del archivo no es correcta"
        print(f"Hash Calculado {self.hashCalculado.hexdigest()}")
        print(f"Hash Recibido {self.hashServidor.hex()}")
        if mensajeComprobacionHash == "La integridad del archivo es correcta":
            print(
                f"El archivo {self.nArchivo} del cliente {self.id} tiene comprobacion de integridad correcta.")
        else:
            print(
                f"El archivo {self.nArchivo} del cliente {self.id} tiene comprobacion de integridad incorrecta.")

        self.socket.send(mensajeComprobacionHash.encode())

        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file = open(f"Logs/{date} Cliente{self.id}.txt", "w")
        file.write(f"Archivo Recibido: {self.nArchivo.split('/')[1]}\n")
        tamanioArchivo = os.path.getsize(f"ArchivosRecibidos/Cliente{self.id}-Prueba{self.numeroConexiones}.txt")
        file.write(f"Tamanio archivo recibido: {tamanioArchivo} bytes\n")
        file.write(f"Servidor con ip {host} y puerto {port}\n")
        file.write(f"Integridad del archivo: {mensajeComprobacionHash}\n")
        file.write(f"Tiempo de transmision: {self.tiempoTotal} segundos\n")
        file.close()
        self.socket.close()


print("\n\n----- Programa Cliente Servidor TCP -----\n\n")
numeroDeClientes = ""
while True:
    numeroDeClientes = input("Numero de clientes (Threads): ")
    if numeroDeClientes.isnumeric():
        numeroDeClientes = int(numeroDeClientes)
        if numeroDeClientes <= 0 or numeroDeClientes > 25:
            print("Seleccione una opción valida")
        else:
            break
    else:
        print("Seleccione una opción valida")
#host = input("Ingres IP del Servidor TCP: ")
host = '192.168.10.20'
port = 8000
arregloClientes = []
for i in range(numeroDeClientes):
    sckt = socket()
    sckt.connect((host, port))
    print(
        f"Conexion del cliente {i} al servidor con ip {host} y puerto {port}")
    thread = ThreadServidor(i, sckt, '1')
    arregloClientes.append(thread)
for thread in arregloClientes:
    thread.start()
for thread in arregloClientes:
    thread.join()
