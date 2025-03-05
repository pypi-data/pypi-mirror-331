"""
Interface gráfica para o VB Downloader.

Este módulo implementa a interface gráfica do aplicativo VB Downloader,
permitindo ao usuário configurar e controlar o download do programa 'A Voz do Brasil'.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import re
import appdirs

# Importação relativa dentro do pacote
from . import downloader

class Application:
    """Classe principal da aplicação."""
    
    def __init__(self, master=None):
        """
        Inicializa a aplicação.
        
        Args:
            master: Janela principal do Tkinter
        """
        self.root = master
        self.root.title("VB Downloader")
        self.root.configure(bg="#f0f0f0")  # Cor de fundo padrão
        self.root.resizable(False, False)  # Impedir redimensionamento da janela
        
        # Configurar diretório de dados do usuário
        self.data_dir = appdirs.user_data_dir("vb-downloader", "erikrocha")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        self.config_file = os.path.join(self.data_dir, "config.txt")
        self.pasta_destino = tk.StringVar(value="")
        self.prefixo_nome = tk.StringVar(value="audio")
        self.monitorando = [False]  # Usando uma lista para ser modificada dentro de threads
        self.thread_monitoramento = None

        # Definir estilo
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", font=("Arial", 10))
        self.style.configure("Green.TButton", background="#4caf50", foreground="black", font=("Arial", 10, "bold"))
        self.style.configure("Red.TButton", background="#f44336", foreground="black", font=("Arial", 10, "bold"))
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0")
        self.style.configure("Header.TLabel", font=("Arial", 11, "bold"))
        self.style.configure("Title.TLabel", font=("Arial", 12, "bold"), foreground="#2c3e50")
        self.style.configure("Credits.TFrame", relief="groove", borderwidth=1)

        self.load_config()
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Cria os widgets da interface."""
        self.create_main_frame()
        self.create_credits_frame()

    def create_main_frame(self):
        """Cria o frame principal com os controles."""
        # Frame principal
        self.frame_principal = ttk.Frame(self.root, padding="10 10 10 10", style="TFrame")
        self.frame_principal.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Pasta de destino
        self.label_pasta = ttk.Label(self.frame_principal, text="Pasta de Destino:", style="Header.TLabel")
        self.label_pasta.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Frame para pasta e botões
        self.frame_pasta = ttk.Frame(self.frame_principal)
        self.frame_pasta.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.frame_pasta.columnconfigure(0, weight=1)

        self.entry_pasta = ttk.Entry(self.frame_pasta, textvariable=self.pasta_destino, width=40)
        self.entry_pasta.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.botao_selecionar_pasta = ttk.Button(self.frame_pasta, text="📁", width=3, command=self.selecionar_pasta)
        self.botao_selecionar_pasta.grid(row=0, column=1, padx=2)
        
        # Nome do arquivo
        self.label_nome = ttk.Label(self.frame_principal, text="Nome do Arquivo:", style="Header.TLabel")
        self.label_nome.grid(row=2, column=0, sticky="w", pady=(15, 5))

        self.entry_nome = ttk.Entry(self.frame_principal, textvariable=self.prefixo_nome, width=40)
        self.entry_nome.grid(row=3, column=0, columnspan=3, sticky="ew", padx=(0, 5))
        
        # Frame para botões de controle
        self.frame_botoes = ttk.Frame(self.frame_principal)
        self.frame_botoes.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(15, 0))
        self.frame_botoes.columnconfigure(0, weight=1)
        self.frame_botoes.columnconfigure(1, weight=1)
        
        # Botões de controle com largura fixa
        self.botao_iniciar = ttk.Button(self.frame_botoes, text="▶️ Iniciar", 
                                       command=self.iniciar_monitoramento, style="Green.TButton", width=15)
        self.botao_iniciar.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.botao_parar = ttk.Button(self.frame_botoes, text="⏹️ Parar", 
                                     command=self.parar_monitoramento, state=tk.DISABLED, style="Red.TButton", width=15)
        self.botao_parar.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def create_credits_frame(self):
        """Cria o frame de créditos."""
        # Frame para os créditos
        self.frame_creditos = ttk.Frame(self.root, style="Credits.TFrame")
        self.frame_creditos.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        # Título
        self.label_titulo = ttk.Label(self.frame_creditos, text="Informações do Desenvolvedor", 
                                     style="Title.TLabel", anchor="center")
        self.label_titulo.pack(pady=(10, 5), fill=tk.X)
        
        # Frame para informações
        self.frame_info = ttk.Frame(self.frame_creditos)
        self.frame_info.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        # Desenvolvedor
        self.label_desenvolvedor = ttk.Label(self.frame_info, text="👨‍💻 Desenvolvido por: Erik Rocha")
        self.label_desenvolvedor.pack(pady=(5, 2), anchor="center")
        
        # Contato
        self.label_contato = ttk.Label(self.frame_info, text="📧 Contato: e.lucasrocha@gmail.com")
        self.label_contato.pack(pady=2, anchor="center")
        
        # Chave PIX
        self.label_pix_titulo = ttk.Label(self.frame_info, text="💰 Contribuições (PIX):", font=("Arial", 9, "bold"))
        self.label_pix_titulo.pack(pady=(5, 2), anchor="center")
        
        self.label_pix = ttk.Label(self.frame_info, text="e.lucasrocha@gmail.com")
        self.label_pix.pack(pady=(0, 5), anchor="center")

    def selecionar_pasta(self):
        """Abre o diálogo para selecionar a pasta de destino."""
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_destino.set(pasta)

    def abrir_pasta(self):
        """Abre a pasta de destino no explorador de arquivos."""
        pasta = self.pasta_destino.get()
        if pasta and os.path.isdir(pasta):
            os.startfile(pasta) if os.name == 'nt' else os.system(f'xdg-open "{pasta}"')
        else:
            messagebox.showerror("Erro", "Pasta inválida ou não selecionada.")

    def iniciar_monitoramento(self):
        """Inicia o monitoramento para download."""
        pasta = self.pasta_destino.get()
        prefixo = self.prefixo_nome.get()

        if not os.path.isdir(pasta):
          messagebox.showerror("Erro", "Selecione uma pasta válida")
          return

        if not re.fullmatch(r"^[a-zA-Z0-9_-]+$", prefixo):
          messagebox.showerror("Erro", "Nome do arquivo inválido. Use apenas letras, números, _ ou -.")
          return

        if self.monitorando[0]:
            messagebox.showinfo("Aviso", "O monitoramento já está em execução.")
            return

        self.monitorando = [True]
        self.botao_iniciar.config(text="▶️ Monitorando...", state=tk.DISABLED)
        self.botao_parar.config(state=tk.NORMAL)

        self.thread_monitoramento = threading.Thread(target=self.executar_download_thread, args=(pasta, prefixo, self.monitorando))
        self.thread_monitoramento.daemon = True
        self.thread_monitoramento.start()

    def executar_download_thread(self, pasta, prefixo, monitorando):
        """
        Executa o download em uma thread separada.
        
        Args:
            pasta (str): Pasta de destino
            prefixo (str): Prefixo do nome do arquivo
            monitorando (list): Lista com um booleano para controlar o monitoramento
        """
        terminou_por_tempo = [False]
        downloader.executar_download(pasta, prefixo, terminou_por_tempo, monitorando)
        self.monitorando[0] = False
        self.botao_iniciar.config(text="▶️ Iniciar", state=tk.NORMAL)
        self.botao_parar.config(state=tk.DISABLED)

        if terminou_por_tempo[0]:
            messagebox.showinfo("Aviso", "Tempo limite atingido (20:58). O processo será encerrado até o próximo dia útil.")

    def parar_monitoramento(self):
        """Para o monitoramento."""
        if self.monitorando[0]:
            print("Parando o monitoramento...")
            self.monitorando[0] = False
            self.botao_parar.config(state=tk.DISABLED)
            self.botao_iniciar.config(state=tk.NORMAL, text="▶️ Iniciar")

    def load_config(self):
        """Carrega as configurações do arquivo."""
        try:
            with open(self.config_file, "r") as f:
                for line in f:
                    key, value = line.strip().split("=")
                    if key == "pasta_destino":
                        self.pasta_destino.set(value)
                    elif key == "prefixo_nome":
                        if value:
                            self.prefixo_nome.set(value)
                        else:
                            self.prefixo_nome.set(downloader.PREFIXO_PADRAO)
        except FileNotFoundError:
            print("Arquivo de configuração não encontrado. Usando valores padrão.")
        except ValueError:
            print("Arquivo de configuração corrompido. Usando valores padrão.")

    def save_config(self):
        """Salva as configurações no arquivo."""
        with open(self.config_file, "w") as f:
            f.write(f"pasta_destino={self.pasta_destino.get()}\n")
            f.write(f"prefixo_nome={self.prefixo_nome.get()}\n")

    def on_closing(self):
        """Manipulador para o evento de fechamento da janela."""
        self.save_config()
        self.root.destroy()


def main():
    """Função principal para iniciar a aplicação."""
    root = tk.Tk()
    app = Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
