# LAB1 - INF256 - Redes de Computadores

## Nombres y Roles
- Lucas Ansieta M. - 202373504-3
- Bastian Garces C. - 202373510-8
- Benjamin Palacios T. - 202373532-9

## Descripcion general
Este laboratorio implementa un sistema de chat compuesto por tres partes:

- Un servidor principal que levanta el chat TCP y la API HTTP.
- Un servidor UDP que recibe y guarda los logs.
- Un cliente que permite participar en el chat y consultar el estado del servidor.

El servidor TCP maneja los comandos del chat, el servidor HTTP expone consultas de solo lectura y el servidor UDP registra eventos como conexiones, mensajes, desconexiones y errores.

## Archivos principales
- `chat_tcp.py`: servidor principal. Levanta el chat TCP en el puerto `6000` y la API HTTP en el puerto `8080`.
- `logs_udp.py`: servidor de logs UDP. Escucha en el puerto `6500` y guarda los eventos en `chat.log`.
- `cliente.py`: cliente del chat. Se conecta por TCP al chat y, de manera independiente, consulta la API HTTP.
- `makefile`: ayuda para levantar una prueba local rapida.

## Instrucciones de ejecucion
### Opcion 1: ejecucion local rapida
Dentro de la carpeta `lab1`, ejecutar:

```bash
make run
```

Esto abre tres terminales:

1. Servidor UDP de logs.
2. Servidor principal TCP + HTTP.
3. Cliente del chat.

La ventana con la que se interactua directamente es la del cliente.

### Opcion 2: ejecucion manual
Tambien se puede levantar cada componente por separado:

Terminal 1:
```bash
python3 logs_udp.py
```

Terminal 2:
```bash
python3 chat_tcp.py
```

Terminal 3:
```bash
python3 cliente.py
```

## Uso del cliente
Al iniciar el cliente, se pide el nickname por consola. Luego se puede interactuar con los siguientes comandos:

- `MSG <texto>`: envia un mensaje al chat.
- `HISTORY`: consulta por HTTP el historial almacenado por el servidor.
- `USERS`: consulta por HTTP la lista de usuarios conectados.
- `DISCONNECT`: cierra la sesion actual.

## Protocolo TCP implementado
El flujo esperado del chat es el siguiente:

1. El cliente se conecta al servidor TCP.
2. El cliente envia su nickname.
3. Una vez registrado, puede enviar mensajes.
4. Cuando termina, se desconecta.

Los comandos soportados por el servidor son:

- `NICK <nombre>`: registra al usuario en memoria.
- `MSG <texto>`: envia un mensaje al resto de los usuarios conectados.
- `DISCONNECT`: cierra la conexion y elimina al usuario del registro activo.

### Respuestas del servidor TCP
Algunas respuestas posibles del servidor son:

- `OK: Bienvenido(a), <nickname>`
- `ERROR: Nick ocupado`
- `ERROR: Ya tienes un nickname (<nickname>) asignado`
- `ERROR: No tienes un nickname, usa 'NICK nombreDeUsuario' para definir uno`
- `ERROR: Comando desconocido`

Ademas, cuando entra o sale un usuario, el servidor retransmite mensajes del tipo:

- `SERVER: <nickname> se unio`
- `SERVER: <nickname> se fue`

Los mensajes normales del chat se retransmiten con el formato:

- `<nickname>: <mensaje>`

## API HTTP
La API HTTP corre en el puerto `8080` y expone dos rutas:

- `GET /history`: retorna el historial de mensajes.
- `GET /users`: retorna la lista de usuarios conectados.

### Formato de respuestas HTTP
Para las rutas validas, el servidor responde en formato JSON:

```json
{"history": ["[12:00:00] usuario: hola"]}
```

```json
{"users": ["usuario1", "usuario2"]}
```

Para rutas no definidas:

```json
{"error": "Ruta galactica no encontrada"}
```

Para solicitudes malformadas:

```json
{"error": "Solicitud malformada"}
```

## Historial de mensajes
El servidor mantiene en memoria el historial del chat y expone por HTTP solo los ultimos `10` mensajes.

## Logs UDP
El servidor principal envia eventos por UDP al servidor de logs. Los eventos se imprimen por consola y tambien se guardan en el archivo `chat.log`.

Los tipos de eventos que se registran son:

- `CONNECT`
- `MSG`
- `DISCONNECT`
- `ERROR`

## Uso del cliente con parametros
Ademas de la ejecucion local, el cliente permite conectarse a otras direcciones si se entregan parametros por linea de comandos.

### Formas de uso
Modo local:

```bash
python3 cliente.py
```

Modo con host y puerto TCP:

```bash
python3 cliente.py <tcp_host> <tcp_port>
```

Modo con host y puerto TCP, mas host y puerto HTTP:

```bash
python3 cliente.py <tcp_host> <tcp_port> <http_host> <http_port> [http|https]
```

Ejemplo:

```bash
python3 cliente.py 0.tcp.ngrok.io 12345 ejemplo.ngrok-free.dev 443 https
```

Esto permite mantener el chat TCP y las consultas HTTP apuntando a destinos distintos, lo que nos sirvio para las pruebas del componente de exposicion publica.

## Exposicion publica con ngrok
Para exponer la API HTTP de forma publica se utilizo `ngrok` sobre el puerto `8080`.

Ejemplo:

```bash
ngrok http 8080
```

Una vez levantado, `ngrok` entrega una URL publica del tipo:

```text
https://xxxxx.ngrok-free.dev
```

Con esa URL se pueden probar las rutas:

```bash
curl https://xxxxx.ngrok-free.dev/users
curl https://xxxxx.ngrok-free.dev/history
```

## Comentario final
En las pruebas locales, las acciones que se realizan en el cliente se reflejan inmediatamente en la terminal del servidor UDP, que es donde se observan los logs del sistema.
