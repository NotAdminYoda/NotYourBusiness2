import copy
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from hashlib import sha256
from time import time, sleep
import os
from datetime import datetime

diccionarioComprobacionesHashArchivos = {}
estadisticasTransmision = {}
BUFFER_SIZE = 4096
MAX_BUFFER_SIZE = 64000
entregados = 0


class ThreadCliente(Thread):
    def __init__(self, id, direccionCliente, nombreArchivo, bytesArchivo, hashArchivo, tamanioArchivo):
        Thread.__init__(self)
        self.id = id
        self.direccionCliente = direccionCliente
        self.nombreArchivo = nombreArchivo
        self.hashCode = hashArchivo
        self.startEnvio = None
        self.bytesArchivo = bytesArchivo
        self.tamanioArchivo = tamanioArchivo
        print(
            f"Cliente creado con id {id}, ip {direccionCliente[0]} y puerto {direccionCliente[1]}")

    def run(self):
        global diccionarioComprobacionesHashArchivos, estadisticasTransmision, socketServerUDP, entregados
        socketServerUDP.sendto(str(self.id).encode(), self.direccionCliente)
        socketServerUDP.sendto(
            self.nombreArchivo.encode(), self.direccionCliente)
        socketServerUDP.sendto(
            str(self.tamanioArchivo).encode(), self.direccionCliente)
        socketServerUDP.sendto(self.hashCode, self.direccionCliente)
        self.startEnvio = time()
        cent = True
        start = 0
        finish = MAX_BUFFER_SIZE
        while cent:
            socketServerUDP.sendto(
                self.bytesArchivo[start:finish], self.direccionCliente)
            start += MAX_BUFFER_SIZE
            finish += MAX_BUFFER_SIZE
            if bytesArchivo[start:finish] == ''.encode():
                cent = False
            sleep(0.001)
        socketServerUDP.sendto("ArchivoEnviado".encode(),
                               self.direccionCliente)
        resultado, adrsClient = socketServerUDP.recvfrom(BUFFER_SIZE)
        estadisticasTransmision[self.id] = time() - self.startEnvio
        print(adrsClient, self.direccionCliente)
        resultado = resultado.decode()
        diccionarioComprobacionesHashArchivos[self.id] = resultado
        if resultado == "La integridad del archivo es correcta":
            entregados += 1
        print(
            f"Finalizacion envio de archivo al Cliente {self.id} con IP {self.direccionCliente[0]} y puerto {self.direccionCliente[1]}")


print("\n\n------- Programa Servidor UDP -------\n")
print("Recuerda ejecutar el comando 'truncate -s 100M 100MB.txt' en la carpeta /ArchivosAEnviar")
print("Recuerda ejecutar el comando 'truncate -s 250M 250MB.txt' en la carpeta /ArchivosAEnviar")
print("\nRecuerda ejecutar el comando ifconfig para conocer la IP del servidor.")
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
tamanioArchivo = os.path.getsize(f"{nArchivo}")
hashArchivo = sha256()
hashArchivo.update(bytesArchivo)
hashBytes = hashArchivo.digest()
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
socketServerUDP = socket(AF_INET, SOCK_DGRAM)
host = '0.0.0.0'
port = 8000
socketServerUDP.bind((host, port))
print(
    f"Servidor corriendo en el puerto {port} (Recuerde encontar la IP usando el comando ifconfig\n")


arregloClientes = []
arregloDirecciones = []

for i in range(numeroDeClientes):
    mensajeCliente, direccionCliente = socketServerUDP.recvfrom(
        BUFFER_SIZE)  # mensaje de Recibido, tupla con 0 la ip y 1 el puerto
    print(mensajeCliente, i)
    print(
        f"Conexion del cliente con ip {direccionCliente[0]} y puerto {direccionCliente[1]}")
    t = ThreadCliente(i, direccionCliente, nArchivo, copy.copy(
        bytesArchivo), hashBytes, tamanioArchivo)
    arregloClientes.append(t)
    arregloDirecciones.append(direccionCliente)

    if len(arregloClientes) == numeroDeClientes:
        for x in arregloClientes:
            x.start()

        for x in arregloClientes:
            x.join()

        # Log
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file = open(f"Logs/{date}.txt", "w")
        file.write(
            f"Archivo enviado: {nArchivo} - Tamanio en Bytes: {tamanioArchivo}")
        file.write(
            "\nIdentificacion por conexión del cliente al que se realiza la transferencia de archivos:\n")
        for j in range(numeroDeClientes):
            file.write(
                f"Cliente {j} con IP {arregloDirecciones[j][0]} y puerto {arregloDirecciones[j][1]}\n")
        file.write("\n")

        file.write("\nTiempos de transmision:\n")
        for j in range(numeroDeClientes):
            file.write(
                f"Cliente {j}: {estadisticasTransmision[j]} segundos\n")
        file.write("\n")

        file.write("Resultados de la transferencia:\n")
        for j in range(numeroDeClientes):
            file.write(
                f"Cliente {j}: {diccionarioComprobacionesHashArchivos[j]}\n")
        file.write("\n")
        file.write(f"Correctos: {entregados} de {numeroDeClientes}\n")

        file.close()
        socketServerUDP.close()
