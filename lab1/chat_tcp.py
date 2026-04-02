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
def send_udp_log(event_type, message): # Envía mensajes de log a la terminal correspondiente y al archivo 'chat.log'
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = f"[{timestamp}] - {event_type} - {message}"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketUDP:
            socketUDP.sendto(log.encode('utf-8'), (UDP_IP, UDP_PORT))
    except: pass

def broadcast(message, exclude_conn=None): # Envía un mensaje público (a todo el chat)
    with lock:
        for conn in list(clientes.keys()):
            if conn != exclude_conn:
                try:
                    conn.sendall((message + "\n").encode('utf-8'))
                except:
                    conn.close()
                    del clientes[conn]

# ----- SERVIDOR TCP (CHAT) ----- #
def handle_tcp_client(conn, addr): # Función que contiene el backend de cada comando del servidor TCP
    nickname = None
    try:
        while True:
            usrInput = conn.recv(1024).decode('utf-8').strip()
            if not usrInput: break

            usrInputSplit = usrInput.split(' ', 1)
            comando = usrInputSplit[0].upper()
            args = usrInputSplit[1] if len(usrInputSplit) > 1 else ""

            if comando == "NICK":
                inputNickname = args.strip()
                with lock:
                    if nickname != None: # Error por reasignación de nickname
                        conn.sendall(f"[SERVER - Para tí]: ERROR - Ya cuentas con un nickname ({nickname})\n".encode('utf-8'))
                        send_udp_log("ERROR", f"Usuario *{nickname}* intentó reasignar su nickname")
                        continue
                    if any(n.lower() == inputNickname.lower() for n in clientes.values()): # Error de nickname ya existente
                        conn.sendall(f"[SERVER - Para tí]: ERROR - Nickname ocupado\n".encode('utf-8'))
                        send_udp_log("ERROR", f"Usuario sin nickname (addr={addr}) intentó usar nickname ya existente (*{inputNickname}*)")
                        continue

                    nickname = inputNickname
                    clientes[conn] = nickname
                
                broadcast(f"[SERVER - Para todos]: {nickname} se unió al chat")
                conn.sendall(f"Bienvenido(a) al chat, {nickname}!\n".encode('utf-8'))
                send_udp_log("CONNECT", f"Usuario *{nickname}* se ha contectado desde {addr}")

            elif comando == "MSG":
                if not nickname: # Error por no asignación de nickname
                    conn.sendall("[SERVER - Para tí]: ERROR - Nickname no asignado. Usa 'NICK nombreDeUsuario' para definir uno\n".encode('utf-8'))
                    send_udp_log("ERROR", f"Usuario sin nickname (addr={addr}) intentó enviar mensaje: {args}")
                    continue
                
                mensaje = f"{nickname}: {args}"
                with lock:
                    historial.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {mensaje}")
                broadcast(mensaje)
                send_udp_log("MSG", f"Mensaje de *{nickname}*: {args}")

            elif comando == "DISCONNECT":
                break

            else:
                conn.sendall("[SERVER - Para tí]: ERROR - Comando desconocido\n".encode('utf-8'))
                send_udp_log("ERROR", f"Comando desconocido de {nickname if nickname else addr}: {usrInput}")
    except: pass
    
    if nickname:
        with lock:
            if conn in clientes: del clientes[conn]
        broadcast(f"[SERVER - Para todos]: {nickname} ha abandonado el chat")
        send_udp_log("DISCONNECT", f"*{nickname}* se ha desconectado")
    conn.close()

def run_tcp_server(): # Pone a correr el servidor TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PUERTO_TCP))
    server.listen()
    print(f"    - Servidor TCP de chat corriendo enx puerto {PUERTO_TCP}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()

# ----- SERVIDOR HTTP (ESTADO) ----- #
class StatusHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/history':
            with lock:
                respuesta = {"history": historial[-10:]}
            self.enviar_json_manual(200, respuesta)

        elif self.path == '/users':
            with lock:
                respuesta = {"users": list(clientes.values())}
            self.enviar_json_manual(200, respuesta)

        elif self.path == '/status':
            with lock:
                respuesta = {
                    "usuarios_conectados": list(clientes.values()),
                    "total": len(clientes),
                    "historial": historial[-10:]
                }
            self.enviar_json_manual(200, respuesta)
        else:
            self.enviar_json_manual(404, {"error": "Ruta galactica no encontrada"})

    def send_error(self, code, message=None, explain=None):
        if code == 400:
            self.enviar_json_manual(400, {"error": message or "Solicitud malformada"})
            return

        super().send_error(code, message, explain)

    def enviar_json_manual(self, codigo, datos):
        cuerpo_respuesta = json.dumps(datos).encode('utf-8')
        self.send_response(codigo)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(cuerpo_respuesta)))
        self.end_headers()
        self.wfile.write(cuerpo_respuesta)

    # Desactivar logs por consola de HTTP para no ensuciar
    def log_message(self, format, *args): return

def run_http_server(): # Pone a correr el servidor HTTP
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