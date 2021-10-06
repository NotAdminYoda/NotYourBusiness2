import copy
from socket import socket
from threading import Thread
from hashlib import sha256
from time import time, sleep
import os
from datetime import datetime

diccionarioComprobacionesHashArchivos = {}
estadisticasTransmision = {}
BUFFER_SIZE = 4096


class ThreadCliente(Thread):
    def __init__(self, id, socket, direccionCliente, numeroConexiones, nombreArchivo, bytesArchivo, hashArchivo):
        Thread.__init__(self)
        self.id = id
        self.socket = socket
        self.direccionCliente = direccionCliente
        self.numeroConexiones = numeroConexiones
        self.nombreArchivo = nombreArchivo
        self.hashCode = hashArchivo
        self.startEnvio = None
        self.bytesArchivo = bytesArchivo
        print(
            f"Cliente creado con id {id}, ip {direccionCliente[0]} y puerto {direccionCliente[1]}")

    def run(self):
        global diccionarioComprobacionesHashArchivos, estadisticasTransmision
        self.socket.recv(BUFFER_SIZE).decode()
        self.socket.send(str(self.id).encode())
        sleep(0.1)
        self.socket.send(str(self.numeroConexiones).encode())
        sleep(0.1)
        self.socket.send(nArchivo.encode())
        sleep(0.1)
        self.socket.send(self.hashCode)
        sleep(0.1)
        self.startEnvio = time()
        # Achivo en bytes
        self.socket.send(self.bytesArchivo)
        sleep(0.1)
        self.socket.send('ArchivoEnviado'.encode())
        sleep(0.1)
        estadisticasTransmision[self.id] = time() - self.startEnvio
        diccionarioComprobacionesHashArchivos[self.id] = self.socket.recv(BUFFER_SIZE).decode()
        self.socket.close()
        print(
            f"Finalizacion envio de archivo al Cliente {self.id} con IP {self.direccionCliente[0]} y puerto {self.direccionCliente[1]}")


print("------- Programa Servidor TCP -------\n")
print("Recuerda ejecutar el comando 'truncate -s 100M 100MB.txt'")
print("Recuerda ejecutar el comando 'truncate -s 250M 250MB.txt'")
nArchivo = ""
while True:
    print("Presione 1 para el archivo de 100MB o 2 para el archivo de 250MB")
    entrada = input()
    if entrada.isnumeric():
        if entrada == '1':
            nArchivo = 'ArchivosAEnviar/100MB.txt'
            break
        elif entrada == '2':
            nArchivo = 'ArchivosAEnviar/250MB.txt'
            break
        else:
            print("Seleccione una opcion valida. Recuerde ejecutar el comando \n $'truncate -s 100M 100MB.txt' o \n $'truncate -s 250M 250MB.txt' para que funcione.")
    else:
        print("Seleccione una opcion valida")

print("Archivo seleccionado correctamente.")
file = open(nArchivo, "rb")
bytesArchivo = file.read()
file.close()
print("Archivo cargado correctamente.")

hashArchivo = sha256()
hashArchivo.update(bytesArchivo)
hashBytes = hashArchivo.digest()
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
s = socket()
host = '0.0.0.0'
port = 8000
s.bind((host, port))
s.listen(5)
print(
    f"Servidor corriendo en el puerto {port} (Recuerde encontar la IP usando el comando ifconfig\n")


arregloClientes = []
arregloDirecciones = []

for i in range(numeroDeClientes):
    socketCliente, direccionCliente = s.accept()
    print(
        f"Conexion del cliente con ip {direccionCliente[0]} y puerto {direccionCliente[1]}")
    t = ThreadCliente(i, socketCliente, direccionCliente,
                      numeroDeClientes, nArchivo, copy.copy(bytesArchivo), hashBytes)
    arregloClientes.append(t)
    arregloDirecciones.append(direccionCliente)

    if len(arregloClientes) == numeroDeClientes:
        for t in arregloClientes:
            t.start()

        for t in arregloClientes:
            t.join()

        # Log
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file = open(f"Logs/{date}.txt", "w")
        tamanioArchivo = os.path.getsize(f"{nArchivo}")
        file.write(
            f"Archivo enviado: {nArchivo} - Tamanio en Bytes: {tamanioArchivo}")
        file.write(
            "\nIdentificacion por conexión del cliente al que se realiza la transferencia de archivos:\n")
        for j in range(numeroDeClientes):
            file.write(f"Cliente {j} con IP {arregloDirecciones[j][0]} y puerto {arregloDirecciones[j][1]}\n")
        file.write("\n")
        file.write("Resultados de la transferencia:\n")
        for j in range(numeroDeClientes):
            file.write(f"Cliente {j}: {diccionarioComprobacionesHashArchivos[j]}\n")
        file.write("\n")

        file.write("Tiempos de transmision:\n")
        for j in range(numeroDeClientes):
            file.write(
                f"Cliente {j}: {estadisticasTransmision[j]} segundos\n")
        file.write("\n")
        file.close()
        s.close()
