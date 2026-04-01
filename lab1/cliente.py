import socket
import ssl
import sys
import threading

# 1. Configuración por defecto: modo local
DEFAULT_TCP_HOST = "127.0.0.1"
DEFAULT_TCP_PORT = 6000
DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_HTTP_PORT = 8080
DEFAULT_HTTP_SCHEME = "http"


def cargar_configuracion():
    tcp_host = DEFAULT_TCP_HOST
    tcp_port = DEFAULT_TCP_PORT
    http_host = DEFAULT_HTTP_HOST
    http_port = DEFAULT_HTTP_PORT
    http_scheme = DEFAULT_HTTP_SCHEME

    # Permite ejecutar:
    # python3 cliente.py
    # python3 cliente.py <tcp_host> <tcp_port>
    # python3 cliente.py <tcp_host> <tcp_port> <http_host> <http_port> [http|https]
    args = sys.argv[1:]

    if len(args) not in (0, 2, 4, 5):
        print("Uso:")
        print("  python3 cliente.py")
        print("  python3 cliente.py <tcp_host> <tcp_port>")
        print("  python3 cliente.py <tcp_host> <tcp_port> <http_host> <http_port> [http|https]")
        sys.exit(1)

    try:
        if len(args) >= 2:
            tcp_host = args[0]
            tcp_port = int(args[1])
            http_host = tcp_host
            http_port = 80
            http_scheme = "http"

        if len(args) >= 4:
            http_host = args[2]
            http_port = int(args[3])

        if len(args) == 5:
            http_scheme = args[4].lower()
            if http_scheme not in ("http", "https"):
                raise ValueError("El esquema HTTP debe ser 'http' o 'https'")
    except ValueError as e:
        print(f"[!] Configuración inválida: {e}")
        sys.exit(1)

    return {
        "tcp_host": tcp_host,
        "tcp_port": tcp_port,
        "http_host": http_host,
        "http_port": http_port,
        "http_scheme": http_scheme,
    }

def recibir_mensajes(sock):
    #  función que solo escucha 
    while True:
        try:
            # Recibimos bytes del servidor y los pasamos a texto
            data = sock.recv(1024).decode('utf-8')
            if data:
                # El '\n' es para que el mensaje nuevo aparezca en una línea limpia
                print(f"\n{data}\n ", end="")
            else:
                # Si no hay data, es que el servidor se cerró
                break
        except:
            print("\n[!] Error recibiendo mensajes.")
            break

def consulta_http_manual(config, ruta):
    # Función para pedir datos por HTTP.
    # Creamos un socket TCP nuevo solo para esta pregunta
    sock_http = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_http.connect((config["http_host"], config["http_port"]))

        if config["http_scheme"] == "https":
            contexto = ssl.create_default_context()
            sock_http = contexto.wrap_socket(sock_http, server_hostname=config["http_host"])

        # Construimos el mensaje HTTP
        peticion = (
            f"GET {ruta} HTTP/1.1\r\n"
            f"Host: {config['http_host']}\r\n"
            "Connection: close\r\n\r\n"
        )
        # Envia la peticion
        sock_http.sendall(peticion.encode('utf-8'))

        # Leemos la respuesta completa hasta que el servidor cierre la conexion
        fragmentos = []
        while True:
            data = sock_http.recv(4096)
            if not data:
                break
            fragmentos.append(data)

        respuesta = b"".join(fragmentos).decode('utf-8', errors='replace')
        print(f"\n--- RESPUESTA DEL SERVIDOR ({ruta}) ---\n{respuesta}")

    except Exception as e:
        print(f"[!] No se pudo conectar a la API: {e}")

    # Para no gastar recursos 
    finally:
        sock_http.close()

def iniciar_cliente():
    config = cargar_configuracion()

    # Creamos el socket principal para el chat. 
    sock_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock_chat.connect((config["tcp_host"], config["tcp_port"]))
        
        # Lo primero que enviamos es el NICK
        nick = input("Bienvenido. Ingresa tu Nickname: ")
        sock_chat.sendall(f"NICK {nick}".encode('utf-8'))
        
        # Creamos y lanzamos al 'trabajador extra' (el thread)
        # daemon=True hace que el hilo se cierre solo cuando cierres el programa
        hilo = threading.Thread(target=recibir_mensajes, args=(sock_chat,), daemon=True)
        hilo.start()
        
        print("\n--- Conectado ---")
        print("Comandos: MSG <texto>, HISTORY, USERS, DISCONNECT\n")
        print(
            "Conexion TCP:",
            f"{config['tcp_host']}:{config['tcp_port']}",
            "| API HTTP:",
            f"{config['http_scheme']}://{config['http_host']}:{config['http_port']}",
        )

        while True:
            # El programa se queda aquí esperando que se escriba algo
            opcion = input("")
            
            # Si escribes HISTORY o USERS, usamos la función HTTP manual
            if opcion.upper() == "HISTORY":
                consulta_http_manual(config, "/history")
            elif opcion.upper() == "USERS":
                consulta_http_manual(config, "/users")
            elif opcion.upper() == "DISCONNECT":
                sock_chat.sendall("DISCONNECT".encode('utf-8'))
                break
            elif opcion:
                # Cualquier otra cosa se manda como comando al chat TCP
                sock_chat.sendall(opcion.encode('utf-8'))
                
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock_chat.close()
        print("Saliendo de la galaxia...")

if __name__ == "__main__":
    iniciar_cliente()
