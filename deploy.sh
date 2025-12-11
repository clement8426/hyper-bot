#!/bin/bash

# Script de déploiement pour VPS
# Ce script installe le bot sans affecter les services existants

set -e

echo "🚀 Déploiement du bot de trading sur le VPS..."
echo

# Variables
BOT_DIR="$HOME/hyper-bot"
REPO_URL="" # À remplir avec votre repo Git ou utiliser SCP

# 1. Créer le dossier du bot
echo "📁 Création du dossier..."
mkdir -p "$BOT_DIR"
cd "$BOT_DIR"

# 2. Vérifier Python 3
echo "🐍 Vérification de Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "Installez-le avec: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

python3 --version

# 3. Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
else
    echo "✅ Environnement virtuel existant"
fi

# 4. Activer et mettre à jour
echo "⬆️  Activation et mise à jour de pip..."
source venv/bin/activate
pip install --upgrade pip

# 5. Installer les dépendances
echo "📥 Installation des dépendances..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dépendances installées"
else
    echo "⚠️  requirements.txt non trouvé - installez-le manuellement"
fi

echo
echo "✅ Installation terminée !"
echo
echo "📋 Prochaines étapes:"
echo "1. Copiez vos fichiers (main.py, requirements.txt, etc.) dans $BOT_DIR"
echo "2. Créez le service systemd avec: sudo nano /etc/systemd/system/hyper-bot.service"
echo "3. Activez le service avec: sudo systemctl enable hyper-bot"
echo "4. Lancez le bot avec: sudo systemctl start hyper-bot"
echo
echo "Voir deploy_guide.md pour plus de détails"

