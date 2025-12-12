#!/bin/bash

echo "======================================================================"
echo "🧹 NETTOYAGE FINAL DU PROJET"
echo "======================================================================"
echo ""
echo "⚠️  Cette opération va supprimer tous les anciens fichiers"
echo "     et ne garder que la nouvelle structure propre."
echo ""
echo "📁 Structure finale :"
echo "   hyper-bot/"
echo "   ├── install.sh"
echo "   ├── launch_bots.sh"
echo "   ├── README.md"
echo "   ├── crypto-bot/"
echo "   ├── sp500-bot/"
echo "   └── venv/"
echo ""
read -p "Voulez-vous continuer ? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Annulé"
    exit 0
fi

echo ""
echo "🗑️  Suppression des anciens fichiers..."

# Liste des fichiers à supprimer
rm -f main.py
rm -f main_sp500.py
rm -f main_sp500_daytrading.py
rm -f ml.py
rm -f requirements.txt
rm -f requirements_sp500.txt
rm -f requirements_merged.txt
rm -f run_bot.sh
rm -f run_sp500_bot.sh
rm -f run_sp500_daytrading.sh
rm -f setup.sh
rm -f hyper-bot.service
rm -f view_indicators.sh
rm -f view_history.sh
rm -f get_sp500_list.py
rm -f sp500_tickers.py
rm -f sp500_tickers.json
rm -f test_sp500.py
rm -f test_simple_sp500.py
rm -f sp500_simulation.db
rm -f trading_simulation.db

# Supprimer les anciens README
rm -f README_OLD.md
rm -f README_SP500.md
rm -f README_DAYTRADING.md
rm -f SP500_DEPLOY.md

# Supprimer les scripts de doc
rm -f CHANGELOG.md
rm -f CLEANUP.sh
rm -f FILES_STRUCTURE.md
rm -f DEPLOY_UPDATE.md
rm -f QUICK_DEPLOY.sh

# Supprimer __pycache__
rm -rf __pycache__

# Renommer le nouveau README
if [ -f README_FINAL.md ]; then
    mv README_FINAL.md README.md
fi

echo "✅ Anciens fichiers supprimés"

echo ""
echo "======================================================================"
echo "✅ NETTOYAGE TERMINÉ"
echo "======================================================================"
echo ""
echo "📂 Structure finale :"
ls -1 | grep -v venv
echo ""
echo "======================================================================"
echo "🚀 PROCHAINES ÉTAPES :"
echo "======================================================================"
echo ""
echo "  1. Tester l'installation :"
echo "     ./install.sh"
echo ""
echo "  2. Lancer les bots :"
echo "     ./launch_bots.sh"
echo ""
echo "  3. Pousser sur GitHub :"
echo "     git add ."
echo "     git commit -m \"Structure finale avec 2 bots organisés\""
echo "     git push origin main"
echo ""
echo "======================================================================"

