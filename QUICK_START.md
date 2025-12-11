# ⚡ Démarrage Rapide

## 🚀 Installation et lancement en 3 commandes

### Sur votre machine locale (développement)

```bash
git clone https://github.com/VOTRE-USERNAME/hyper-bot.git
cd hyper-bot
./setup.sh && ./run_bot.sh
```

### Sur votre VPS (production)

```bash
# 1. Cloner
git clone https://github.com/VOTRE-USERNAME/hyper-bot.git
cd hyper-bot

# 2. Installer
./setup.sh

# 3. Configurer le service systemd
sudo cp hyper-bot.service /etc/systemd/system/
sudo nano /etc/systemd/system/hyper-bot.service  # Remplacez %USER% par votre utilisateur

# 4. Démarrer
sudo systemctl daemon-reload
sudo systemctl enable hyper-bot
sudo systemctl start hyper-bot

# 5. Voir les logs
tail -f logs/bot.log
```

## 📝 Configuration minimale

Modifiez `main.py` ligne 9-14 :

```python
ASSETS = ["BTC", "ETH"]  # Cryptos à trader
INITIAL_CAPITAL = 1000   # Capital de départ
RISK_PER_TRADE = 0.01    # 1% risque par trade
LEVERAGE = 2             # Levier 2x
STOP_LOSS_PCT = 0.01     # Stop loss 1%
```

## 🔍 Commandes utiles

```bash
# Voir le statut (VPS)
sudo systemctl status hyper-bot

# Arrêter
sudo systemctl stop hyper-bot

# Redémarrer
sudo systemctl restart hyper-bot

# Logs en temps réel
tail -f logs/bot.log

# Voir les trades dans la DB
sqlite3 trading_simulation.db "SELECT * FROM trades ORDER BY id DESC LIMIT 10;"
```

## 📚 Documentation complète

- **README.md** - Documentation principale
- **deploy_guide.md** - Guide de déploiement détaillé
- **ISOLATION_GUIDE.md** - Isolation multi-bots
- **GIT_SETUP.md** - Mise en ligne sur GitHub

---

**C'est parti ! 🤖**

