#!/bin/bash
# mdct-installer.sh v1.0.0

set -euo pipefail

green='\033[0;32m'
red='\033[0;31m'
normal='\033[0m'
yellow='\033[0;33m'

INSTALL_DIR="$HOME/.local/share/mdct"
FRESH_INSTALL=false

cleanup() {
    status=$?
    echo -e "${red}Installation failed with error status $status ${normal}"

    if [[ "$FRESH_INSTALL" == true ]]; then
        rm -rf "$INSTALL_DIR"
    fi
}
trap cleanup ERR


echo -e "Installing MDCT..."


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


if [[ -d "$INSTALL_DIR/.git" ]]; then
    echo -e "${yellow}Existing install found, updating...${normal}"
    git -C "$INSTALL_DIR" pull --ff-only
else
    FRESH_INSTALL=true
    git clone https://github.com/nisyk/mediacontrol-tui.git "$INSTALL_DIR"

fi


cd "$INSTALL_DIR"

python3 -m venv --system-site-packages venv

set +u
source venv/bin/activate
set -u
pip install --upgrade pip # pip biarkan transparan
pip install -r requirements.txt

pip install pyinstaller
rm -rf build/ dist/ *.spec
pyinstaller --onefile --name mdct app.py

mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/dist/mdct" "$HOME/.local/bin/mdct"

# Make uninstaller
cat > "$INSTALL_DIR/mdct-uninstall" << 'EOF'
#!/bin/bash
green='\033[0;32m'
yellow='\033[0;33m'
normal='\033[0m'

echo -e "${yellow}Uninstalling MDCT...${normal}"
rm -rf "$HOME/.local/share/mdct"
rm -f "$HOME/.local/bin/mdct"
echo -e "${green}MDCT uninstalled.${normal}"
EOF
chmod +x "$INSTALL_DIR/mdct-uninstall"


if command -v mdct &> /dev/null; then
    echo -e "${green}Installation completed! Run mdct.${normal}"
    echo -e "To uninstall this program. Run: mdct-uninstall"

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
