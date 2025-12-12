#!/bin/bash

echo "======================================================================"
echo "🚀 DÉPLOIEMENT RAPIDE - Version 1.1.0"
echo "======================================================================"
echo ""

# Étape 1 : Commit et push sur GitHub
echo "📦 Étape 1/3 : Push sur GitHub..."
git add .
git commit -m "v1.1.0: Ajout filtres de sécurité anti-contre-tendance"
git push origin main

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du push GitHub"
    exit 1
fi

echo "✅ Push réussi sur GitHub"
echo ""

# Étape 2 : Se connecter au VPS et déployer
echo "🌐 Étape 2/3 : Connexion au VPS..."
echo ""
echo "⚠️  Veuillez exécuter ces commandes sur votre VPS :"
echo ""
echo "---------------------------------------"
echo "cd ~/hyper-bot"
echo "git pull origin main"
echo "chmod +x view_indicators.sh view_history.sh"
echo "sudo systemctl restart hyper-bot"
echo "sleep 10"
echo "sudo systemctl status hyper-bot"
echo "---------------------------------------"
echo ""
echo "📊 Étape 3/3 : Voir les logs en direct"
echo ""
echo "tail -f ~/hyper-bot/logs/bot.log"
echo ""
echo "======================================================================"
echo "✅ Instructions affichées. Connectez-vous maintenant à votre VPS."
echo "======================================================================"

