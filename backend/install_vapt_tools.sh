# To install use: ./install_vapt_tools.sh
#!/bin/bash

echo "🛠️ Installing VAPT Tools..."

# Update and upgrade system
sudo apt update && sudo apt upgrade -y

# Install essential tools via APT
TOOLS_APT=("nmap" "sqlmap" "nikto" "gobuster" "whatweb" "wpscan" "metasploit-framework")
for tool in "${TOOLS_APT[@]}"; do
    sudo apt install -y "$tool" && echo "✅ $tool installed" || echo "❌ $tool failed"
done

# Install Python dependencies
sudo apt install -y python3-pip git curl

# Install Python-based tools via pip
TOOLS_PIP=("sublist3r" "python3-nmap")
for tool in "${TOOLS_PIP[@]}"; do
    pip3 install "$tool" && echo "✅ $tool installed" || echo "❌ $tool failed"
done

# Verify installations
echo -e "\n🔍 Verifying installations..."
declare -A TOOL_CHECKS=(
    ["Nmap"]="nmap --version | head -n 1"
    ["SQLMap"]="sqlmap --version 2>&1 | head -n 1"
    ["Nikto"]="nikto -Version 2>&1"
    ["Gobuster"]="gobuster -V 2>&1"
    ["WhatWeb"]="whatweb --version 2>&1"
    ["WPScan"]="wpscan --version 2>&1"
    ["Sublist3r"]="sublist3r --version 2>&1 || echo 'Sublist3r Installed'"
    ["Metasploit"]="msfconsole -q -x 'version; exit' 2>/dev/null | head -n 1"
)

FAILED_TOOLS=()

for tool in "${!TOOL_CHECKS[@]}"; do
    OUTPUT=$(eval "${TOOL_CHECKS[$tool]}")
    if [[ -z "$OUTPUT" || "$OUTPUT" == *"command not found"* ]]; then
        echo "❌ $tool installation failed!"
        FAILED_TOOLS+=("$tool")
    else
        echo "✅ $tool installed successfully!"
    fi
done

# Final Summary
echo -e "\n🚀 Installation Summary:"
if [ ${#FAILED_TOOLS[@]} -eq 0 ]; then
    echo "✅ All tools installed successfully!"
else
    echo "❌ The following tools failed to install:"
    printf "   - %s\n" "${FAILED_TOOLS[@]}"
fi
