from setuptools import setup, find_packages
import sys
import subprocess
import os

# Verificar se tkinter está disponível
try:
    import tkinter
except ImportError:
    print("AVISO: tkinter não está instalado. Este pacote requer tkinter para funcionar.")
    print("No Windows, reinstale o Python e selecione a opção 'tcl/tk and IDLE'.")
    print("No Linux, instale o pacote python3-tk (ex: sudo apt-get install python3-tk).")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Criar um script batch para Windows
if sys.platform == 'win32':
    batch_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vb-downloader.bat')
    with open(batch_script, 'w') as f:
        f.write('@echo off\r\n')
        f.write('python -m vb_downloader.gui %*\r\n')

setup(
    name="vb-downloader",
    version="0.1.1",
    author="Erik Rocha",
    author_email="e.lucasrocha@gmail.com",
    description="Aplicativo para download automático do programa 'A Voz do Brasil'",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/vb-downloader",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "appdirs>=1.4.4",
    ],
    entry_points={
        "console_scripts": [
            "vb-downloader=vb_downloader.wrapper:main" if not sys.platform == 'win32' else "vb-downloader=vb_downloader.wrapper:main",
        ],
    },
    scripts=['vb-downloader.bat'] if sys.platform == 'win32' else [],
    include_package_data=True,
)
