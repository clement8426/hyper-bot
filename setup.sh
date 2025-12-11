#!/bin/bash

# Script de setup automatique après clonage du repo
# Usage: ./setup.sh

set -e

echo "🚀 Configuration du bot de trading..."
echo

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "Installez-le avec: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

echo "✅ Python 3 trouvé: $(python3 --version)"
echo

# Créer l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
else
    echo "✅ Environnement virtuel existant"
fi

# Activer l'environnement
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Mettre à jour pip
echo "⬆️  Mise à jour de pip..."
pip install --upgrade pip --quiet

# Installer les dépendances
echo "📥 Installation des dépendances..."

# Créer un répertoire temporaire alternatif si /tmp est plein
mkdir -p ~/tmp

# Installer avec TMPDIR personnalisé et sans cache pour économiser l'espace
TMPDIR=~/tmp pip install --no-cache-dir -r requirements.txt --quiet
echo "✅ Dépendances installées"
echo

# Créer le dossier logs
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "✅ Dossier logs créé"
fi

echo
echo "======================================================================"
echo "✅ Installation terminée avec succès !"
echo "======================================================================"
echo
echo "📋 Prochaines étapes:"
echo "1. Configurez les paramètres dans main.py si nécessaire"
echo "2. Lancez le bot avec: ./run_bot.sh"
echo "   ou directement: source venv/bin/activate && python main.py"
echo
echo "Pour le déploiement sur VPS, consultez: deploy_guide.md"
echo

