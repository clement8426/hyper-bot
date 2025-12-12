#!/bin/bash

echo "======================================================================"
echo "🚀 CONFIGURATION AUTOMATIQUE VPS - HYPER-BOT"
echo "======================================================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Détecter l'utilisateur
CURRENT_USER=$(whoami)
CURRENT_HOME=$HOME
PROJECT_DIR="$CURRENT_HOME/hyper-bot"

echo "👤 Utilisateur détecté: $CURRENT_USER"
echo "📁 Dossier projet: $PROJECT_DIR"
echo ""

# Vérifier qu'on est dans le bon dossier
if [ ! -f "install.sh" ]; then
    echo -e "${RED}❌ Erreur: Exécutez ce script depuis le dossier hyper-bot${NC}"
    exit 1
fi

# Étape 1: Arrêter l'ancien service
echo "======================================================================"
echo "🛑 Étape 1/6 : Arrêter l'ancien service"
echo "======================================================================"
echo ""

if systemctl is-active --quiet hyper-bot; then
    echo "Arrêt de l'ancien service hyper-bot..."
    sudo systemctl stop hyper-bot
    sudo systemctl disable hyper-bot 2>/dev/null || true
    sudo rm -f /etc/systemd/system/hyper-bot.service
    sudo systemctl daemon-reload
    echo -e "${GREEN}✅ Ancien service arrêté${NC}"
else
    echo "ℹ️  Aucun ancien service à arrêter"
fi

echo ""

# Étape 2: Sauvegarder les anciennes données
echo "======================================================================"
echo "💾 Étape 2/6 : Sauvegarder les anciennes données"
echo "======================================================================"
echo ""

if [ -f "trading_simulation.db" ] || [ -f "sp500_simulation.db" ]; then
    BACKUP_DIR="$CURRENT_HOME/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    [ -f "trading_simulation.db" ] && cp trading_simulation.db "$BACKUP_DIR/"
    [ -f "sp500_simulation.db" ] && cp sp500_simulation.db "$BACKUP_DIR/"
    [ -d "logs" ] && cp -r logs "$BACKUP_DIR/"
    
    echo -e "${GREEN}✅ Données sauvegardées dans: $BACKUP_DIR${NC}"
else
    echo "ℹ️  Aucune ancienne donnée à sauvegarder"
fi

echo ""

# Étape 3: Nettoyer
echo "======================================================================"
echo "🗑️  Étape 3/6 : Nettoyer les anciennes données"
echo "======================================================================"
echo ""

rm -f trading_simulation.db sp500_simulation.db
rm -rf logs
echo -e "${GREEN}✅ Nettoyage terminé${NC}"

echo ""

# Étape 4: Installer
echo "======================================================================"
echo "📦 Étape 4/6 : Installation des dépendances"
echo "======================================================================"
echo ""

./install.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors de l'installation${NC}"
    exit 1
fi

echo ""

# Étape 5: Créer les services systemd
echo "======================================================================"
echo "🤖 Étape 5/6 : Configuration des services systemd"
echo "======================================================================"
echo ""

# Service crypto-bot
echo "Création du service crypto-bot..."
sudo tee /etc/systemd/system/crypto-bot.service > /dev/null <<EOF
[Unit]
Description=Crypto Trading Bot (Hyperliquid)
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR/crypto-bot
Environment="PYTHONUNBUFFERED=1"
ExecStart=$PROJECT_DIR/venv/bin/python -u main.py
Restart=always
RestartSec=10

StandardOutput=append:$PROJECT_DIR/crypto-bot/logs/bot.log
StandardError=append:$PROJECT_DIR/crypto-bot/logs/bot_error.log

[Install]
WantedBy=multi-user.target
EOF

# Service sp500-bot
echo "Création du service sp500-bot..."
sudo tee /etc/systemd/system/sp500-bot.service > /dev/null <<EOF
[Unit]
Description=S&P 500 Day Trading Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR/sp500-bot
Environment="PYTHONUNBUFFERED=1"
ExecStart=$PROJECT_DIR/venv/bin/python -u main.py
Restart=always
RestartSec=10

StandardOutput=append:$PROJECT_DIR/sp500-bot/logs/bot.log
StandardError=append:$PROJECT_DIR/sp500-bot/logs/bot_error.log

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Services créés${NC}"

echo ""

# Étape 6: Activer et démarrer
echo "======================================================================"
echo "🚀 Étape 6/6 : Démarrage des bots"
echo "======================================================================"
echo ""

# Recharger systemd
sudo systemctl daemon-reload

# Activer
sudo systemctl enable crypto-bot sp500-bot

# Démarrer
sudo systemctl start crypto-bot
sleep 2
sudo systemctl start sp500-bot

echo -e "${GREEN}✅ Bots démarrés${NC}"

echo ""

# Vérifier le statut
echo "======================================================================"
echo "📊 Statut des services"
echo "======================================================================"
echo ""

echo "🔵 Bot Crypto:"
sudo systemctl is-active crypto-bot && echo -e "${GREEN}✅ Actif${NC}" || echo -e "${RED}❌ Inactif${NC}"

echo ""
echo "🔴 Bot S&P 500:"
sudo systemctl is-active sp500-bot && echo -e "${GREEN}✅ Actif${NC}" || echo -e "${RED}❌ Inactif${NC}"

echo ""
echo "======================================================================"
echo "✅ INSTALLATION TERMINÉE"
echo "======================================================================"
echo ""
echo "📊 Commandes utiles:"
echo ""
echo "  # Voir les logs en direct"
echo "  tail -f $PROJECT_DIR/crypto-bot/logs/bot.log"
echo "  tail -f $PROJECT_DIR/sp500-bot/logs/bot.log"
echo ""
echo "  # Voir le statut"
echo "  sudo systemctl status crypto-bot"
echo "  sudo systemctl status sp500-bot"
echo ""
echo "  # Redémarrer un bot"
echo "  sudo systemctl restart crypto-bot"
echo "  sudo systemctl restart sp500-bot"
echo ""
echo "  # Voir les indicateurs (après quelques minutes)"
echo "  cd $PROJECT_DIR/crypto-bot && ./view_indicators.sh"
echo "  cd $PROJECT_DIR/sp500-bot && ./view_indicators.sh"
echo ""
echo "======================================================================"
echo ""
echo -e "${YELLOW}⏳ Attends 2-3 minutes puis vérifie les logs pour confirmer${NC}"
echo ""

