#!/bin/bash
# Setup script to prepare the repository for running as a service
# This script assumes the repository is already in place at /home/terranote/terranote-adapter-whatsapp
# It will set up the virtual environment and install dependencies

set -euo pipefail

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

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

log_info "Setting up terranote-adapter-whatsapp in: $REPO_DIR"

# Check Python version
log_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    log_error "Python 3.11 or higher is required."
    exit 1
fi

log_info "Python version OK: $(python3 --version)"

# Create virtual environment
log_info "Creating virtual environment..."
cd "$REPO_DIR"
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
if [ ! -f "$REPO_DIR/.env" ]; then
    log_info "Creating .env file from template..."
    cp "$REPO_DIR/env.example" "$REPO_DIR/.env"
    log_warn "Please edit $REPO_DIR/.env with your production configuration"
else
    log_info ".env file already exists, skipping"
fi

# Create logs directory
log_info "Creating logs directory..."
mkdir -p "$REPO_DIR/logs"

# Set permissions
log_info "Setting permissions..."
chmod 600 "$REPO_DIR/.env" 2>/dev/null || true
chmod +x "$REPO_DIR/.venv/bin/uvicorn" 2>/dev/null || true

log_info "Setup completed successfully!"
log_info ""
log_info "Next steps:"
log_info "1. Edit $REPO_DIR/.env with your production configuration"
log_info "2. Copy the systemd service file:"
log_info "   sudo cp $REPO_DIR/deploy/terranote-adapter-whatsapp.service /etc/systemd/system/"
log_info "3. Enable and start the service:"
log_info "   sudo systemctl daemon-reload"
log_info "   sudo systemctl enable terranote-adapter-whatsapp"
log_info "   sudo systemctl start terranote-adapter-whatsapp"
log_info "4. Check status:"
log_info "   sudo systemctl status terranote-adapter-whatsapp"

