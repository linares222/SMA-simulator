#!/bin/bash
#
# Script para executar o CLI interativo do Simulador Multi-Agente
# Ativa automaticamente o ambiente virtual antes de executar
#

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Diretorio do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Nome do ambiente virtual (pode ser venv, .venv, env, etc.)
VENV_DIRS=(".env-aa" "venv" ".venv" "env" ".env")
VENV_PATH=""

# Procurar ambiente virtual
for dir in "${VENV_DIRS[@]}"; do
    if [ -d "$SCRIPT_DIR/$dir" ]; then
        VENV_PATH="$SCRIPT_DIR/$dir"
        break
    fi
done

# Se nao encontrou, criar um novo
if [ -z "$VENV_PATH" ]; then
    echo -e "${YELLOW}[!] Ambiente virtual nao encontrado. A criar...${NC}"
    python3 -m venv venv
    VENV_PATH="$SCRIPT_DIR/venv"
    echo -e "${GREEN}[OK] Ambiente virtual criado em: $VENV_PATH${NC}"
fi

# Ativar ambiente virtual
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}[OK] Ambiente virtual ativado: $VENV_PATH${NC}"
elif [ -f "$VENV_PATH/Scripts/activate" ]; then
    # Windows Git Bash
    source "$VENV_PATH/Scripts/activate"
    echo -e "${GREEN}[OK] Ambiente virtual ativado: $VENV_PATH${NC}"
else
    echo -e "${RED}[ERRO] Nao foi possivel encontrar o script de ativacao do venv${NC}"
    exit 1
fi

# Verificar se as dependencias estao instaladas
if ! python -c "import questionary" 2>/dev/null; then
    echo -e "${YELLOW}[...] A instalar dependencias...${NC}"
    pip install -q -r requirements.txt
    echo -e "${GREEN}[OK] Dependencias instaladas!${NC}"
fi

# Executar o CLI
echo ""
python -m sma.cli
