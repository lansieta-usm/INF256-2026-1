import socket
import threading

# 1. Configuración: A dónde nos vamos a conectar
IP_SERVIDOR = "127.0.0.1" 
PUERTO_TCP = 6000
PUERTO_HTTP = 8080

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

def consulta_http_manual(ruta):
    # Función para pedir datos por HTTP.
    # Creamos un socket TCP nuevo solo para esta pregunta
    sock_http = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_http.connect((IP_SERVIDOR, PUERTO_HTTP))
        
        # Construimos el mensaje HTTP
        peticion = f"GET {ruta} HTTP/1.1\r\nHost: {IP_SERVIDOR}\r\nConnection: close\r\n\r\n"
        # Envia la peticion
        sock_http.sendall(peticion.encode('utf-8'))
        
        # Leemos la respuesta que nos mande el servidor
        respuesta = sock_http.recv(4096).decode('utf-8')
        print(f"\n--- RESPUESTA DEL SERVIDOR ({ruta}) ---\n{respuesta}")

    except Exception as e:
        print(f"[!] No se pudo conectar a la API: {e}")

    # Para no gastar recursos 
    finally:
        sock_http.close()

def iniciar_cliente():
    # Creamos el socket principal para el chat. 
    sock_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock_chat.connect((IP_SERVIDOR, PUERTO_TCP))
        
        # Lo primero que enviamos es el NICK
        nick = input("Bienvenido. Ingresa tu Nickname: ")
        sock_chat.sendall(f"NICK {nick}".encode('utf-8'))
        
        # Creamos y lanzamos al 'trabajador extra' (el thread)
        # daemon=True hace que el hilo se cierre solo cuando cierres el programa
        hilo = threading.Thread(target=recibir_mensajes, args=(sock_chat,), daemon=True)
        hilo.start()
        
        print("\n--- Conectado ---")
        print("Comandos: MSG <texto>, HISTORY, USERS, DISCONNECT\n")

        while True:
            # El programa se queda aquí esperando que se escriba algo
            opcion = input("")
            
            # Si escribes HISTORY o USERS, usamos la función HTTP manual
            if opcion.upper() == "HISTORY":
                consulta_http_manual("/history")
            elif opcion.upper() == "USERS":
                consulta_http_manual("/users")
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