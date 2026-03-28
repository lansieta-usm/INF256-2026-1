import socket

IP_UDP = "127.0.0.1"
PUERTO_UDP = 6500

def start_log_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP_UDP, PUERTO_UDP))
    
    print(f"----- Este es el Servidor UDP de logs corriendo en puerto {PUERTO_UDP} -----")
    print()
    print("Logs recibidos a continuación:")
    while True:
        data, addr = sock.recvfrom(1024)
        print(data.decode('utf-8'))

if __name__ == "__main__":
    start_log_server()
