# LAB1 - INF256 - Redes de Computadores

## Nombres y Roles
- Lucas Ansieta M. - 202373504-3
- Bastián Garcés C. - 202373510-8
- Benjamín Palacios T. - 202373532-9

## Instrucciones de ejecución (hasta el momento)
En la terminal, abrir la carpeta ```lab1``` y ejecutar:
```bash
make run
```

## Comentarios (borrar después)
### ¿Qué se abrirá?
Al ejecutar ```make run``` se les abrirán 3 pestañas de terminal: 
1. Servidor TCP: Básicamente es el proceso que inicia el servidor TCP para el chat. **OJO: Esta ventana NO ES EL CHAT**.
2. Servidor UDP: En esta pestaña de terminal aparecerán todos los logs.
3. Cliente TCP: Esta pestaña de terminal es el Chat... Acá se ejecutan los comandos, se mandan mensajes, etc.

### ¿Con qué interactúo?
Con la pestaña de terminal que siga **Cliente TCP**... Ese es el chat.

Cuando se realicen acciones en el Cliente TCP, éstas se verán reflejadas en la terminal del **Servidor UDP**, esto significa que si desde el Cliente TCP hago algo como ```NICK nickname```, en el Servidor UDP aparecerá el log que diga que ```nickname``` se acaba de conectar.

### Funciona en Windows?
No tengo ni puta idea, testeé la wea en macOS nomás, si no funciona, mala cuea XD.