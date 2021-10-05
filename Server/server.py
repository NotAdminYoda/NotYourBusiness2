import socket
import hashlib
import os
import time
import traceback
from threading import Thread
from datetime import datetime

# Parámetro para fijar dirección genérica en la configuración del socket.
TCP_IP = '0.0.0.0'
# Puerto TCP de escucha (recepción de peticiones) en el servidor.
TCP_PORT = 8000
BUFFER_SIZE = 4096  # tamaño del buffer de empaquetamiento en máquina.

log_info = []

# Clase que establece hilos de conexión con los clientes que envíen petición de enlace.


class ClientThread(Thread):

    def __init__(self, id, ip, port, sock, filename):
        Thread.__init__(self)
        self.id = id
        self.ip = ip
        self.port = port
        self.sock = sock
        self.filename = filename
        # Confirmación de conexión con cada cliente.
        print(
            f"Nueva conexión desde{(ip,port)}. Cliente {id} listo para recibir.")

    # Función run realiza el envío del mensaje solicitado de manera persistente utilizando el socket y el hilo abierto previamente.
    def run(self):
        try:
            filesize = os.path.getsize(filename)
            self.sock.sendall(
                f'HASH###{hash_val}###FILE###{filename}###SIZE###{filesize}'.encode())
            time.sleep(1)
            # Algoritmo de lectura y envío.
            with open(filename, "rb") as f:
                start_time = time.time()
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    self.sock.send(bytes_read)
                finish_time = time.time()

            hash_stat = None
            data = self.sock.recv(BUFFER_SIZE)
            if len(data) > 0:
                info = data.decode().split("###")
                if info[0] == "HASH":
                    hash_stat = info[1]
                self.sock.close()
            else:
                raise Exception(
                    "No se recibió la confirmación del hash del cliente:", self.id)

            # Recoleccion de info para el log
            conn_info = dict()
            conn_info["Client ID"] = self.id
            conn_info["Client IP"] = self.ip
            conn_info["Client PORT"] = self.port
            conn_info["Transfer status"] = "Success" if hash_stat == "OK" else "Error"
            conn_info["Transfer time"] = "%s miliseconds" % (
                (finish_time - start_time)*1000)

            log_info.append(conn_info)
        except:
            traceback.print_exc()
            self.sock.close()


# Inicio del programa

# Selección de archivo
print("Los archivos disponibles son:\n1. 100 MB\n2. 250 MB\n")
seleccion_arch = int(input("Ingrese el número del archivo que desea enviar: "))
filename = "ArchivosAEnviar/"
if(seleccion_arch == 1):
    filename += "100MB.test"
elif (seleccion_arch == 2):
    filename += "250MB.test"

# Calculo del hash del archivo
BLOCK_SIZE = 4096
file_hash = hashlib.sha256()
with open(filename, 'rb') as f:
    # Read from the file. Take in the amount declared above
    fb = f.read(BLOCK_SIZE)
    while len(fb) > 0:
        file_hash.update(fb)
        fb = f.read(BLOCK_SIZE)
f.close()
hash_val = file_hash.hexdigest()

# Selección num de clientes
num_clientes = int(input("Ingrese el número de clientes a conectar: "))

# Creación del socket
tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((TCP_IP, TCP_PORT))
threads = []

tcpsock.listen(5)
print("Servidor escuchando en el puerto", TCP_PORT)

id = 0
while len(threads) < num_clientes:
    try:
        (conn, (ip, port)) = tcpsock.accept()
        newthread = ClientThread(id, ip, port, conn, filename)
        threads.append(newthread)
        id += 1
    except:
        # tcpsock.shutdown(socket.SHUT_RD)
        tcpsock.close()
        print("Socket cerrado")
        break

for t in threads:
    t.start()
    t.join()


# Creación del log
fecha = datetime.now()
filesize = os.path.getsize(filename)
log_name = f"{fecha.year}-{fecha.month}-{fecha.day}-{fecha.hour}-{fecha.minute}-{fecha.second}-log.txt"

file_log = open(f"Logs/{log_name}", "x")

file_log.write(f"LOG {fecha}\n\n")
file_log.write(f"Archivo enviado: {filename.split('/')[2]}\n")
file_log.write(f"Tamaño archivo: {filesize} bytes\n")
file_log.write(f"Número de conexiones: {len(log_info)}\n\n")
file_log.write(f"Información de conexiones: \n")

for data in log_info:
    elements = list(data.items())
    elements.sort()
    for (key, val) in elements:
        file_log.write(f"\t{key}: {val}\n")
    file_log.write(f"\n")

file_log.close()
