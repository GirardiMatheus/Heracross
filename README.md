# ⚡ HERACROSS ⚡
### Sistema de Informações de Hardware

<div align="center">
  <img src="ui/heracross.png" alt="Heracross Logo" width="128" height="128">
  
  ![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
  ![Platform](https://img.shields.io/badge/Platform-Linux-green.svg)
  ![License](https://img.shields.io/badge/License-MIT-yellow.svg)
  ![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg)
</div>

## 📋 Sobre

**HERACROSS** é um sistema completo de informações de hardware inspirado no poderoso Pokémon Heracross. Esta aplicação oferece uma interface gráfica moderna e temática para visualizar informações detalhadas sobre o hardware do seu sistema Linux.

## ✨ Funcionalidades

### 🖥️ **Interface Gráfica (GUI)**
- **Design temático Heracross** com cores azul e dourado
- **Sistema de abas** organizado e intuitivo
- **Loading animado** durante atualizações
- **Scroll automático** para conteúdo extenso
- **Atualização em tempo real** das informações

### 📊 **Informações Coletadas**
- **🧠 CPU**: Modelo, arquitetura, cores, frequência, cache
- **🧮 Memória**: RAM total, disponível, uso, swap
- **💾 Disco**: Hardware, partições, espaço em disco
- **🔧 Motherboard**: Fabricante, modelo, versão
- **⚙️ BIOS**: Versão, data, fabricante
- **🎮 GPU**: Placas de vídeo e informações gráficas
- **🌐 Rede**: Interfaces, conexões, hardware de rede
- **🔌 USB**: Dispositivos USB conectados
- **💻 Sistema**: OS, kernel, uptime, usuário

### 🖨️ **Interface CLI**
- **Terminal interativo** com Rich formatting
- **Cores e estilos** para melhor legibilidade
- **Exportação** de dados em formato estruturado

## 🚀 Instalação

### Pré-requisitos
- **Python 3.8+**
- **Sistema Linux** (Ubuntu, Debian, Fedora, etc.)
- **Tkinter** (geralmente incluído no Python)

### 1. Clone o repositório
```bash
git clone https://github.com/GirardiMatheus/Heracross.git
cd Heracross
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Instale dependências do sistema (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3-tk python3-pil.imagetk
```

## 🎮 Como Usar

### Interface Gráfica (Recomendado)
```bash
python3 run_gui.py
```

### Interface de Linha de Comando
```bash
# Exibir todas as informações
python3 main.py

# Exibir informações específicas
python3 main.py --cpu
python3 main.py --memory
python3 main.py --disk
python3 main.py --gpu
python3 main.py --network
python3 main.py --usb
python3 main.py --motherboard
python3 main.py --bios
python3 main.py --system

# Combinar múltiplas opções
python3 main.py --cpu --memory --disk
```

### Opções da CLI
- `--cpu`: Informações do processador
- `--memory`: Informações de memória
- `--disk`: Informações de disco
- `--gpu`: Informações da GPU
- `--network`: Informações de rede
- `--usb`: Dispositivos USB
- `--motherboard`: Informações da placa-mãe
- `--bios`: Informações do BIOS
- `--system`: Informações do sistema operacional

## 📁 Estrutura do Projeto

```
Heracross/
├── main.py              # CLI principal
├── run_gui.py           # Launcher da GUI
├── requirements.txt     # Dependências Python
├── README.md           # Este arquivo
├── system_info/        # Módulos de coleta de informações
│   ├── cpu.py          # Informações do CPU
│   ├── memory.py       # Informações de memória
│   ├── disk.py         # Informações de disco
│   ├── gpu.py          # Informações da GPU
│   ├── network.py      # Informações de rede
│   ├── usb.py          # Dispositivos USB
│   ├── motherboard.py  # Placa-mãe e BIOS
│   └── os_info.py      # Sistema operacional
└── ui/                 # Interface do usuário
    ├── gui.py          # Interface gráfica
    ├── cli.py          # Interface CLI
    └── heracross.png   # Logo do Heracross
```

## 🎨 Design e Tema

O **HERACROSS** utiliza um design inspirado no Pokémon Heracross:

### 🎯 **Paleta de Cores**
- **Azul Escuro** (`#1a237e`): Cor principal do fundo
- **Azul Médio** (`#283593`): Containers e elementos
- **Dourado** (`#ffc107`): Destaques e aba selecionada
- **Branco** (`#ffffff`): Texto principal
- **Roxo Claro** (`#b39ddb`): Texto secundário

### ⚡ **Elementos Visuais**
- Logo do Heracross (64x64px) no cabeçalho
- Ícones emoji temáticos nas abas
- Separadores dourados entre seções
- Efeitos hover nas abas
- Loading animado com pontos

## 🔧 Dependências

### Python Packages
```python
rich>=12.0.0      # CLI formatting e cores
psutil>=5.8.0     # Informações do sistema
tk                # Interface gráfica
argparse          # Parsing de argumentos CLI
pillow>=8.0.0     # Processamento de imagens
```

### Ferramentas do Sistema
- `lscpu` - Informações do CPU
- `lshw` - Hardware information
- `lsusb` - Dispositivos USB
- `dmidecode` - BIOS e motherboard
- `df` - Espaço em disco
- `free` - Informações de memória

## 🤝 Contribuindo

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feat/nova-feature`)
3. **Commit** suas mudanças (`git commit -m 'feat: adiciona nova feature'`)
4. **Push** para a branch (`git push origin feat/nova-feature`)
5. Abra um **Pull Request**

### 📝 Padrão de Commits
Utilizamos [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação
- `refactor:` - Refatoração
- `test:` - Testes
- `chore:` - Tarefas de manutenção

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Matheus Girardi**
- GitHub: [@GirardiMatheus](https://github.com/GirardiMatheus)
- Email: [girardimatheus27@gmail.com](mailto:girardimatheus27@gmail.com)

## 🐛 Suporte

Encontrou um bug ou tem uma sugestão? 
- Abra uma [Issue](https://github.com/GirardiMatheus/Heracross/issues)
- Entre em contato através do email

---

<div align="center">
  <strong>⚡ Powered by Heracross ⚡</strong><br>
  <em>Sistema de Informações de Hardware</em>
</div>