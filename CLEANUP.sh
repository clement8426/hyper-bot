#!/bin/bash

echo "======================================================================"
echo "🧹 NETTOYAGE DU PROJET"
echo "======================================================================"
echo ""

# Fichiers de documentation à supprimer
FILES_TO_REMOVE=(
    "CHANGELOG.md"
    "DEPLOY_UPDATE.md"
    "QUICK_DEPLOY.sh"
    "deploy_guide.md"
    "deploy.sh"
    "GIT_SETUP.md"
    "ISOLATION_GUIDE.md"
    "QUICK_START.md"
    "TROUBLESHOOTING.md"
)

echo "📋 Fichiers à supprimer :"
for file in "${FILES_TO_REMOVE[@]}"; do
    if [ -f "$file" ]; then
        echo "  - $file"
    fi
done

echo ""
read -p "⚠️  Voulez-vous continuer ? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🗑️  Suppression en cours..."
    
    for file in "${FILES_TO_REMOVE[@]}"; do
        if [ -f "$file" ]; then
            rm "$file"
            echo "  ✅ $file supprimé"
        fi
    done
    
    echo ""
    echo "✅ Nettoyage terminé !"
    echo ""
    echo "📦 Fichiers restants (essentiels) :"
    ls -1 | grep -v "^venv$" | grep -v "^logs$" | grep -v ".db$"
else
    echo ""
    echo "❌ Nettoyage annulé"
fi

echo ""
echo "======================================================================"

