#!/bin/bash

# High Priestess Bot - DigitalOcean Deployment Script
# Run this script on your DigitalOcean droplet

set -e  # Exit on any error

echo "🌙 Deploying High Priestess Bot to DigitalOcean..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor redis-server sqlite3

# Install Docker (optional, for advanced deployment)
print_status "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p /opt/high-priestess
sudo chown $USER:$USER /opt/high-priestess
cd /opt/high-priestess

# Clone repository (you'll need to do this manually or provide GitHub token)
print_status "Repository cloning instructions:"
echo "Run this command to clone your repo:"
echo "git clone https://github.com/GeorgieXRPL/High_Priestess.git ."
echo "Then copy your .env file to this directory"

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python packages..."
pip install --upgrade pip
pip install python-dotenv tweepy openai fastapi uvicorn sqlalchemy redis ephem

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/high-priestess.service > /dev/null <<EOF
[Unit]
Description=High Priestess Oracle Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/high-priestess/high_priestess_bot
Environment=PATH=/opt/high-priestess/venv/bin
ExecStart=/opt/high-priestess/venv/bin/python simple_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create web service for health checks
sudo tee /etc/systemd/system/high-priestess-web.service > /dev/null <<EOF
[Unit]
Description=High Priestess Web Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/high-priestess/high_priestess_bot
Environment=PATH=/opt/high-priestess/venv/bin
ExecStart=/opt/high-priestess/venv/bin/python simple_bot.py web
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx (optional - for web dashboard)
print_status "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/high-priestess > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/high-priestess /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# Enable services
print_status "Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable high-priestess
sudo systemctl enable high-priestess-web
sudo systemctl enable nginx
sudo systemctl enable redis-server

print_success "Deployment setup complete!"
echo ""
echo "🔮 Next Steps:"
echo "1. Clone your repository: git clone https://github.com/GeorgieXRPL/High_Priestess.git ."
echo "2. Copy your .env file to /opt/high-priestess/high_priestess_bot/"
echo "3. Start the services:"
echo "   sudo systemctl start high-priestess"
echo "   sudo systemctl start high-priestess-web"
echo "4. Check status:"
echo "   sudo systemctl status high-priestess"
echo "   curl http://localhost/health"
echo ""
echo "✨ Your High Priestess will then be live 24/7!"
