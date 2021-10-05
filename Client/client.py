import socket
import hashlib
import traceback
import time
from threading import Thread
from datetime import datetime

# Parámetro para fijar dirección genérica en la configuración del socket. Es IP genérica pues no depende de otro servidor para responder.
TCP_IP = '0.0.0.0'
# Puerto TCP de escucha (recepción de peticiones) en el servidor.
TCP_PORT = 3000
BUFFER_SIZE = 4096  # tamaño del buffer de empaquetamiento en máquina.
SERVER_IP = input("Ingrese la dirección IP del servidor: ")
SERVER_PORT = 8000
BLOCK_SIZE = 4096
DOWNLOADS_PATH = "ArchivosRecibidos/"

log_info = []
file_dict = dict()


def hash(filename):
    # Create the hash object, can use something other than `.sha256()` if you wish
    file_hash = hashlib.sha256()
    with open(filename, 'rb') as f:  # Open the file to read it's bytes
        # Read from the file. Take in the amount declared above
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:  # While there is still data being read from the file
            file_hash.update(fb)  # Update the hash
            fb = f.read(BLOCK_SIZE)  # Read the next block from the file
    f.close()
    hash_val = file_hash.hexdigest()
    return hash_val


class ServerThread(Thread):
    def __init__(self, id, sock):
        Thread.__init__(self)
        self.id = id
        self.sock = sock
        self.port = TCP_PORT+self.id

    def run(self):
        try:
            conn_info = dict()
            self.sock.bind((TCP_IP, self.port))
            self.sock.connect((SERVER_IP, SERVER_PORT))
            print(
                f"Conexión establecida con el servidor {(TCP_IP, SERVER_PORT)}. Cliente {self.id} listo para recibir")

            data = self.sock.recv(BUFFER_SIZE)
            if len(data) > 0:
                info = data.decode().split("###")
                hash_val = info[1]
                archivo = info[3].split("/")[2]
                tamano = int(info[5])

                file_dict["name"] = archivo
                file_dict["size"] = tamano

                file = open(
                    f"{DOWNLOADS_PATH}Cliente{self.id}-Prueba-{num_clientes}_{archivo}", 'wb')
                recibidos = 0
                start_time = time.time()
                while recibidos < tamano:
                    descarga = self.sock.recv(BUFFER_SIZE)

                    file.write(descarga)
                    recibidos += len(descarga)
                finish_time = time.time()
                file.close()

                new_hash = hash(
                    f"{DOWNLOADS_PATH}Cliente{self.id}-Prueba-{num_clientes}_{archivo}")
                if(new_hash == hash_val):
                    print(
                        f"Descarga del cliente {self.id} finalizada con éxito. Valores hash coinciden")
                    self.sock.send("HASH###OK".encode())
                    conn_info["Transfer status"] = "Success - HASH matches"
                else:
                    print(
                        f"Descarga del cliente {self.id} finalizada sin éxito. Valores hash no coinciden")
                    self.sock.send("HASH###NOT_OK".encode())
                    conn_info["Transfer status"] = "Error - HASH does not match"

                # Recoleccion de info para el log

                conn_info["Client ID"] = self.id
                conn_info["Client IP"] = TCP_IP
                conn_info["Client PORT"] = self.port
                conn_info["Transfer time"] = "%s miliseconds" % (
                    (finish_time - start_time)*1000)

                log_info.append(conn_info)
            else:
                raise Exception(
                    "No se recibió la primera información desde el servidor")

        except:
            traceback.print_exc()

        finally:
            self.sock.close()


# Inicio del programa
num_clientes = int(
    input("Ingrese el número de conexiones que desea realizar con el servidor: "))

threads = []
for i in range(num_clientes):
    mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection = ServerThread(i, mysock)
    connection.start()
    threads.append(connection)

for t in threads:
    t.join()

# Creación del log
fecha = datetime.now()
log_name = f"{fecha.year}-{fecha.month}-{fecha.day}-{fecha.hour}-{fecha.minute}-{fecha.second}-log.txt"

file_log = open(f"Logs/{log_name}", "w")

file_log.write(f"LOG {fecha}\n\n")
file_log.write(f"SERVER IP: {SERVER_IP}\n")
file_log.write(f"SERVER PORT: {SERVER_PORT}\n")
file_log.write(f"Archivo recibido: {file_dict['name']}\n")
file_log.write(f"Tamaño archivo: {file_dict['size']} bytes\n")
file_log.write(f"Número de conexiones: {len(log_info)}\n\n")
file_log.write(f"Información de conexiones: \n")

for data in log_info:
    elements = list(data.items())
    elements.sort()
    for (key, val) in elements:
        file_log.write(f"\t{key}: {val}\n")
    file_log.write(f"\n")

file_log.close()
