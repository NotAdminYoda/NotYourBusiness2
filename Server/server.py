from socket import socket
from threading import Thread
from hashlib import sha256
from time import time, sleep
import os
from datetime import datetime


numeroClientesProcesados = 0
comprobacionesHash = {}
estadisticasTransmision = {}


class ThreadCliente(Thread):
    def __init__(self, id, socket, direccionCliente, numeroConexiones, nombreArchivo, bytesArchivo, hashArchivo):
        Thread.__init__(self)
        self.id = id
        self.socket = socket
        self.direccionCliente = direccionCliente
        self.numeroConexiones = numeroConexiones
        self.nombreArchivo = nombreArchivo
        self.hashCode = None
        self.startEnvio = None
        self.bytesArchivo = bytesArchivo
        self.hashArchivo = hashArchivo
        print(
            f"Cliente creado con id {id}, ip {direccionCliente[0]} y puerto {direccionCliente[1]}")

    def run(self):
        global numeroClientesProcesados, comprobacionesHash, estadisticasTransmision
        self.socket.recv(1024).decode()
        numeroClientesProcesados += 1
        while numeroClientesProcesados < self.numeroConexiones:
            sleep(0.1)
        self.socket.send(str(self.id).encode())
        self.socket.send(str(self.numeroConexiones).encode())
        self.socket.send(nArchivo.encode())
        self.socket.send(self.hashArchivo)
        self.startEnvio = time()

        # Achivo en bytes
        self.socket.send(self.bytesArchivo)
        self.socket.send('ArchivoEnviado'.encode())
        estadisticasTransmision[self.id] = time() - self.startEnvio
        answerHash = bool(self.socket.recv(1024).decode())
        if answerHash:
            comprobacionesHash[self.id] = "Enviado Correctamente :D"
        else:
            comprobacionesHash[self.id] = "Error en la transferencia D:"
        self.socket.close()
        print(f"Enviado Correctamente al Cliente {self.id} con IP {self.direccionCliente[0]} y puerto {self.direccionCliente[1]}")


print("------- Programa Servidor TCP -------\n")
print("Recuerda ejecutar el comando 'truncate -s 100M 100MB.test'")
print("Recuerda ejecutar el comando 'truncate -s 250M 250MB.test'")
nArchivo = ""
while True:
    print("Presione 1 para el archivo de 100MB o 2 para el archivo de 250MB")
    entrada = input()
    if entrada.isnumeric():
        if entrada == '1':
            nArchivo = 'ArchivosAEnviar/100MB.test'
            break
        elif entrada == '2':
            nArchivo = 'ArchivosAEnviar/250MB.test'
            break
        else:
            print("Seleccione una opcion valida. Recuerde ejecutar el comando \n $'truncate -s 100M 100MB.test' o \n $'truncate -s 250M 250MB.test' para que funcione.")
    else:
        print("Seleccione una opcion valida")

print("Archivo seleccionado correctamente.")
file = open(nArchivo, "rb")
bytesArchivo = file.read()
file.close()
print("Archivo cargado correctamente.")

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

hashCode = sha256()
hashCode.update(bytesArchivo)
hashBytes = hashCode.digest()

for i in range(numeroDeClientes):
    socketCliente, direccionCliente = s.accept()
    print(
        f"Conexion del cliente con ip {direccionCliente[0]} y puerto {direccionCliente[1]}")
    t = ThreadCliente(i, socketCliente, direccionCliente,
                      numeroDeClientes, nArchivo, bytesArchivo, hashBytes)
    arregloClientes.append(t)
    arregloDirecciones.append(direccionCliente)

    if len(arregloClientes) == numeroDeClientes:
        for t in arregloClientes:
            t.start()

        for t in arregloClientes:
            t.join()

        # Log
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file = open("Logs/{}.txt".format(date), "w")
        tamanioArchivo = os.path.getsize(f"{nArchivo}")
        file.write(
            f"Archivo enviado: {nArchivo} - Tamanio en Bytes: {tamanioArchivo}")
        file.write(
            "Identificacion por conexión del cliente al que se realiza la transferencia de archivos:\n")
        for j in range(numeroDeClientes):
            file.write(f"Cliente {j}: {arregloDirecciones[j]}\n")
        file.write("\n")
        file.write("Resultados de la transferencia:\n")
        for j in range(numeroDeClientes):
            file.write(f"Cliente {j}: {comprobacionesHash[j]}\n")
        file.write("\n")

        file.write("Tiempos de transmision:\n")
        for j in range(numeroDeClientes):
            file.write(
                f"Cliente {j}: {str(round(estadisticasTransmision[j]), 3)} segundos\n")
        file.write("\n")
        file.close()
