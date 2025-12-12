#!/bin/bash

echo "======================================================================"
echo "📦 INSTALLATION - HYPER-BOT"
echo "======================================================================"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✅ Python 3 trouvé: $(python3 --version)"
echo ""

# Créer venv si inexistant
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
else
    echo "✅ Environnement virtuel existant"
fi

echo ""
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

echo ""
echo "📥 Installation des dépendances..."

# Fusionner les requirements
cat > requirements_merged.txt << 'EOF'
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.3.0
eth-account>=0.8.0
hyperliquid-python-sdk>=0.2.0
yfinance>=0.2.28
pytz>=2023.3
lxml>=4.9.0
html5lib>=1.1
EOF

pip install -q --upgrade pip
pip install -q -r requirements_merged.txt

echo "✅ Dépendances installées"

# Créer les dossiers logs si inexistants
echo ""
echo "📁 Création des dossiers..."
mkdir -p crypto-bot/logs
mkdir -p sp500-bot/logs
echo "✅ Dossiers créés"

# Rendre les scripts exécutables
echo ""
echo "🔒 Configuration des permissions..."
chmod +x launch_bots.sh
chmod +x crypto-bot/view_indicators.sh
chmod +x crypto-bot/view_history.sh
chmod +x sp500-bot/view_indicators.sh
chmod +x sp500-bot/view_history.sh
chmod +x sp500-bot/get_sp500_list.py
echo "✅ Permissions configurées"

# Récupérer la liste S&P 500 si nécessaire
if [ ! -f "sp500-bot/sp500_tickers.py" ]; then
    echo ""
    echo "📊 Téléchargement de la liste S&P 500..."
    cd sp500-bot
    python get_sp500_list.py
    cd ..
    echo "✅ Liste S&P 500 téléchargée"
fi

echo ""
echo "======================================================================"
echo "✅ INSTALLATION TERMINÉE"
echo "======================================================================"
echo ""
echo "📊 Structure du projet:"
echo ""
echo "  hyper-bot/"
echo "  ├── crypto-bot/          🔵 Bot Hyperliquid (24/7)"
echo "  │   ├── main.py"
echo "  │   ├── view_indicators.sh"
echo "  │   └── view_history.sh"
echo "  │"
echo "  ├── sp500-bot/           🔴 Bot S&P 500 Day Trading"
echo "  │   ├── main.py"
echo "  │   ├── view_indicators.sh"
echo "  │   └── view_history.sh"
echo "  │"
echo "  └── launch_bots.sh       🚀 Lancer les 2 bots"
echo ""
echo "======================================================================"
echo "🚀 PROCHAINES ÉTAPES:"
echo "======================================================================"
echo ""
echo "  1. Lancer les deux bots:"
echo "     ./launch_bots.sh"
echo ""
echo "  2. Voir les indicateurs (crypto):"
echo "     cd crypto-bot && ./view_indicators.sh"
echo ""
echo "  3. Voir l'historique (S&P 500):"
echo "     cd sp500-bot && ./view_history.sh"
echo ""
echo "======================================================================"

