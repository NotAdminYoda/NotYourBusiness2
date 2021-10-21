from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from hashlib import sha256
from time import time
from datetime import datetime
from os import path
BUFFER_SIZE = 4096
MAX_BUFFER_SIZE = 64000


class ThreadServidor(Thread):
    def __init__(self, id, socket, address, nConexiones):
        Thread.__init__(self)
        self.id = id
        self.socket = socket
        self.numeroConexiones = nConexiones
        self.tamanioArchivoServidor = None
        self.nArchivo = ""
        self.hashCalculado = ""
        self.hashServidor = ""
        self.startTime = None
        self.tiempoTotal = None
        self.address = address

    def run(self):
        self.socket.sendto("ImReadyServer".encode(), self.address)
        self.id, addressServer = self.socket.recvfrom(BUFFER_SIZE)
        self.id = self.id.decode()
        self.nArchivo, addressServer = self.socket.recvfrom(BUFFER_SIZE)
        self.nArchivo = self.nArchivo.decode()
        self.nArchivo = self.nArchivo.split('/')[1]
        self.tamanioArchivoServidor, addressServer = self.socket.recvfrom(
            BUFFER_SIZE)
        self.tamanioArchivoServidor = self.tamanioArchivoServidor.decode()
        self.hashServidor, addressServer = self.socket.recvfrom(BUFFER_SIZE)
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        fileName = f"ArchivosRecibidos/{date}-Cliente{self.id}-Prueba-{self.numeroConexiones}.txt"
        file1 = open(fileName, "wb")
        print(f"Recibiendo archivo del Cliente {self.id}...")
        self.startTime = time()
        response, addressServer = self.socket.recvfrom(MAX_BUFFER_SIZE)
        cent = True
        self.socket.settimeout(10)
        while cent:
            if 'ArchivoEnviado\'' not in str(response):
                file1.write(response)
                try:
                    response, addressServer = self.socket.recvfrom(
                        MAX_BUFFER_SIZE)
                except:
                    cent = False
            else:
                cent = False
        self.tiempoTotal = time() - self.startTime
        file1.write(response[:-14])
        file1.close()
        print(
            f"Transmision y Escritura del archivo {self.nArchivo} Completada para el cliente {self.id}")
        hashCode = sha256()
        file2 = open(
            f"ArchivosRecibidos/{date}-Cliente{self.id}-Prueba-{self.numeroConexiones}.txt", "rb")
        hashCode.update(file2.read())
        file2.close()
        self.hashCalculado = hashCode.digest()
        tamanioArchivo = path.getsize(
            f"ArchivosRecibidos/{date}-Cliente{self.id}-Prueba-{self.numeroConexiones}.txt")
        print(
            f"Tamaño archivo original: {self.tamanioArchivoServidor} Tamaño archivo recibido: {path.getsize(fileName)}")
        mensajeComprobacionHash = "La integridad del archivo es correcta" if self.hashCalculado == self.hashServidor and str(
            tamanioArchivo) == self.tamanioArchivoServidor else "La integridad del archivo no es correcta"
        print(f"Hash Calculado {self.hashCalculado.hex()}")
        print(f"Hash Recibido {self.hashServidor.hex()}")
        if mensajeComprobacionHash == "La integridad del archivo es correcta":
            mensajeFinal = f"El archivo {self.nArchivo} del cliente {self.id} tiene comprobacion de integridad correcta:\n\tHash Recibido: {self.hashServidor.hex()}\n\tHash Calculado: {self.hashCalculado.hex()}\n\tTamaño archivo original: {self.tamanioArchivoServidor}\n\tTamaño archivo recibido: {tamanioArchivo}\n"
        else:
            mensajeFinal = f"El archivo {self.nArchivo} del cliente {self.id} tiene comprobacion de integridad incorrecta.:\n\tHash Recibido: {self.hashServidor.hex()}\n\tHash Calculado: {self.hashCalculado.hex()}\n\tTamaño archivo original: {self.tamanioArchivoServidor}\n\tTamaño archivo recibido: {tamanioArchivo}\n"

        self.socket.sendto(mensajeComprobacionHash.encode(), self.address)
        file3 = open(f"Logs/{date} Cliente{self.id}.txt", "w")
        file3.write(f"Archivo Recibido: {self.nArchivo}\n")

        file3.write(f"Tamanio archivo recibido: {tamanioArchivo} bytes\n")
        file3.write(f"Servidor con ip {host} y puerto {port}\n")
        file3.write(f"Integridad del archivo:\n{mensajeFinal}")
        file3.write(f"Tiempo de transmision: {self.tiempoTotal} segundos\n")
        file3.close()
        self.socket.close()


print("\n\n----- Programa Cliente UDP -----\n\n")
numeroDeClientes = ""
while True:
    numeroDeClientes = input("Numero de clientes (Threads): ")
    if numeroDeClientes.isnumeric():
        numeroDeClientes = int(numeroDeClientes)
        if numeroDeClientes <= 0 or numeroDeClientes > 25:
            print("Seleccione entre 1 y 25 clientes concurrentes.")
        else:
            break
    else:
        print("Seleccione una opción valida")

while True:
    host = input(
        "Ingrese la IP del Servidor UDP (Recuerde usar el comando ifconfig para conocer la IP): ")
    if len(host.strip().split(".")) == 4:
        break
    else:
        print("Seleccione una opción valida.")
# host = '192.168.10.24'
port = 8000
arregloClientes = []
for i in range(numeroDeClientes):
    sckt = socket(AF_INET, SOCK_DGRAM)
    print(
        f"Conexion del cliente {i} al servidor con ip {host} y puerto {port}")
    thread = ThreadServidor(i, sckt, (host, port), numeroDeClientes)
    arregloClientes.append(thread)
for thread in arregloClientes:
    thread.start()
for thread in arregloClientes:
    thread.join()
