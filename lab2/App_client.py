import socket
import struct

DNS_SERVER_IP = '192.168.1.228'  # IP DEL PC QUE CORRE EL DNS SERVER
DNS_PORT = 53 #PUERTO POR DEFECTO DNS
DOMINIO_A_CONSULTAR = 'laboratorio.redes' #DOMINIO DE LA PAGINA A CONSULTAR

def build_dns_query(domain):
    transaction_id = b'\x12\x34'
    flags = b'\x01\x00'
    counts = b'\x00\x01\x00\x00\x00\x00\x00\x00'
    parts = domain.split('.')
    qname = b''
    for part in parts:
        qname += struct.pack('B', len(part)) + part.encode()
    qname += b'\x00'
    qtype_qclass = b'\x00\x01\x00\x01'
    
    return transaction_id + flags + counts + qname + qtype_qclass

def solve_and_connect():
    #CODE ZONE 1: Cliente UDP! Completa lo necesario para construir el socket de cliente!
    # -------------------
    sock_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock_udp.settimeout(5)
    
    query = build_dns_query(DOMINIO_A_CONSULTAR)
    
    try:
        sock_udp.sendto(query, (DNS_SERVER_IP, DNS_PORT))
        data, _ = sock_udp.recvfrom(1024)
        
        # ----

        # PARSER DE RESPUESTA DNS, NO TOCAR
        
        ip_bytes = data[-4:]
        resolved_ip = socket.inet_ntoa(ip_bytes)
        
        # ----

    except socket.timeout:
        print("Error: server DNS no responde")
        return
    finally:
        sock_udp.close()

    # ------------------------
    #CODE ZONE 2: Cliente TCP! construye un cliente TCP común para consultar al servidor central!
    # ------------------------
    sock_tcp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock_tcp.settimeout(5)
    
    try:
        # hint: Metodo connect de la librería socket!
        sock_tcp.connect(DNS_SERVER_IP,80)
        
        # Programa el envío de un mensaje de prueba (prueba con una consulta HTTP simple!)
        
        #EXTRA: si puedes, imprime el mensaje obtenido de la request por pantalla!
    except Exception as e:
        print(f"Error: Falló el handshake")
        sock_tcp.close()

    # -------------------------
if __name__ == "__main__":
    solve_and_connect()