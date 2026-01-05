#!/bin/bash
# Configuración de Antigravity para Sentinel TUI
# Este script te ayuda a configurar el proveedor de IA

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🤖 Configuración de Proveedor de IA - Sentinel TUI${NC}\n"

# Función para configurar Ollama (local)
configure_ollama() {
    echo -e "${GREEN}✅ Configurando Ollama (Local)${NC}"
    
    # Verificar que Ollama esté corriendo
    if systemctl is-active --quiet ollama; then
        echo -e "${GREEN}✓ Ollama está corriendo${NC}"
    else
        echo -e "${RED}✗ Ollama no está corriendo${NC}"
        echo -e "${YELLOW}   Inicia con: sudo systemctl start ollama${NC}"
        return 1
    fi
    
    # Verificar modelos disponibles
    echo -e "\n${BLUE}Modelos disponibles:${NC}"
    ollama list
    
    # Exportar variables
    export SENTINEL_AI_PROVIDER="ollama"
    
    echo -e "\n${GREEN}✅ Configuración completa${NC}"
    echo -e "${BLUE}Para hacerla permanente, agrega a ~/.bashrc:${NC}"
    echo -e "${YELLOW}export SENTINEL_AI_PROVIDER=\"ollama\"${NC}"
}

# Función para configurar Antigravity
configure_antigravity() {
    echo -e "${GREEN}Configurando Antigravity (Google Gemini)${NC}\n"
    
    echo -e "${YELLOW}Necesitas una API Key de Google AI Studio${NC}"
    echo -e "${BLUE}Obtén una en: https://makersuite.google.com/app/apikey${NC}\n"
    
    read -p "¿Ya tienes una API Key? (s/n): " has_key
    
    if [[ "$has_key" != "s" ]]; then
        echo -e "\n${YELLOW}Pasos para obtener tu API Key:${NC}"
        echo "1. Ve a https://makersuite.google.com/app/apikey"
        echo "2. Inicia sesión con tu cuenta de Google"
        echo "3. Haz clic en 'Create API Key'"
        echo "4. Copia la key generada"
        echo ""
        echo -e "${BLUE}Cuando tengas tu key, ejecuta este script de nuevo${NC}"
        return 1
    fi
    
    echo ""
    read -sp "Pega tu API Key aquí: " api_key
    echo ""
    
    if [[ -z "$api_key" ]]; then
        echo -e "${RED}✗ API Key vacía${NC}"
        return 1
    fi
    
    # Verificar que la key funciona
    echo -e "\n${BLUE}Verificando API Key...${NC}"
    response=$(curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$api_key" 2>&1)
    
    if echo "$response" | grep -q "error"; then
        echo -e "${RED}✗ API Key inválida${NC}"
        echo "$response" | head -5
        return 1
    fi
    
    echo -e "${GREEN}✓ API Key válida${NC}"
    
    # Seleccionar modelo
    echo -e "\n${BLUE}Modelos disponibles:${NC}"
    echo "1) gemini-1.5-flash (Rápido, recomendado)"
    echo "2) gemini-1.5-pro (Más capaz)"
    echo "3) gemini-pro (Balanceado)"
    
    read -p "Selecciona modelo (1-3) [1]: " model_choice
    model_choice=${model_choice:-1}
    
    case $model_choice in
        1) model="gemini-1.5-flash" ;;
        2) model="gemini-1.5-pro" ;;
        3) model="gemini-pro" ;;
        *) model="gemini-1.5-flash" ;;
    esac
    
    # Exportar variables
    export SENTINEL_AI_PROVIDER="antigravity"
    export GOOGLE_AI_API_KEY="$api_key"
    export ANTIGRAVITY_MODEL="$model"
    
    echo -e "\n${GREEN}✅ Configuración completa${NC}"
    echo -e "${BLUE}Modelo seleccionado: $model${NC}"
    
    # Guardar en archivo de configuración
    config_file="$HOME/.sentinel_ai_config"
    cat > "$config_file" << EOF
# Sentinel AI Provider Configuration
# Generado: $(date)
export SENTINEL_AI_PROVIDER="antigravity"
export GOOGLE_AI_API_KEY="$api_key"
export ANTIGRAVITY_MODEL="$model"
EOF
    
    chmod 600 "$config_file"
    
    echo -e "\n${BLUE}Configuración guardada en: $config_file${NC}"
    echo -e "${YELLOW}Para hacerla permanente, agrega a ~/.bashrc:${NC}"
    echo -e "${YELLOW}source $config_file${NC}"
}

# Menú principal
echo "Selecciona proveedor de IA:"
echo "1) Ollama (Local, privado, GPU)"
echo "2) Antigravity (Google Gemini, cloud, más inteligente)"
echo ""
read -p "Opción (1-2): " choice

case $choice in
    1)
        configure_ollama
        ;;
    2)
        configure_antigravity
        ;;
    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}🎉 ¡Listo!${NC}"
echo -e "${BLUE}Ahora puedes ejecutar:${NC}"
echo -e "${YELLOW}./sentinel_tui.py${NC}"
