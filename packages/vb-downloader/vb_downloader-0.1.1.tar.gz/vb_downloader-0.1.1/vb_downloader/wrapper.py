#!/usr/bin/env python
import sys
import os

# Adicionar o diretório pai ao PATH se não estiver
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Importação relativa
from . import gui

def main():
    """Função principal que inicia a aplicação."""
    gui.main()

if __name__ == "__main__":
    main()
