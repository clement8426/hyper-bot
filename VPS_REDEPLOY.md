# 🚀 Guide de Redéploiement Complet sur VPS

## 📋 Étape 1 : Arrêter l'ancien bot

```bash
# Se connecter au VPS
ssh votre-user@votre-vps

# Arrêter le service systemd
sudo systemctl stop hyper-bot

# Vérifier qu'il est bien arrêté
sudo systemctl status hyper-bot
```

## 🗑️ Étape 2 : Nettoyer l'ancien déploiement

```bash
# Aller dans le dossier
cd ~/hyper-bot

# Sauvegarder l'ancienne BDD (optionnel)
mkdir -p ~/backup_old_bot
cp -r *.db ~/backup_old_bot/ 2>/dev/null || true
cp -r logs ~/backup_old_bot/ 2>/dev/null || true

# Supprimer les anciennes BDD
rm -f trading_simulation.db sp500_simulation.db

# Supprimer les anciens logs
rm -rf logs

# Désactiver l'ancien service
sudo systemctl disable hyper-bot
sudo rm -f /etc/systemd/system/hyper-bot.service
sudo systemctl daemon-reload
```

## 📥 Étape 3 : Pull le nouveau code

```bash
# Toujours dans ~/hyper-bot
git fetch origin
git reset --hard origin/main
git pull origin main

# Vérifier la nouvelle structure
ls -la
# Tu dois voir : crypto-bot/ sp500-bot/ install.sh launch_bots.sh
```

## 🔧 Étape 4 : Réinstaller

```bash
# Lancer l'installation
./install.sh

# Vérifier que tout est OK
ls crypto-bot/
ls sp500-bot/
```

## 🤖 Étape 5 : Créer les nouveaux services systemd

### Service pour le bot crypto

```bash
sudo nano /etc/systemd/system/crypto-bot.service
```

Coller :

```ini
[Unit]
Description=Crypto Trading Bot (Hyperliquid)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/hyper-bot/crypto-bot
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/ubuntu/hyper-bot/venv/bin/python -u main.py
Restart=always
RestartSec=10

StandardOutput=append:/home/ubuntu/hyper-bot/crypto-bot/logs/bot.log
StandardError=append:/home/ubuntu/hyper-bot/crypto-bot/logs/bot_error.log

[Install]
WantedBy=multi-user.target
```

**⚠️ IMPORTANT : Remplace `ubuntu` par ton vrai nom d'utilisateur VPS !**

### Service pour le bot S&P 500

```bash
sudo nano /etc/systemd/system/sp500-bot.service
```

Coller :

```ini
[Unit]
Description=S&P 500 Day Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/hyper-bot/sp500-bot
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/ubuntu/hyper-bot/venv/bin/python -u main.py
Restart=always
RestartSec=10

StandardOutput=append:/home/ubuntu/hyper-bot/sp500-bot/logs/bot.log
StandardError=append:/home/ubuntu/hyper-bot/sp500-bot/logs/bot_error.log

[Install]
WantedBy=multi-user.target
```

**⚠️ IMPORTANT : Remplace `ubuntu` par ton vrai nom d'utilisateur VPS !**

## 🚀 Étape 6 : Activer et démarrer les bots

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer au démarrage
sudo systemctl enable crypto-bot
sudo systemctl enable sp500-bot

# Démarrer les bots
sudo systemctl start crypto-bot
sudo systemctl start sp500-bot

# Vérifier le statut
sudo systemctl status crypto-bot
sudo systemctl status sp500-bot
```

## 📊 Étape 7 : Vérifier que tout fonctionne

### Logs en temps réel

```bash
# Bot crypto
tail -f ~/hyper-bot/crypto-bot/logs/bot.log

# Bot S&P 500 (dans un autre terminal)
tail -f ~/hyper-bot/sp500-bot/logs/bot.log

