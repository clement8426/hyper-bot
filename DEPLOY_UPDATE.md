# 🚀 Déployer la mise à jour v1.1.0 sur le VPS

## Étape 1 : Pousser sur GitHub (depuis votre machine locale)

```bash
# Ajouter tous les fichiers modifiés
git add main.py CHANGELOG.md DEPLOY_UPDATE.md view_indicators.sh view_history.sh

# Commit avec message descriptif
git commit -m "v1.1.0: Ajout filtres de sécurité anti-contre-tendance

- Filtres LONG: refuse si RSI>70 ou tendance baissière
- Filtres SHORT: refuse si RSI<30 ou tendance haussière
- Affichage des raisons de filtrage dans les logs
- Scripts d'analyse des indicateurs (view_indicators.sh, view_history.sh)"

# Push sur GitHub
git push origin main
```

---

## Étape 2 : Déployer sur le VPS

Connectez-vous à votre VPS puis exécutez :

```bash
# Se connecter au VPS
ssh ubuntu@votre-vps-ip

# Aller dans le répertoire du bot
cd ~/hyper-bot

# Récupérer les dernières modifications
git pull origin main

# Rendre les nouveaux scripts exécutables
chmod +x view_indicators.sh view_history.sh

# Redémarrer le bot avec la nouvelle version
sudo systemctl restart hyper-bot

# Attendre 10 secondes pour le démarrage
sleep 10

# Vérifier que le bot tourne
sudo systemctl status hyper-bot

# Voir les logs en temps réel pour vérifier les filtres
tail -f ~/hyper-bot/logs/bot.log
```

---

## Étape 3 : Vérifier que les filtres fonctionnent

Dans les logs, vous devriez maintenant voir des messages comme :

```
⚪ ETH: $3234.10 | RSI:74.8 | Bull:⏳3/7 | Bear:✅5/7 | Signal: AUCUN ⚠️ SHORT filtré (tendance haussière)
🟢 BTC: $92025.00 | RSI:45.2 | Bull:✅5/7 | Bear:⏳2/7 | Signal: LONG
```

✅ Les signaux dangereux sont maintenant **filtrés automatiquement** !

---

## Commandes utiles après déploiement

```bash
# Voir les logs en direct
tail -f ~/hyper-bot/logs/bot.log

# Voir l'historique des trades avec tous les indicateurs
./view_indicators.sh

# Voir le résumé depuis hier
./view_history.sh

# Arrêter le bot
sudo systemctl stop hyper-bot

# Redémarrer le bot
sudo systemctl restart hyper-bot

# Voir le statut
sudo systemctl status hyper-bot
```

---

## 🎉 C'est tout !

Votre bot est maintenant plus intelligent et évite les trades à contre-tendance.

