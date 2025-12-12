# ⚡ QUICKSTART - Déploiement VPS en 3 commandes

## 📋 Sur ton VPS

```bash
# 1. Arrêter l'ancien bot
sudo systemctl stop hyper-bot
sudo systemctl disable hyper-bot

# 2. Pull le nouveau code
cd ~/hyper-bot
git pull origin main

# 3. Tout installer et lancer automatiquement
./vps_setup.sh
```

C'est tout ! 🎉

---

## 📊 Vérifier que ça tourne

**2-3 minutes après :**

```bash
# Logs en direct
tail -f ~/hyper-bot/crypto-bot/logs/bot.log
tail -f ~/hyper-bot/sp500-bot/logs/bot.log

# Statut
sudo systemctl status crypto-bot
sudo systemctl status sp500-bot

# Voir les trades (après quelques heures)
cd ~/hyper-bot/crypto-bot && ./view_indicators.sh
cd ~/hyper-bot/sp500-bot && ./view_indicators.sh
```

---

## 🔧 Gestion quotidienne

```bash
# Redémarrer
sudo systemctl restart crypto-bot sp500-bot

# Arrêter
sudo systemctl stop crypto-bot sp500-bot

# Mettre à jour
cd ~/hyper-bot
git pull origin main
sudo systemctl restart crypto-bot sp500-bot
```

---

## 📁 Structure finale

```
hyper-bot/
├── crypto-bot/              🔵 Bot crypto 24/7
│   ├── main.py
│   ├── trading_simulation.db
│   ├── view_indicators.sh
│   └── logs/
│
├── sp500-bot/               🔴 Bot S&P 500 9h30-16h
│   ├── main.py
│   ├── sp500_daytrading.db
│   ├── view_indicators.sh
│   └── logs/
│
└── venv/                    Environnement Python partagé
```

---

**Les 2 bots sont isolés et n'impactent pas ton bot de scraping !** ✅