# Ou avec journalctl
journalctl -u crypto-bot -f
journalctl -u sp500-bot -f
```

### Vérifier les bases de données

Attendre quelques minutes, puis :

```bash
# Bot crypto
cd ~/hyper-bot/crypto-bot
./view_indicators.sh

# Bot S&P 500
cd ~/hyper-bot/sp500-bot
./view_indicators.sh
```

## 🔧 Commandes de gestion quotidienne

### Redémarrer un bot

```bash
sudo systemctl restart crypto-bot
sudo systemctl restart sp500-bot
```

### Arrêter un bot

```bash
sudo systemctl stop crypto-bot
sudo systemctl stop sp500-bot
```

### Voir les logs

```bash
# Dernières 50 lignes
journalctl -u crypto-bot -n 50
journalctl -u sp500-bot -n 50

# Logs en continu
journalctl -u crypto-bot -f
journalctl -u sp500-bot -f

# Ou directement dans les fichiers
tail -f ~/hyper-bot/crypto-bot/logs/bot.log
tail -f ~/hyper-bot/sp500-bot/logs/bot.log
```

### Mettre à jour le code

```bash
cd ~/hyper-bot
git pull origin main
sudo systemctl restart crypto-bot sp500-bot
```

### Voir l'historique des trades

```bash
# Bot crypto
cd ~/hyper-bot/crypto-bot
./view_history.sh

# Bot S&P 500
cd ~/hyper-bot/sp500-bot
./view_history.sh
```

## ⚠️ Résolution de problèmes

### Bot qui ne démarre pas

```bash
# Vérifier les logs d'erreur
journalctl -u crypto-bot -n 100
journalctl -u sp500-bot -n 100

# Vérifier les permissions
ls -la ~/hyper-bot/crypto-bot/
ls -la ~/hyper-bot/sp500-bot/

# Vérifier que venv fonctionne
source ~/hyper-bot/venv/bin/activate
python --version
pip list
```

### Pas de logs dans les fichiers

```bash
# Vérifier que les dossiers existent
ls -la ~/hyper-bot/crypto-bot/logs/
ls -la ~/hyper-bot/sp500-bot/logs/

# Créer manuellement si besoin
mkdir -p ~/hyper-bot/crypto-bot/logs
mkdir -p ~/hyper-bot/sp500-bot/logs

# Redémarrer
sudo systemctl restart crypto-bot sp500-bot
```

### Base de données corrompue

```bash
# Arrêter le bot
sudo systemctl stop crypto-bot  # ou sp500-bot

# Supprimer la BDD
rm ~/hyper-bot/crypto-bot/trading_simulation.db
# ou
rm ~/hyper-bot/sp500-bot/sp500_daytrading.db

# Redémarrer (elle sera recréée)
sudo systemctl start crypto-bot  # ou sp500-bot
```

## ✅ Checklist finale

- [ ] Ancien bot arrêté
- [ ] Anciennes BDD sauvegardées (optionnel)
- [ ] Nouveau code pullé
- [ ] `install.sh` exécuté
- [ ] Services systemd créés
- [ ] Services activés et démarrés
- [ ] Logs affichent du contenu
- [ ] BDD créées et tables présentes
- [ ] Scripts `view_indicators.sh` fonctionnent

---

## 📊 Après quelques heures/jours

```bash
# Bot crypto - Voir les performances
cd ~/hyper-bot/crypto-bot
./view_history.sh

# Bot S&P 500 - Voir les scans quotidiens
cd ~/hyper-bot/sp500-bot
./view_indicators.sh

# Export CSV pour analyse
sqlite3 ~/hyper-bot/crypto-bot/trading_simulation.db \
  -header -csv "SELECT * FROM trades" > ~/crypto_trades.csv

sqlite3 ~/hyper-bot/sp500-bot/sp500_daytrading.db \
  -header -csv "SELECT * FROM trades" > ~/sp500_trades.csv
```

---

**🎯 Les 2 bots tourneront 24/7 sans impacter ton bot de scraping !**

