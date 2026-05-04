import socket

IP_ESCUCHA = '0.0.0.0'
PUERTO_DNS = 52
IP_RESPUESTA = '192.168.1.232'
DOMINIO_OBJETIVO = 'laboratorio.redes'

def build_response(data):
    transaction_id = data[:2]
    flags = b'\x85\x80'
    counts = b'\x00\x01\x00\x01\x00\x00\x00\x00'
    header = transaction_id + flags + counts
    end_of_query = data.find(b'\x00', 12) + 1
    question_section = data[12:end_of_query + 4] 
    ans_name = b'\xc0\x0c'
    ans_type_class = b'\x00\x01\x00\x01'
    ans_ttl = b'\x00\x00\x00\x3c'
    ans_rdlength = b'\x00\x04'
    ip_parts = [int(part) for part in IP_RESPUESTA.split('.')]
    ans_rdata = bytes(ip_parts)
    answer_section = ans_name + ans_type_class + ans_ttl + ans_rdlength + ans_rdata
    return header + question_section + answer_section

def start_dns_server():
    # CODE ZONE! - CREAR SOCKET UDP PARA EL SERVIDOR BASADO EN LOS DATOS DE LAS LINEAS 3,4,5,6

    # -------------------------
    # Hint: método .socket y .bind de la librería socket!
    UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPsocket.bind((IP_ESCUCHA, PUERTO_DNS))

    # Hint2: recordar lo realizado durante la entrega 1, como realizar un socket UDP
    # Hint3: usar un while para asegurar respuestas constantes podría ser útil.
    print(f'Socket UDP corriendo en {IP_ESCUCHA}, puerto {PUERTO_DNS}.')
    print()
    while True:
        data, addr = UDPsocket.recvfrom(1024)
        infoRecibida = data.decode("utf-8")

        respuesta = build_response(data)
        UDPsocket.sendto(respuesta, addr)

        print(f'infoRecibida: {infoRecibida}')

    # -------------------------

if __name__ == "__main__":
    start_dns_server()