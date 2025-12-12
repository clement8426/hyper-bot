# 🤖 Hyper-Bot - Trading Bot Hyperliquid

Bot de trading automatisé avec 30+ indicateurs techniques et filtres de sécurité intelligents.

## 🚀 Installation

### Local (Mac/Linux/Windows)

```bash
# Cloner le repo
git clone https://github.com/votre-username/hyper-bot.git
cd hyper-bot

# Lancer (crée venv + installe dépendances + lance le bot)
./run_bot.sh
```

### VPS (Ubuntu/Debian) - Mode 24/7

```bash
# 1. Cloner le repo
git clone https://github.com/votre-username/hyper-bot.git
cd hyper-bot

# 2. Setup initial
./setup.sh

# 3. Configurer le service systemd
sudo cp hyper-bot.service /etc/systemd/system/
sudo sed -i "s|%USER%|$USER|g" /etc/systemd/system/hyper-bot.service
sudo systemctl daemon-reload
sudo systemctl enable hyper-bot
sudo systemctl start hyper-bot

# 4. Vérifier le statut
sudo systemctl status hyper-bot
tail -f ~/hyper-bot/logs/bot.log
```

## ⚙️ Configuration

Modifiez les paramètres dans `main.py` (lignes 10-27) :

```python
ASSETS = ["BTC", "ETH", "SOL", "ARB", "MATIC"]
INITIAL_CAPITAL = 1000
LEVERAGE = 2
RISK_PER_TRADE = 0.01  # 1% risque par trade
STOP_LOSS_PCT = 0.01   # 1% stop loss
MIN_CONFIRMATIONS = 5  # 5 signaux sur 7 minimum
MIN_TRADE_DURATION = 5      # 5 minutes minimum
MAX_TRADE_DURATION = 120    # 2 heures maximum
```

## 🛡️ Filtres de sécurité (v1.1.0+)

Le bot refuse automatiquement :
- ❌ LONG si RSI > 70 (surchauffe) ou tendance baissière
- ❌ SHORT si RSI < 30 (survente) ou tendance haussière

## 📊 Analyse des données

```bash
# Voir tous les indicateurs des trades
./view_indicators.sh

# Résumé des trades depuis hier
./view_history.sh

# Analyse ML (après plusieurs jours de données)
source venv/bin/activate
python ml.py
```

## 🔧 Commandes VPS

```bash
# Voir les logs en direct
tail -f ~/hyper-bot/logs/bot.log

# Redémarrer le bot
sudo systemctl restart hyper-bot

# Arrêter le bot
sudo systemctl stop hyper-bot

# Voir le statut
sudo systemctl status hyper-bot
```

## 📈 Base de données

Toutes les données sont dans `trading_simulation.db` (SQLite) :

```sql
-- Voir les derniers trades
SELECT * FROM trades WHERE status='CLOSED' ORDER BY id DESC LIMIT 10;

-- Statistiques
SELECT 
    COUNT(*) as total,
    SUM(pnl) as pnl_total,
    AVG(pnl) as pnl_moyen
FROM trades WHERE status='CLOSED';
```

## 🔄 Mise à jour

```bash
# Sur le VPS
cd ~/hyper-bot
git pull origin main
sudo systemctl restart hyper-bot
```

## ⚠️ Avertissement

**Bot de simulation uniquement.** Le trading comporte des risques. Ne tradez jamais plus que ce que vous pouvez perdre.

## 📝 Structure du projet

```
hyper-bot/
├── main.py               # Bot principal
├── ml.py                 # Analyse ML
├── requirements.txt      # Dépendances Python
├── run_bot.sh           # Lancer en local
├── setup.sh             # Setup VPS
├── hyper-bot.service    # Service systemd
├── view_indicators.sh   # Voir les indicateurs
├── view_history.sh      # Voir l'historique
└── README.md            # Ce fichier
```

## 🆘 Support

- 🐛 Bug ? Ouvrir une issue sur GitHub
- 💬 Questions ? Consulter le code source (commenté)
- 📊 Données ML ? Attendre plusieurs jours de collecte

---

**Version actuelle : 1.1.0** | MIT License

