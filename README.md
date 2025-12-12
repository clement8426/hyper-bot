# 🤖 Hyper-Bot - Bots de Trading Automatisés

Deux bots de trading avec 30+ indicateurs techniques et filtres de sécurité intelligents.

## 📦 Structure du projet

```
hyper-bot/
├── install.sh              # Installation unique
├── launch_bots.sh          # Lancer les bots
├── README.md              # Ce fichier
│
├── crypto-bot/             # 🔵 Bot Hyperliquid (24/7)
│   ├── main.py
│   ├── view_indicators.sh
│   ├── view_history.sh
│   ├── trading_simulation.db
│   └── logs/
│
├── sp500-bot/              # 🔴 Bot S&P 500 Day Trading
│   ├── main.py
│   ├── sp500_tickers.py
│   ├── get_sp500_list.py
│   ├── view_indicators.sh
│   ├── view_history.sh
│   ├── sp500_daytrading.db
│   └── logs/
│
└── venv/                   # Environnement virtuel partagé
```

---

## 🚀 Installation rapide

```bash
# 1. Cloner le repo
git clone https://github.com/votre-username/hyper-bot.git
cd hyper-bot

# 2. Installer
./install.sh

# 3. Lancer les bots
./launch_bots.sh
```

---

## 🤖 Les deux bots

### 🔵 Bot Crypto (Hyperliquid)

| Caractéristique | Valeur |
|----------------|--------|
| **Plateforme** | Hyperliquid API |
| **Actifs** | BTC, ETH, SOL, ARB, MATIC |
| **Horaires** | 24/7 |
| **Capital** | $1,000 |
| **Levier** | 2x |
| **Risque** | 1% par trade |
| **Durée trades** | 5 min - 2h |
| **Base de données** | `crypto-bot/trading_simulation.db` |

**Stratégie** : Multi-indicateurs avec filtres anti-contre-tendance

---

### 🔴 Bot S&P 500 Day Trading

| Caractéristique | Valeur |
|----------------|--------|
| **Plateforme** | Yahoo Finance |
| **Actifs** | Top 20 / 502 analysés |
| **Horaires** | 9h30-16h00 EST (Lun-Ven) |
| **Capital** | $10,000 |
| **Levier** | 1x (sans levier) |
| **Stratégie** | Opening Range Breakout |
| **Scan** | 9h45 (analyse 15 premières min) |
| **Base de données** | `sp500-bot/sp500_daytrading.db` |

**Stratégie** : Notation des gaps/volume/momentum à l'ouverture

---

## 📊 Analyse des données

### Bot Crypto

```bash
cd crypto-bot

# Voir les indicateurs des trades
./view_indicators.sh

# Voir l'historique complet
./view_history.sh

# Requête SQL custom
sqlite3 trading_simulation.db "SELECT * FROM trades WHERE status='CLOSED'"
```

### Bot S&P 500

```bash
cd sp500-bot

# Voir les scores d'ouverture
./view_indicators.sh

# Voir l'historique quotidien
./view_history.sh

# Voir le scan du jour
sqlite3 sp500_daytrading.db "SELECT * FROM daily_scans WHERE date = '2025-12-13'"
```

---

## 🖥️ Déploiement VPS (24/7)

### 1. Préparation

```bash
# Sur votre machine locale
git add .
git commit -m "Structure finale avec 2 bots"
git push origin main

# Sur le VPS
cd ~
git clone https://github.com/votre-username/hyper-bot.git
cd hyper-bot
./install.sh
```

### 2. Configuration systemd

**Bot Crypto :**

```bash
sudo nano /etc/systemd/system/crypto-bot.service
```

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

**Bot S&P 500 :**

```bash
sudo nano /etc/systemd/system/sp500-bot.service
```

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

### 3. Activation

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer au démarrage
sudo systemctl enable crypto-bot sp500-bot

# Démarrer
sudo systemctl start crypto-bot sp500-bot

# Vérifier
sudo systemctl status crypto-bot
sudo systemctl status sp500-bot

# Logs en direct
tail -f crypto-bot/logs/bot.log
tail -f sp500-bot/logs/bot.log
```

---

## 🔧 Commandes utiles

### Gestion des bots (systemd)

```bash
# Redémarrer
sudo systemctl restart crypto-bot
sudo systemctl restart sp500-bot

# Arrêter
sudo systemctl stop crypto-bot
sudo systemctl stop sp500-bot

# Logs
journalctl -u crypto-bot -f
journalctl -u sp500-bot -f
```

### Mise à jour

```bash
cd ~/hyper-bot
git pull origin main
sudo systemctl restart crypto-bot sp500-bot
```

---

## 📈 Analyse ML

Après plusieurs jours de collecte de données :

```bash
# Adapter ml.py pour analyser crypto-bot
python ml.py  # Modifier DB_FILE dans le script

# Ou analyser sp500-bot
cd sp500-bot
# Modifier ml.py pour pointer vers sp500_daytrading.db
```

---

## ⚠️ Avertissement

**Simulation uniquement.** Ces bots :
- Ne passent pas de vrais ordres
- Simulent les trades localement
- Collectent des données pour analyse ML

Pour du trading réel, il faudrait :
- Comptes de trading actifs
- API keys authentifiées
- Gestion des ordres réels
- Capital réel à risque

---

## 🆘 Support

- 🐛 Bug ? Ouvrir une issue
- 💬 Questions ? Consulter le code (commenté)
- 📊 Analyse ? Attendre plusieurs jours de données

---

**Version : 2.0.0** | MIT License | Trading Simulation

