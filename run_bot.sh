#!/bin/bash

# Script pour installer les dépendances et lancer le bot de trading
# Usage: ./run_bot.sh

set -e  # Arrête le script en cas d'erreur

VENV_DIR="venv"
PYTHON_CMD="python3"

echo "🚀 Configuration du bot de trading..."
echo ""

# Vérifier que Python 3 est installé
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Erreur: Python 3 n'est pas installé"
    exit 1
fi

# Créer le venv s'il n'existe pas
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Création de l'environnement virtuel..."
    $PYTHON_CMD -m venv $VENV_DIR
    echo "✅ Environnement virtuel créé"
else
    echo "✅ Environnement virtuel existant détecté"
fi

# Activer le venv
echo "🔧 Activation de l'environnement virtuel..."
source $VENV_DIR/bin/activate

# Mettre à jour pip
echo "⬆️  Mise à jour de pip..."
pip install --upgrade pip --quiet

# Installer les dépendances
if [ -f "requirements.txt" ]; then
    echo "📥 Installation des dépendances depuis requirements.txt..."
    pip install -r requirements.txt
    echo "✅ Dépendances installées"
else
    echo "❌ Erreur: requirements.txt non trouvé"
    exit 1
fi

echo ""
echo "======================================================================"
echo "🤖 Lancement du bot..."
echo "======================================================================"
echo ""

# Lancer le bot
python main.py

