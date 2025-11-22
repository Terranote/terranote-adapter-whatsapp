#!/bin/bash
# Quick setup script for production server
# This script assumes:
# - You have SSH access with a user that has sudo (not terranote)
# - The repository is at /home/terranote/terranote-adapter-whatsapp
# - The service will run as user 'terranote' from the repository location

set -euo pipefail

REPO_DIR="/home/terranote/terranote-adapter-whatsapp"
SERVICE_USER="terranote"

echo "=== Terranote WhatsApp Adapter - Production Setup ==="
echo ""
echo "This script will:"
echo "1. Set up the adapter in place at $REPO_DIR"
echo "2. Configure it to run as user: $SERVICE_USER"
echo "3. Set up systemd service"
echo ""

# Check if running with sudo
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run with sudo"
    echo "Usage: sudo ./install-on-server.sh"
    exit 1
fi

# Check if repository exists
if [ ! -d "$REPO_DIR" ]; then
    echo "Error: Repository not found at $REPO_DIR"
    echo "Please ensure the repository is at that location"
    exit 1
fi

# Check if terranote user exists
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Error: User $SERVICE_USER does not exist"
    exit 1
fi

echo "Step 1: Setting up virtual environment and dependencies as user $SERVICE_USER..."
cd "$REPO_DIR"
chmod +x deploy/setup-local.sh
sudo -u "$SERVICE_USER" ./deploy/setup-local.sh

echo ""
echo "Step 2: Setting ownership..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$REPO_DIR"

echo ""
echo "Step 3: Installing systemd service..."
cp "$REPO_DIR/deploy/terranote-adapter-whatsapp.service" /etc/systemd/system/
systemctl daemon-reload

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit the .env file:"
echo "   sudo nano $REPO_DIR/.env"
echo ""
echo "2. Make sure to set:"
echo "   - WHATSAPP_ACCESS_TOKEN"
echo "   - WHATSAPP_PHONE_NUMBER_ID"
echo "   - WHATSAPP_VERIFY_TOKEN"
echo "   - CORE_API_BASE_URL"
echo ""
echo "3. Set proper permissions:"
echo "   sudo chmod 600 $REPO_DIR/.env"
echo "   sudo chown $SERVICE_USER:$SERVICE_USER $REPO_DIR/.env"
echo ""
echo "4. Enable and start the service:"
echo "   sudo systemctl enable terranote-adapter-whatsapp"
echo "   sudo systemctl start terranote-adapter-whatsapp"
echo ""
echo "5. Check status:"
echo "   sudo systemctl status terranote-adapter-whatsapp"
echo ""

