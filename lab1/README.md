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

El servidor TCP maneja los comandos del chat y la lógica del encío de mensajes; el servidor HTTP expone consultas de solo lectura y el servidor UDP registra eventos como conexiones, mensajes, desconexiones y errores.

## Archivos principales
- `chat_tcp.py`: Servidor principal. Levanta el chat TCP en el puerto `6000` y la API HTTP en el puerto `8080`.
- `logs_udp.py`: Servidor de logs UDP. Escucha en el puerto `6500` y guarda los eventos en el archivo `chat.log`.
- `cliente.py`: Cliente del chat. Se conecta por TCP al chat y, de manera independiente, consulta la API HTTP.
- `makefile`: Archivo que agiliza la ejecución de los archivos. Está pensado para el equipo que actúa como **servidor**.

## Disclaimers antes de la ejecución
1. La ejecución de la presente tarea tiene dos formas distintas de realizarse, pues, ésta depende si el equipo va a actuar como **cliente** o como **servidor**.
2. Para la ejecución en modo servidor se utiliza **ngrok**, para hacer uso de todas las funciones que la tarea necesita, se requiere tener una cuenta verificada en el sitio. Lo anterior puede requerir la inscripción de una tarjeta bancaria con el fin de verificar la cuenta. OJO: No se realizará ningún cobro, el registro de la tarjeta es únicamente para verificar la cuenta. No tenemos certeza de que esto ocurra en el 100% de los casos, pero al menos a nosotros, durante el desarrollo de la tarea, tuvimos que hacer registro de una tarjeta bancaria para poder acceder a las funciones de ngrok que la tarea requería.
3. Vamos a definir una constante que será útil en la ejecución en modo **servidor**: `PUERTO_TCP`, de valor `6000`.

## Instrucciones de ejecución

### Ejecución en modo servidor
1. Nos ubicamos en la carpeta `lab1` y ejecutamos en la terminal:

```bash
make run
```

Esto abre 2 ventanas de terminal: Una contiene el servidor UDP de logs y la otra contiene el servidor principal (TCP+HTTP).

2. Adicional a las 2 ventanas creadas, se deben abrir una tercera ventana de terminal donde ejecutaremos:

```bash
ngrok tcp 6000
```

*Nótese que `6000` corresponde al valor de la constante `PUERTO_TCP`, definida más arriba.*

Una vez levantado, **ngrok** entrega una dirección pública. Para la parte TCP entrega una dirección del tipo:

```text
tcp://0.tcp.ngrok.io:12345
```

De esta dirección, se van a extraer dos variables:
- La cadena de texto que inicia justo después del doble slash (`//`) y termina justo antes de los dos puntos al lado de `.io`. En el ejemplo, sería `0.tcp.ngrok.io`. A esta serie de caracteres la llamaremos `ngrok_tcp_link`.
- Los números que están a la derecha de los dos puntos al lado del `.io`. En el ejemplo, sería `12345`. A esta serie de números la llamaremos `ngrok_tcp_port`.

La extracción de estas variables es vital para ejecutar correctamente el archivo `cliente.py` en modo cliente. Lo anterior implica que **el anfitrión del servidor deberá proporcionarles estas variables a todas las personas que se quieran conectar al chat**.

3. En modo servidor, para ejecutar el cliente e interactuar con él, se abre una última pestaña de terminal y se ejecuta:

```bash
python3 cliente.py
```

### Ejecución en modo cliente
**NOTA**: Como ya se mencionó, la ejecución en modo cliente requiere tener a mano las variables `ngrok_tcp_link` y `ngrok_tcp_port`... Sin éstas, la ejecución desde una máquina remota no es posible.

1. Se abre una pestaña de terminal y se ejecuta:

```bash
python3 cliente.py {ngrok_tcp_link} {ngrok_tcp_port}
```

*A modo de apunte, los valores de `ngrok_tcp_link` y `ngrok_tcp_port` **NO** deben ponerse entre llaves, éstas solo indican que en ese lugar va el valor de la variable que corresponde.*

## En caso de querer realizar consultas HTTP
El archivo `chat_tcp.py` inicia también un servidor HTTP al cual se le pueden realizar una serie de consultas. Para poder realizarlas, el equipo que actúa como servidor, desde una ventana de terminal limpia, deberá ejecutar el siguiente comando:

```bash
ngrok http 8080
```

*Nótese que `8080` corresponde al valor de la constante `PUERTO_HTTP`, definida más arriba.*

Una vez hecho esto, **ngrok** entregará una dirección pública a la cual llamaremos `ngrok_http_link`. Para la parte HTTP entrega una dirección del tipo:

```text
https://xxxxx.ngrok-free.dev
```

*Nótese que `ngrok_http_link` debe seguir la estructura recién descrita.*

Ésta dirección será la que se use para realizar las consultas HTTP. Se admiten:
- `/history`: Devuelve un JSON del historial almacenado por el servidor.
- `/users`: Devuelve un JSON con la lista de usuarios conectados.

Para realizar cualquiera de estas consultas, se debe acudir al navegador de internet de su preferencia y escribir en la barra de búsqueda:

```bash
{ngrok_http_link}/{consulta}
```

*A modo de apunte, los valores de `ngrok_http_link` y `consulta` **NO** deben ponerse entre llaves, éstas solo indican que en ese lugar va el valor de la variable que corresponde. Por lo demás, `consulta` puede tomar el valor de `history` o `users`, no otro.*

## Uso del cliente
Al iniciar el cliente, se pide el nickname por consola utilizando el comando `NICK <nickname>`. Luego se puede interactuar con los siguientes comandos:

- `MSG <texto>`: Envía un mensaje al chat.
- `DISCONNECT`: Cierra la sesión actual y desconecta al usuario del chat.

## Protocolo TCP implementado
El flujo esperado del chat es el siguiente:
1. El cliente se conecta al servidor TCP.
2. El cliente registra su nickname.
3. Una vez registrado, puede enviar mensajes.
4. Cuando termina, se desconecta.

### Respuestas del servidor TCP
Algunas respuestas posibles del servidor son:
- `Bienvenido(a) al chat, <nickname>!`
- `[SERVER - Para tí]: ERROR - Nickname ocupado`
- `[SERVER - Para tí]: ERROR - Ya cuentas con un nickname (<nickname>)`
- `[SERVER - Para tí]: ERROR - Nickname no asignado. Usa 'NICK nombreDeUsuario' para definir uno`
- `[SERVER - Para tí]: ERROR - Comando desconocido`

Además, cuando entra o sale un usuario, el servidor retransmite mensajes del tipo:
- `[SERVER - Para todos]: <nickname> se unió al chat`
- `[SERVER - Para todos]: <nickname> ha abandonado el chat`

Los mensajes normales del chat se retransmiten con el formato:
- `<nickname>: <mensaje>`

## API HTTP

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
El servidor principal envía eventos al servidor UDP de logs. Los eventos se imprimen por consola y también se guardan en el archivo `chat.log`.

Los tipos de eventos que se registran son:
- `CONNECT`
- `MSG`
- `DISCONNECT`
- `ERROR`
