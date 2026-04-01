import socket

# ----- CONFIGURACIÓN DE REDES ----- #
IP_UDP = "127.0.0.1"
PUERTO_UDP = 6500

def start_log_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP_UDP, PUERTO_UDP))
    
    print(f"----- Este es el Servidor UDP de logs corriendo en puerto {PUERTO_UDP} -----")
    print("NOTA: Los logs que acá se imprimirán son los mismos que se guardarán en 'chat.log' en el mismo directorio.")
    print()
    print("Logs recibidos a continuación:")
    with open("chat.log", "a", encoding="utf-8") as f:
        while True:
            data, addr = sock.recvfrom(1024)

            linea_log = data.decode("utf-8")

            print(linea_log) # El log se imprime por consola
            f.write(linea_log + "\n") # El mismo log se guarda en chat.log

            f.flush()

if __name__ == "__main__":
    start_log_server()
