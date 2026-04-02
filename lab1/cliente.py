import socket
import sys
import threading
from chat_tcp import PUERTO_TCP as DEFAULT_TCP_PORT, PUERTO_HTTP as DEFAULT_HTTP_PORT

# Valores por defecto para correr todo en local.
DEFAULT_TCP_HOST = "127.0.0.1"
DEFAULT_HTTP_HOST = "127.0.0.1"

def cargar_configuracion():
    tcp_host = DEFAULT_TCP_HOST
    tcp_port = DEFAULT_TCP_PORT
    http_host = DEFAULT_HTTP_HOST
    http_port = DEFAULT_HTTP_PORT

    args = sys.argv[1:] # NOTA: Se puede usar sin parametros o indicando host/puertos manualmente.

    if len(args) not in (0, 2, 4):
        print("Uso:")
        print("  python3 cliente.py")
        print("  python3 cliente.py <tcp_host> <tcp_port>")
        print("  python3 cliente.py <tcp_host> <tcp_port> <http_host> <http_port>")
        sys.exit(1)

    try:
        if len(args) >= 2:
            tcp_host = args[0]
            tcp_port = int(args[1])
            http_host = tcp_host
            http_port = 80

        if len(args) >= 4:
            http_host = args[2]
            http_port = int(args[3])
    except ValueError as e:
        print(f"[!] Configuración inválida: {e}")
        sys.exit(1)

    return {
        "tcp_host": tcp_host,
        "tcp_port": tcp_port,
        "http_host": http_host,
        "http_port": http_port,
    }

def recibir_mensajes(sock): # Función para recibir inputs del servidor TCP
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
	
def consulta_http_manual(config, ruta): # Usa un socket aparte para no mezclarla con el chat.
    sock_http = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_http.connect((config["http_host"], config["http_port"]))

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
        print(f"\n--- RESPUESTA DEL SERVIDOR ({ruta}) ---\n{respuesta}")

    except Exception as e:
        print(f"[!] No se pudo conectar a la API: {e}")
	
    finally:
        sock_http.close()
	
def iniciar_cliente(): # Función principal para iniciar el cliente, cargar configuración y manejar la interacción con el usuario.
    config = cargar_configuracion()

    sock_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock_chat.connect((config["tcp_host"], config["tcp_port"]))
        
        nick = input("Bienvenido(a). Utiliza 'NICK <nickname>' para establecer tu nombre de usuario: ")
        sock_chat.sendall(f"{nick}".encode('utf-8'))
        while nick[0:5].upper() != "NICK " or len(nick) <= 5:
            nick = input("Reingresa tu nombre de usuario usando 'NICK <nickname>': ")
            sock_chat.sendall(f"{nick}".encode('utf-8'))
	        
        hilo = threading.Thread(target=recibir_mensajes, args=(sock_chat,), daemon=True)
        hilo.start()
        
        print(f"----- ¡OK! Conexión exitosa para {nick[5:]} -----")
        print()
        print("""[SERVER - Pata tí]: Lista de comandos disponibles:
    - MSG <texto>: Envía un mensaje al chat
    - DISCONNECT: Cierra la sesión y desconecta del chat
    - HISTORY: Consulta por HTTP el historial almacenado por el servidor
    - USERS: Consulta por HTTP la lista de usuarios conectados
""")

        print(f"""[SERVER - Para tí]: Links a las distintas conexiones:
    - Conexión TCP: {config['tcp_host']}:{config['tcp_port']}
    - API HTTP: http://{config['http_host']}:{config['http_port']}
""")

        while True:
            opcion = input()
            
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
