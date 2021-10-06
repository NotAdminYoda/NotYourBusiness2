from genericpath import getsize
from socket import socket
from threading import Thread
from hashlib import sha256
from time import time
from datetime import datetime
from os import path
BUFFER_SIZE = 1024


class ThreadServidor(Thread):
    def __init__(self, id, socket):
        Thread.__init__(self)
        self.id = id
        self.socket = socket
        self.numeroConexiones = ""
        self.nArchivo = ""
        self.hashCalculado = ""
        self.hashServidor = ""
        self.startTime = None
        self.tiempoTotal = None

    def run(self):
        self.socket.send("ImReadyServer".encode())
        self.id = self.socket.recv(BUFFER_SIZE).decode()
        self.numeroConexiones = self.socket.recv(BUFFER_SIZE).decode()
        self.nArchivo = self.socket.recv(BUFFER_SIZE).decode()
        self.hashServidor = self.socket.recv(BUFFER_SIZE)
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file1 = open(
            f"ArchivosRecibidos/{date}-Cliente{self.id}-Prueba-{self.numeroConexiones}.txt", "wb")
        print(f"Recibiendo archivo de Cliente {self.id}...")
        self.startTime = time()
        response = self.socket.recv(BUFFER_SIZE*64)
        while True:
            if 'ArchivoEnviado\'' not in str(response):
                file1.write(response)
                response = self.socket.recv(BUFFER_SIZE*64)
            else:
                break

        file1.write(response[:-14])
        file1.close()
        self.tiempoTotal = time() - self.startTime
        print(
            f"Transmision y Escritura del archivo {self.nArchivo} Completada para el cliente {self.id}")
        hashCode = sha256()
        file2 = open(
            f"ArchivosRecibidos/{date}-Cliente{self.id}-Prueba-{self.numeroConexiones}.txt", "rb")
        hashCode.update(file2.read())
        file2.close()
        self.hashCalculado = hashCode.digest()
        mensajeComprobacionHash = "La integridad del archivo es correcta" if self.hashCalculado == self.hashServidor else "La integridad del archivo no es correcta"
        print(f"Hash Calculado {self.hashCalculado.hex()}")
        print(f"Hash Recibido {self.hashServidor.hex()}")
        if mensajeComprobacionHash == "La integridad del archivo es correcta":
            print(
                f"El archivo {self.nArchivo} del cliente {self.id} tiene comprobacion de integridad correcta.")
        else:
            print(
                f"El archivo {self.nArchivo} del cliente {self.id} tiene comprobacion de integridad incorrecta.")

        self.socket.send(mensajeComprobacionHash.encode())
        file3 = open(f"Logs/{date} Cliente{self.id}.txt", "w")
        file3.write(f"Archivo Recibido: {self.nArchivo.split('/')[1]}\n")
        tamanioArchivo = path.getsize(
            f"ArchivosRecibidos/{date}-Cliente{self.id}-Prueba-{self.numeroConexiones}.txt")
        file3.write(f"Tamanio archivo recibido: {tamanioArchivo} bytes\n")
        file3.write(f"Servidor con ip {host} y puerto {port}\n")
        file3.write(f"Integridad del archivo: {mensajeComprobacionHash}\n")
        file3.write(f"Tiempo de transmision: {self.tiempoTotal} segundos\n")
        file3.close()
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
    thread = ThreadServidor(i, sckt)
    arregloClientes.append(thread)
for thread in arregloClientes:
    thread.start()
for thread in arregloClientes:
    thread.join()
