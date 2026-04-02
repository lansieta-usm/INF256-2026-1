# ----- VARIABLES -----
PYTHON = python3
LOG_SERVER = logs_udp.py
CHAT_SERVER = chat_tcp.py
CLIENT_SCRIPT = cliente.py
PUERTO_TCP = 6000

# Detectar Sistema Operativo
OS := $(shell uname -s 2>/dev/null || echo Windows)

.PHONY: all run clean help

help:
	@echo "Uso: make run  -> Abre servidor de Logs y servidor principal"

run:
ifeq ($(OS), Darwin)
	@echo "Detectado macOS... Abriendo 2 terminales."
	@# 1. Servidor de Logs
	@osascript -e 'tell app "Terminal" to do script "cd \"$(PWD)\" && $(PYTHON) $(LOG_SERVER)"'
	@# 2. Servidor de Chat
	@osascript -e 'tell app "Terminal" to do script "cd \"$(PWD)\" && $(PYTHON) $(CHAT_SERVER)"'

else ifeq ($(OS), Linux)
	@echo "Detectado Linux..."
	@# 1. Servidor de Logs
	@gnome-terminal -- bash -c "cd '$(PWD)' && $(PYTHON) $(LOG_SERVER); exec bash"
	@# 2. Servidor de Chat
	@gnome-terminal -- bash -c "cd '$(PWD)' && $(PYTHON) $(CHAT_SERVER); exec bash"

else
	@echo "Detectado Windows..."
	@start cmd /k "cd /d $(PWD) && $(PYTHON) $(LOG_SERVER)"
	@start cmd /k "cd /d $(PWD) && $(PYTHON) $(CHAT_SERVER)"
endif

clean:
	rm -rf __pycache__
	rm -f *.pyc
	