#!/bin/bash
set -e

### =========================
### CONFIGURATION
### =========================
REPO_URL="https://github.com/RahmadOktaKhoirul/hourmeter.git"
PROJECT_DIR="/home/pi/hourmeter"
VENV_DIR="$PROJECT_DIR/venv"

STATIC_IP="192.168.100.108"
SUBNET="/24"
GATEWAY="192.168.100.1"
DNS="192.168.100.1"
BROKER_IP="192.168.100.107"

CORE_SERVICE="hourmeter.service"
MQTT_SERVICE="hourmeter-slave.service"

echo "======================================"
echo " HOURMETER INDUSTRIAL INSTALLER"
echo "======================================"

### Detect Active Interface
IFACE=$(ip route | grep default | awk '{print $5}')
echo "Detected interface: $IFACE"

CONN_NAME=$(nmcli -t -f NAME,DEVICE connection show --active | grep $IFACE | cut -d: -f1)

if [ -z "$CONN_NAME" ]; then
    echo "❌ Could not detect active connection."
    exit 1
fi

echo "Using connection: $CONN_NAME"

### Backup Network Config
sudo nmcli connection export "$CONN_NAME" "/home/pi/${CONN_NAME}_backup.nmconnection"

### Check IP Conflict
echo "Checking IP conflict for $STATIC_IP ..."
if ping -c 2 $STATIC_IP > /dev/null; then
    echo "❌ IP $STATIC_IP already in use. Abort."
    exit 1
fi

### Update System
sudo apt update -y
sudo apt install -y git python3-venv python3-pip

### Clone or Update Repo
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    git pull
else
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

### Patch Broker IP
sed -i "s/BROKER *= *.*/BROKER = \"$BROKER_IP\"/" slave.py

### Apply Static IP
sudo nmcli connection modify "$CONN_NAME" ipv4.addresses "$STATIC_IP$SUBNET"
sudo nmcli connection modify "$CONN_NAME" ipv4.gateway "$GATEWAY"
sudo nmcli connection modify "$CONN_NAME" ipv4.dns "$DNS"
sudo nmcli connection modify "$CONN_NAME" ipv4.method manual
sudo nmcli connection down "$CONN_NAME"
sudo nmcli connection up "$CONN_NAME"

### Create Virtualenv
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install paho-mqtt
fi
deactivate

### Create Core Service
sudo bash -c "cat > /etc/systemd/system/$CORE_SERVICE" <<EOF
[Unit]
Description=Hourmeter Core Service
After=network-online.target
Wants=network-online.target

[Service]
User=pi
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

### Create MQTT Service
sudo bash -c "cat > /etc/systemd/system/$MQTT_SERVICE" <<EOF
[Unit]
Description=Hourmeter MQTT Forwarder
After=network-online.target
Wants=network-online.target

[Service]
User=pi
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/slave.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

### Enable Services
sudo systemctl daemon-reload
sudo systemctl enable $CORE_SERVICE
sudo systemctl enable $MQTT_SERVICE
sudo systemctl start $CORE_SERVICE
sudo systemctl start $MQTT_SERVICE

### =========================
### HEALTH CHECK SECTION
### =========================
echo ""
echo "========== SYSTEM INFO =========="
echo "IP Address:"
hostname -I

echo ""
echo "Disk Usage:"
df -h /

echo ""
echo "Hourmeter Services:"
systemctl list-unit-files --type=service | grep hourmeter || true

echo ""
echo "Service Status:"
systemctl status $CORE_SERVICE --no-pager || true
systemctl status $MQTT_SERVICE --no-pager || true

echo ""
echo "Failed Services:"
systemctl --failed || true

echo ""
echo "======================================"
echo " INSTALLATION COMPLETE"
echo "======================================"
echo "Reboot recommended."
