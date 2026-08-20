#!/bin/bash
green='\033[0;32m'
yellow='\033[0;33m'
normal='\033[0m'

echo -e "${yellow}Uninstalling MDCT...${normal}"
rm -rf "$HOME/.local/share/mdct"
rm -f "$HOME/.local/bin/mdct"
echo -e "${green}MDCT uninstalled.${normal}"