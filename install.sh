#!/bin/bash
# mdct-installer.sh v0.1.1

set -eu

green='\033[0;32m'
red='\033[0;31m'
normal='\033[0m'
yellow='\033[0;33m'

INSTALL_DIR="$HOME/.local/share/mdct"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRESH_INSTALL=false


# Removes the installation if error occurred
cleanup() {
    status=$?
    echo -e "${red}Installation failed with error status $status ${normal}"

    if [[ "$FRESH_INSTALL" == true ]]; then
        rm -rf "$INSTALL_DIR"
    fi
}
trap cleanup ERR



echo -e "Installing MDCT..."

# Checking dependencies
if ! command -v python3 &> /dev/null; then
    echo -e "${red}ERROR: Python3 isn't installed.${normal}"


    if grep -qi "ubuntu\|debian" /etc/os-release 2>/dev/null; then
        echo -e "${yellow}Run: sudo apt install python3 python3-pip python3-venv${normal}"
    elif grep -qi "fedora\|rhel\|centos" /etc/os-release 2>/dev/null; then
        echo -e "${yellow}Run: sudo dnf install python3 python3-pip${normal}"
    elif grep -qi "arch\|manjaro\|cachyos" /etc/os-release 2>/dev/null; then
        echo -e "${yellow}Run: sudo pacman -S python python-pip${normal}"
    fi

    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${red}ERROR: git isn't installed.${normal}"

    if grep -qi "ubuntu\|debian" /etc/os-release 2>/dev/null; then
        echo -e "${yellow}Run: sudo apt install git${normal}"
    elif grep -qi "fedora\|rhel\|centos" /etc/os-release 2>/dev/null; then
        echo -e "${yellow}Run: sudo dnf install git${normal}"
    elif grep -qi "arch\|manjaro\|cachyos" /etc/os-release 2>/dev/null; then
        echo -e "${yellow}Run: sudo pacman -S git${normal}"
    fi

    exit 1

fi

if ! python3 -m venv --help &> /dev/null; then
    echo -e "${red}ERROR: python-venv isn't installed.${normal}"
    if grep -qi "ubuntu\|debian" /etc/os-release 2>/dev/null; then
        echo -e "${yellow}Run: sudo apt install python3-venv${normal}"
    fi

    exit 1
fi


if ! python3 -c "import dbus" &>/dev/null; then
    echo -e "${red}ERROR: python3-dbus is not installed.${normal}"

    if grep -qi "ubuntu\|debian" /etc/os-release 2>/dev/null; then
        echo -e "${yellow}Run: sudo apt install python3-dbus${normal}"
    elif grep -qi "fedora\|rhel\|centos" /etc/os-release 2>/dev/null; then
        echo -e "${yellow}Run: sudo dnf install python3-dbus${normal}"
    elif grep -qi "arch\|manjaro\|cachyos" /etc/os-release 2>/dev/null; then
        echo -e "${yellow}Run: sudo pacman -S python-dbus${normal}"
    fi

    exit 1
fi

# Checking if the installation directory is installed
if [[ -d "$INSTALL_DIR" ]]; then
  echo -e "${yellow}Existing install found, updating...${normal}"
  find "$INSTALL_DIR" -mindepth 1 -maxdepth 1 ! -name ".venv" -exec rm -rf {} +

else
  FRESH_INSTALL=true
  mkdir -p "$INSTALL_DIR"
fi

(cd "$SCRIPT_DIR" && tar -c --exclude='.git' --exclude='.idea' --exclude='.gitignore' .) | (cd "$INSTALL_DIR" && tar -x)

cd "$INSTALL_DIR"

if [[ ! -d ".venv" ]]; then
    python3 -m venv --system-site-packages .venv
fi

set +u
source .venv/bin/activate
set -u
pip install --upgrade pip
pip install -r requirements.txt

pip install pyinstaller

pyinstaller --onefile --name mdct app.py

mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/dist/mdct" "$HOME/.local/bin/mdct"

chmod +x "uninstall.sh"

if ! "$INSTALL_DIR/dist/mdct" --version &>/dev/null; then
    echo -e "${red}ERROR: Compiled binary failed to execute.${normal}"
    exit 1
fi

if command -v mdct &> /dev/null; then
    echo -e "${green}Installation completed! Run mdct.${normal}"

else

    if  [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo -e "${yellow}~/.local/bin not in PATH${normal}"
        if [[ "$SHELL" == *"bash"* ]] && [[ -w "$HOME/.bashrc" ]]; then
            if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" 2>/dev/null; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
                echo -e "${green}Added to ~/.bashrc. Please reset your terminal.${normal}"
            fi
        elif [[ "$SHELL" == *"zsh"* ]] && [[ -w "$HOME/.zshrc" ]]; then
            if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.zshrc" 2>/dev/null; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
                echo -e "${green}Added to ~/.zshrc. Please reset your terminal.${normal}"
            fi
        elif [[ "$SHELL" == *"fish"* ]]; then
            mkdir -p "$HOME/.config/fish/"
            if ! grep -q 'set -gx PATH $HOME/.local/bin $PATH' "$HOME/.config/fish/config.fish" 2>/dev/null; then
                echo 'set -gx PATH $HOME/.local/bin $PATH' >> "$HOME/.config/fish/config.fish"
                echo -e "${green}Added to ~/.config/fish/config.fish. Please reset your terminal.${normal}"
            fi
        else
            echo -e "${yellow}Add this to your shell config manually:${normal}"
            echo 'export PATH="$HOME/.local/bin:$PATH"'
            echo 'set -gx PATH $HOME/.local/bin $PATH'
        fi
    fi
fi
