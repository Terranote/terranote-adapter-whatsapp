#!/bin/bash
# Production installation script for terranote-adapter-whatsapp
# Usage: ./production-install.sh [install_dir]

set -euo pipefail

# Configuration
INSTALL_DIR="${1:-/opt/terranote-adapter-whatsapp}"
SERVICE_USER="${SERVICE_USER:-terranote}"
APP_NAME="terranote-adapter-whatsapp"
SERVICE_NAME="terranote-adapter-whatsapp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    log_error "This script should not be run as root. Run as user: $SERVICE_USER"
    exit 1
fi

# Check Python version
log_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    log_error "Python 3.11 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

log_info "Python version OK: $(python3 --version)"

# Create installation directory
log_info "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

log_info "Copying project files to $INSTALL_DIR..."
rsync -av --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='*.egg-info' \
    --exclude='.env' \
    "$PROJECT_ROOT/" "$INSTALL_DIR/"

# Create virtual environment
log_info "Creating virtual environment..."
cd "$INSTALL_DIR"
if [ -d ".venv" ]; then
    log_warn "Virtual environment already exists, skipping creation"
else
    python3 -m venv .venv
fi

# Activate virtual environment and install dependencies
log_info "Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -e . --no-dev

# Create .env file if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    log_info "Creating .env file from template..."
    cp "$INSTALL_DIR/env.example" "$INSTALL_DIR/.env"
    log_warn "Please edit $INSTALL_DIR/.env with your production configuration"
else
    log_info ".env file already exists, skipping"
fi

# Create logs directory
log_info "Creating logs directory..."
mkdir -p "$INSTALL_DIR/logs"

# Set permissions
log_info "Setting permissions..."
chmod 600 "$INSTALL_DIR/.env" 2>/dev/null || true
chmod +x "$INSTALL_DIR/.venv/bin/uvicorn" 2>/dev/null || true

log_info "Installation completed successfully!"
log_info ""
log_info "Next steps:"
log_info "1. Edit $INSTALL_DIR/.env with your production configuration"
log_info "2. Copy the systemd service file:"
log_info "   sudo cp $INSTALL_DIR/deploy/terranote-adapter-whatsapp.service /etc/systemd/system/"
log_info "3. Edit the service file to match your installation path if needed"
log_info "4. Enable and start the service:"
log_info "   sudo systemctl daemon-reload"
log_info "   sudo systemctl enable $SERVICE_NAME"
log_info "   sudo systemctl start $SERVICE_NAME"
log_info "5. Check status:"
log_info "   sudo systemctl status $SERVICE_NAME"

