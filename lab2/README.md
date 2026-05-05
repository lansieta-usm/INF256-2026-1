# LAB2 - INF256 - Redes de Computadores

## Nombres y Roles
- Lucas Ansieta M. - 202373504-3
- Bastian Garces C. - 202373510-8
- Benjamin Palacios T. - 202373532-9

## Descripción general
Este desarrollo consiste en una implementación práctica de un sistema de resolución de nombres de dominio (DNS) y una conexión posterior vía TCP, está compuesto por:

- `App_client.py`: Cliente que realiza consultas DNS, construye un paquete de consulta DNS manual, lo envía por UDP y parsea la respuesta para extraer la IP. Luego, inicia un handshake TCP hacia la IP resuelta para simular una petición HTTP.
- `DNS_server.py`: Implementación de un servidor UDP que simula el comportamiento de un servidor DNS, escucha peticiones UDP, construye una respuesta binaria usando el formato del protocolo DNS y resuelve el dominio `laboratorio.redes` a la IP `192.168.1.232`.

## Instrucciones de ejecución

### Servidor DNS
Desde una terminal limpia, ejecutamos:
```bash
python3 DNS_server.py
```

### Cliente
Abrimos una segunda terminal y ejecutamos:
```bash
python3 App_client.py
```

## Consideraciones adicionales
-   **Puerto 53:** El uso del puerto `53` (DNS estándar) puede requerir permisos de administrador (`sudo` en Linux/macOS o `Ejecutar como Administrador` en Windows).
-   **Alineación de Puertos:** Se debe verificar que la variable `PUERTO_DNS` en el servidor y `DNS_PORT` en el cliente coincidan.
-   **Handshake TCP:** Para que la segunda parte del cliente (`sock_tcp.connect`) sea exitosa, debe existir un servicio (como un servidor web o un socket escuchando) en la IP de destino en el puerto 80.
-   **Archivos `.pcapng`:** Estos archivos corresponden a evidencia de que el grupo estuvo presente durante la experiencia presencial, pues el contenido de éstos representa todos los paquetes capturados durante la ejecución del laboratorio.
