import socket
import threading
import http.server
import json
import datetime
from logs_udp import PUERTO_UDP as UDP_PORT, IP_UDP as UDP_IP

# ----- CONFIGURACIÓN DE REDES ----- #
PUERTO_TCP = 6000
PUERTO_HTTP = 8080

# ----- VARIABLES COMPARTIDAS ----- #
clientes = {}  # {socket: nickname}
historial = []  # ["msg1", "msg2"]
lock = threading.Lock()

# ----- FUNCIONES ----- #
def send_udp_log(event_type, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = f"[{timestamp}] - {event_type} - {message}"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socket_udp:
            socket_udp.sendto(log.encode('utf-8'), (UDP_IP, UDP_PORT))
    except: pass

def broadcast(message, exclude_conn=None):
    with lock:
        for conn in list(clientes.keys()):
            if conn != exclude_conn:
                try:
                    conn.sendall((message + "\n").encode('utf-8'))
                except:
                    conn.close()
                    del clientes[conn]

# ----- SERVIDOR TCP (CHAT) ----- #
def handle_tcp_client(conn, addr):
    nickname = None
    try:
        while True:
            usrInput = conn.recv(1024).decode('utf-8').strip()
            if not usrInput: break

            usrInputSplit = usrInput.split(' ', 1)
            comando = usrInputSplit[0].upper()
            args = usrInputSplit[1] if len(usrInputSplit) > 1 else ""

            if comando == "NICK":
                new_nick = args.strip()
                with lock:
                    if nickname != None: # Error por reasignación de nickname
                        conn.sendall(f"ERROR: Ya tienes un nickname ({nickname}) asignado\n".encode('utf-8'))
                        send_udp_log("ERROR", f"Usuario {nickname} intentó reasignar su nickname")
                        continue
                    if any(n.lower() == new_nick.lower() for n in clientes.values()): # Error de nick duplicado
                        conn.sendall("ERROR: Nick ocupado\n".encode('utf-8'))
                        send_udp_log("ERROR", f"Intento de nick duplicado: {new_nick}")
                        continue
                    nickname = new_nick
                    clientes[conn] = nickname
                
                broadcast(f"SERVER: {nickname} se unió")
                send_udp_log("CONNECT", f"{nickname} desde {addr}")
                conn.sendall(f"OK: Bienvenido(a), {nickname}\n".encode('utf-8'))

            elif comando == "MSG":
                if not nickname:
                    conn.sendall("ERROR: No tienes un nickname, usa 'NICK nombreDeUsuario' para definir uno\n".encode('utf-8'))
                    send_udp_log("ERROR", f"Usuario sin nickname intentó enviar mensaje desde {addr}")
                    continue
                mensaje = f"{nickname}: {args}"
                with lock:
                    historial.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {mensaje}")
                broadcast(mensaje)
                send_udp_log("MSG", f"Mensaje de {nickname}")

            elif comando == "DISCONNECT":
                break

            else:
                conn.sendall("ERROR: Comando desconocido\n".encode('utf-8'))
                send_udp_log("ERROR", f"Comando desconocido de {nickname if nickname else addr}: {usrInput}")
    except: pass
    
    if nickname:
        with lock:
            if conn in clientes: del clientes[conn]
        broadcast(f"SERVER: {nickname} se fue")
        send_udp_log("DISCONNECT", nickname)
    conn.close()

def run_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PUERTO_TCP))
    server.listen()
    print(f"    - Servidor TCP de chat corriendo en puerto {PUERTO_TCP}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()

# ----- SERVIDOR HTTP (ESTADO) ----- #
class StatusHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        # Usamos el lock para que nadie modifique los mensajes mientras los leemos
        with lock:
            if self.path == '/history':
                # Preparamos los datos con formato JSON. Mostraremos los ultimos 10 mensajes. Recordemos que la cantidad es arbitraria.
                respuesta_datos = {"history": historial[-10:]}
                self.enviar_json_manual(200,respuesta_datos)

            elif self.path == '/users':
                # Obtenemos la lista de nombres de los clientes conectados
                respuesta_datos = {"users": list(clientes.values())}
                self.enviar_json_manual(200,respuesta_datos)

            else:
                # Aca cae cuando la ruta no existe.
                self.send_error(404, "Ruta galáctica no encontrada")
    
    def enviar_json_manual(self,codigo,datos):
        # Funcion para cumplir con el envio manual de los headers
        # Convertimos los datos a texto JSON y luego Bytes
        cuerpo_respuesta = json.dumps(datos).encode('utf-8')

        # Enviamos la linea de estado 200 OK.
        self.send_response(codigo)

        # Enviamos los headers que exige el lab
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(cuerpo_respuesta)))
        self.end_headers() # Salto de linea anashe

        # Enviamos le contenido real
        self.wfile.write(cuerpo_respuesta)

def run_http_server():
    server = http.server.HTTPServer(('0.0.0.0', PUERTO_HTTP), StatusHandler)
    print(f"    - API HTTP corriendo en puerto {PUERTO_HTTP}")
    server.serve_forever()

# ----- MAIN ----- #
if __name__ == "__main__":
    print(f"----- Este es el archivo para los servidores TCP y HTTP -----")

    # Hilo para TCP
    tcp_thread = threading.Thread(target=run_tcp_server, daemon=True)
    tcp_thread.start()
    
    # El hilo principal se queda con el HTTP
    try:
        run_http_server()
    except KeyboardInterrupt:
        print("\nApagando servidores...")
