import socket

# Definimos direccion y puerto donde vamos a escuchar. La direccion 127.0.0.1 es la direccion de la propia computadora.
IP_UDP = "127.0.0.1"
PUERTO_UDP = 6500

def start_log_server():
    # Creamos el Socket.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Usamos bind para "Adueñarnos de este puerto"
    sock.bind((IP_UDP, PUERTO_UDP))
    
    print(f"----- Este es el Servidor UDP de logs corriendo en puerto {PUERTO_UDP} -----")
    print()
    print("Logs recibidos a continuación:")
    # Abrimos el archivo "chat.log" en modo append para poder ir guardando los mensajes
    with open("chat.log", "a", encoding="utf-8") as f:
        while True:
            # Esperamos el mensaje
            # El recvfrom nos da los datos y la direccion (IP y Puerto). Recibimos los datos del que envió.
            data, addr = sock.recvfrom(1024)

            # Los datos viajan como bytes. Los decodificamos a texto.
            mensaje = data.decode("utf-8")

            # Creamos la linea para apendarlo al chat.log y lo mostramos por pantalla.
            linea_log = f"Desde {addr}: {mensaje}"
            print(linea_log)

            # Lo guardamos en el archivo
            f.write(linea_log + "\n")

            # Usamos flush para que se escriba de una en el disco 
            f.flush()


if __name__ == "__main__":
    start_log_server()
