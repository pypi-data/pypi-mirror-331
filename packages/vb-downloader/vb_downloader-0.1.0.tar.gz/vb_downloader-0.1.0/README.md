# VB Downloader

Um aplicativo para download automático do programa "A Voz do Brasil" para emissoras de rádio.

## Sobre o Projeto

O VB Downloader foi desenvolvido para automatizar o processo de download diário do programa "A Voz do Brasil", transmitido de segunda a sexta-feira. Este aplicativo é utilizado por várias emissoras de rádio em todo o Brasil para facilitar a retransmissão do programa obrigatório.

## Funcionalidades

- Download automático do programa "A Voz do Brasil" em dias úteis
- Tentativas em múltiplas fontes para garantir o sucesso do download
- Interface gráfica simples e intuitiva
- Personalização da pasta de destino e nome do arquivo
- Monitoramento contínuo com possibilidade de interrupção
- Registro detalhado de operações (logs)

## Requisitos

- Python 3.6 ou superior
- Bibliotecas: requests, tkinter

## Instalação

### 1. Instalar o Python

#### Windows
1. Acesse o site oficial do Python: https://www.python.org/downloads/windows/
2. Baixe a versão mais recente do Python 3 (3.6 ou superior)
3. Execute o instalador e marque a opção "Add Python to PATH"
4. Clique em "Install Now"
5. Verifique a instalação abrindo o Prompt de Comando e digitando:
   ```
   python --version
   ```

#### macOS
1. Acesse o site oficial do Python: https://www.python.org/downloads/macos/
2. Baixe a versão mais recente do Python 3 (3.6 ou superior)
3. Execute o instalador e siga as instruções
4. Verifique a instalação abrindo o Terminal e digitando:
   ```
   python3 --version
   ```

#### Linux (Ubuntu/Debian)
```bash
# Atualize os repositórios
sudo apt update

# Instale o Python e o pip
sudo apt install python3 python3-pip

# Verifique a instalação
python3 --version
```

### 2. Instalar o VB Downloader

#### Método 1: Instalação via pip (Recomendado)

```bash
# Instale diretamente do PyPI
pip install vb-downloader
# Em alguns sistemas pode ser necessário usar pip3 em vez de pip
```

#### Método 2: Instalação a partir do código-fonte

```bash
# Clone o repositório ou baixe os arquivos
git clone https://github.com/seu-usuario/vb-downloader.git
# Ou baixe o ZIP do projeto e extraia

# Entre na pasta do projeto
cd vb-downloader

# Instale o pacote em modo de desenvolvimento
pip install -e .
# Em alguns sistemas pode ser necessário usar pip3 em vez de pip
```

## Como Usar

### Executando o Programa

Após instalar o pacote via pip, você pode executar o programa diretamente do terminal:

```bash
# Execute o comando
vb-downloader
```

Se você instalou a partir do código-fonte, pode executar:

#### Windows
```bash
# Navegue até a pasta do projeto
cd caminho\para\vb-downloader

# Execute o programa
python -m vb_downloader.gui
```

#### macOS/Linux
```bash
# Navegue até a pasta do projeto
cd caminho/para/vb-downloader

# Execute o programa
python3 -m vb_downloader.gui
```

### Utilizando o Aplicativo

1. Após iniciar o aplicativo, você verá a interface gráfica do VB Downloader
2. Clique no botão de pasta (📁) para selecionar a pasta de destino para os arquivos baixados
3. No campo "Nome do Arquivo", defina o nome desejado para o arquivo de áudio (opcional)
4. Clique em "▶️ Iniciar" para começar o monitoramento
5. O programa irá:
   - Verificar se é dia útil (segunda a sexta-feira)
   - Aguardar até às 20:20 para iniciar o download
   - Tentar baixar o programa de duas fontes diferentes
   - Continuar tentando até às 20:58, caso necessário
   - Aguardar até o próximo dia útil após o download ou após o tempo limite
6. Para interromper o monitoramento, clique em "⏹️ Parar"


## Uso em Emissoras de Rádio

Este projeto pode ser utilizado por diversas emissoras de rádio em todo o Brasil para automatizar o download e a retransmissão do programa "A Voz do Brasil", facilitando o cumprimento da obrigatoriedade de transmissão.

## Desenvolvedor

- **Erik Rocha** - e.lucasrocha@gmail.com

## Contribuições

Contribuições são bem-vindas! Se você encontrar bugs ou tiver sugestões de melhorias, por favor abra uma issue ou envie um pull request.
