import socket
import threading
import ssl
import sys
from chat_tcp import PUERTO_TCP as DEFAULT_TCP_PORT, PUERTO_HTTP as DEFAULT_HTTP_PORT

# Configuraciones locales
DEFAULT_TCP_HOST = "127.0.0.1"
DEFAULT_HTTP_HOST = "127.0.0.1"
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

def recibir_mensajes(sock): # Se queda escuchando mensajes del servidor TCP y los imprime por consola
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            if data:
                print(f"\n{data}\n ", end="")
            else:
                break
        except:
            print("\n[!] Error recibiendo mensajes.")
            break

def consulta_http_manual(config, ruta): # Función para pedir datos por HTTP
    sock_http = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_http.connect((config["http_host"], config["http_port"]))

        if config["http_scheme"] == "https":
            contexto = ssl.create_default_context()
            sock_http = contexto.wrap_socket(sock_http, server_hostname=config["http_host"])

        # Construcción del mensaje HTTP
        peticion = (
            f"GET {ruta} HTTP/1.1\r\n"
            f"Host: {config['http_host']}\r\n"
            "Connection: close\r\n\r\n"
        )
        sock_http.sendall(peticion.encode('utf-8'))

        fragmentos = []
        while True:
            data = sock_http.recv(4096)
            if not data:
                break
            fragmentos.append(data)

        respuesta = b"".join(fragmentos).decode('utf-8', errors='replace')
        print(f"\n----- RESPUESTA DEL SERVIDOR ({ruta}) -----\n{respuesta}")

    except Exception as e:
        print(f"[!] No se pudo conectar a la API: {e}")

    finally:
        sock_http.close()

def iniciar_cliente(): # Función que inicia el cliente TCP para el chat
    config = cargar_configuracion()

    sock_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock_chat.connect((config["tcp_host"], config["tcp_port"]))
        
        nick = input("Bienvenido(a). Ingresa tu Nickname: ")
        sock_chat.sendall(f"NICK {nick}".encode('utf-8'))

        hilo = threading.Thread(target=recibir_mensajes, args=(sock_chat,), daemon=True)
        hilo.start()
        
        print("[SERVER - Para tí]: Conectado(a) exitosamente")
        print("""[SERVER - Para tí]: Puedes utilizar los siguiente comandos:
    - MSG <mensaje> - Envía un mensaje a todos los participantes
    - HISTORY - Muestra el historial de mensajes
    - USERS - Entrega una lista de los usuarios conectados
    - DISCONNECT - Para desconectarse del chat
""")
        print(f"""[SERVER - Para tí]: Links de conexión:
    - Conexion TCP: {config['tcp_host']}:{config['tcp_port']}
    - API HTTP: {config['http_scheme']}://{config['http_host']}:{config['http_port']}
""")

        while True:
            opcion = input("")
            
            if opcion.upper() == "HISTORY":
                consulta_http_manual(config, "/history")
            elif opcion.upper() == "USERS":
                consulta_http_manual(config, "/users")
            elif opcion.upper() == "DISCONNECT":
                sock_chat.sendall("DISCONNECT".encode('utf-8'))
                break
            elif opcion:
                sock_chat.sendall(opcion.encode('utf-8'))
                
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock_chat.close()
        print("Saliendo de la galaxia...")

if __name__ == "__main__":
    iniciar_cliente()
