# ----- VARIABLES -----
PYTHON = python3
LOG_SERVER = logs_udp.py
CHAT_SERVER = chat_tcp.py
# Añadimos tu script de cliente
CLIENT_SCRIPT = cliente.py
TCP_PORT = 6000

# Detectar Sistema Operativo
OS := $(shell uname -s 2>/dev/null || echo Windows)

.PHONY: all run clean help

help:
	@echo "Uso: make run  -> Abre Logs, Servidor y Cliente nc"

run:
ifeq ($(OS), Darwin)
	@echo "Detectado macOS... Abriendo 3 terminales."
	@# 1. Servidor de Logs
	@osascript -e 'tell app "Terminal" to do script "cd \"$(PWD)\" && $(PYTHON) $(LOG_SERVER)"'
	@# 2. Servidor de Chat
	@osascript -e 'tell app "Terminal" to do script "cd \"$(PWD)\" && $(PYTHON) $(CHAT_SERVER)"'
	@# 3. Cliente TCP (Usando tu script de python)
	@osascript -e 'tell app "Terminal" to do script "sleep 1 && echo \"----- CLIENTE TCP: Usa *NICK nombreDeUsuario* para empezar  -----\" && $(PYTHON) $(CLIENT_SCRIPT)"'

else ifeq ($(OS), Linux)
	@echo "Detectado Linux..."
	@# 1. Servidor de Logs
	@gnome-terminal -- bash -c "cd '$(PWD)' && $(PYTHON) $(LOG_SERVER); exec bash"
	@# 2. Servidor de Chat
	@gnome-terminal -- bash -c "cd '$(PWD)' && $(PYTHON) $(CHAT_SERVER); exec bash"
	@# 3. Cliente TCP (Usando tu script de python)
	@gnome-terminal -- bash -c "sleep 1; echo '----- CLIENTE TCP: Usa *NICK nombreDeUsuario* para empezar  -----'; $(PYTHON) $(CLIENT_SCRIPT); exec bash"

else
	@echo "Detectado Windows..."
	@# En Windows 'nc' no es nativo, se suele usar 'telnet' o instalar nmap (ncat)
	@start cmd /k "cd /d $(PWD) && $(PYTHON) $(LOG_SERVER)"
	@start cmd /k "cd /d $(PWD) && $(PYTHON) $(CHAT_SERVER)"
	@echo "En Windows, si no tienes netcat, usa: telnet localhost $(TCP_PORT)"
	@# 3. Cliente TCP en Windows usando tu script
	@start cmd /k "timeout /t 2 && echo Intentando conectar... && $(PYTHON) $(CLIENT_SCRIPT)"
endif

clean:
	rm -rf __pycache__
	rm -f *.pyc