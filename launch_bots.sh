#!/bin/bash

echo "======================================================================"
echo "🚀 LANCEMENT DES BOTS DE TRADING"
echo "======================================================================"
echo ""

# Vérifier que venv existe
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé"
    echo "   Exécutez d'abord: ./install.sh"
    exit 1
fi

# Activer venv
source venv/bin/activate

echo "Choisissez quel bot lancer:"
echo ""
echo "  1. 🔵 Bot Crypto (Hyperliquid 24/7)"
echo "  2. 🔴 Bot S&P 500 (Day Trading 9h30-16h)"
echo "  3. ⚡ Les deux en parallèle (tmux requis)"
echo "  4. ❌ Annuler"
echo ""
read -p "Votre choix (1-4): " choice

case $choice in
    1)
        echo ""
        echo "======================================================================"
        echo "🔵 LANCEMENT DU BOT CRYPTO"
        echo "======================================================================"
        echo ""
        echo "📊 Informations:"
        echo "   - Plateforme: Hyperliquid"
        echo "   - Actifs: BTC, ETH, SOL, ARB, MATIC"
        echo "   - Horaires: 24/7"
        echo "   - Capital: \$1,000"
        echo "   - Levier: 2x"
        echo "   - Base de données: crypto-bot/trading_simulation.db"
        echo ""
        echo "💡 Pour arrêter: Ctrl+C"
        echo ""
        echo "======================================================================"
        echo ""
        cd crypto-bot
        python main.py
        ;;
    
    2)
        echo ""
        echo "======================================================================"
        echo "🔴 LANCEMENT DU BOT S&P 500 DAY TRADING"
        echo "======================================================================"
        echo ""
        echo "📊 Informations:"
        echo "   - Plateforme: Yahoo Finance"
        echo "   - Actifs: Top 20 du S&P 500 (502 analysés)"
        echo "   - Horaires: 9h30-16h00 (EST)"
        echo "   - Capital: \$10,000"
        echo "   - Levier: 1x (sans levier)"
        echo "   - Stratégie: Opening Range Breakout"
        echo "   - Base de données: sp500-bot/sp500_daytrading.db"
        echo ""
        echo "⏰ Le bot attend automatiquement 9h45 pour scanner"
        echo "💡 Pour arrêter: Ctrl+C"
        echo ""
        echo "======================================================================"
        echo ""
        cd sp500-bot
        python main.py
        ;;
    
    3)
        # Vérifier si tmux est installé
        if ! command -v tmux &> /dev/null; then
            echo ""
            echo "❌ tmux n'est pas installé"
            echo "   Pour lancer les 2 bots en parallèle, installez tmux:"
            echo ""
            echo "   Ubuntu/Debian: sudo apt install tmux"
            echo "   macOS: brew install tmux"
            echo ""
            exit 1
        fi
        
        echo ""
        echo "======================================================================"
        echo "⚡ LANCEMENT DES DEUX BOTS EN PARALLÈLE"
        echo "======================================================================"
        echo ""
        echo "📊 Les bots vont démarrer dans des sessions tmux séparées:"
        echo ""
        echo "   Session 1: crypto-bot"
        echo "   Session 2: sp500-bot"
        echo ""
        echo "Pour voir les bots:"
        echo "   tmux attach -t crypto-bot"
        echo "   tmux attach -t sp500-bot"
        echo ""
        echo "Pour détacher (sortir sans arrêter): Ctrl+B puis D"
        echo "Pour lister les sessions: tmux ls"
        echo ""
        read -p "Appuyez sur Entrée pour continuer..."
        
        # Lancer crypto-bot
        echo ""
        echo "🔵 Lancement du bot crypto..."
        tmux new-session -d -s crypto-bot "cd $(pwd)/crypto-bot && ../venv/bin/python main.py"
        
        # Lancer sp500-bot
        echo "🔴 Lancement du bot S&P 500..."
        tmux new-session -d -s sp500-bot "cd $(pwd)/sp500-bot && ../venv/bin/python main.py"
        
        echo ""
        echo "✅ Les deux bots sont lancés !"
        echo ""
        echo "======================================================================"
        echo "📊 COMMANDES UTILES"
        echo "======================================================================"
        echo ""
        echo "  # Voir le bot crypto"
        echo "  tmux attach -t crypto-bot"
        echo ""
        echo "  # Voir le bot S&P 500"
        echo "  tmux attach -t sp500-bot"
        echo ""
        echo "  # Lister les sessions"
        echo "  tmux ls"
        echo ""
        echo "  # Arrêter un bot"
        echo "  tmux kill-session -t crypto-bot"
        echo "  tmux kill-session -t sp500-bot"
        echo ""
        echo "======================================================================"
        ;;
    
    4)
        echo ""
        echo "❌ Annulé"
        exit 0
        ;;
    
    *)
        echo ""
        echo "❌ Choix invalide"
        exit 1
        ;;
esac

