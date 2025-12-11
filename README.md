# 🤖 Hyperliquid Trading Bot

Bot de trading automatisé pour Hyperliquid avec collecte de données ML.

## 🎯 Fonctionnalités

- 📊 Analyse technique avec 20+ indicateurs (RSI, EMA, MACD, Bollinger Bands, SuperTrend, etc.)
- 🔄 Trading automatisé (LONG/SHORT) avec signaux basés sur 7 confirmations
- 💰 Gestion du risque (stop-loss, trailing stop, position sizing)
- 📈 Collecte de données pour analyse ML
- 💾 Stockage SQLite avec historique complet des trades
- 🔍 Logs détaillés pour debugging

## 📋 Prérequis

- Python 3.8+
- pip
- Accès internet (pour l'API Hyperliquid)

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/votre-username/hyper-bot.git
cd hyper-bot
```

### 2. Installer les dépendances

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate  # Sur Windows

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuration

Modifiez `main.py` pour ajuster les paramètres :

```python
ASSETS = ["BTC", "ETH", "SOL", "ARB", "MATIC"]  # Cryptos à trader
INITIAL_CAPITAL = 1000         # Capital de simulation
LEVERAGE = 2                   # Levier
RISK_PER_TRADE = 0.01          # 1% risque par trade
STOP_LOSS_PCT = 0.01          # 1% stop loss
MIN_CONFIRMATIONS = 5          # Signal min 5/7
```

## 🏃 Lancer le bot

### Méthode 1 : Script shell (Linux/Mac)

```bash
chmod +x run_bot.sh
./run_bot.sh
```

### Méthode 2 : Python direct

```bash
source venv/bin/activate
python main.py
```

## 🖥️ Déploiement sur VPS

Voir le guide complet : [deploy_guide.md](deploy_guide.md)

### Installation rapide

```bash
# Sur votre VPS
git clone https://github.com/votre-username/hyper-bot.git
cd hyper-bot

# Installer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurer le service systemd
sudo cp hyper-bot.service /etc/systemd/system/
sudo nano /etc/systemd/system/hyper-bot.service  # Remplacez %USER%

# Démarrer
sudo systemctl daemon-reload
sudo systemctl enable hyper-bot
sudo systemctl start hyper-bot
```

### Gestion du service

```bash
# Voir le statut
sudo systemctl status hyper-bot

# Voir les logs
tail -f logs/bot.log

# Redémarrer
sudo systemctl restart hyper-bot

# Arrêter
sudo systemctl stop hyper-bot
```

## 📊 Structure du projet

```
hyper-bot/
├── main.py                 # Bot principal
├── ml.py                   # Analyse ML (à venir)
├── requirements.txt        # Dépendances Python
├── run_bot.sh             # Script de lancement
├── deploy.sh              # Script de déploiement
├── hyper-bot.service      # Configuration systemd
├── deploy_guide.md        # Guide de déploiement
├── ISOLATION_GUIDE.md     # Guide d'isolation multi-bots
├── README.md              # Ce fichier
└── logs/                  # Logs (créé automatiquement)
```

## 🔧 Configuration

### Paramètres principaux

| Paramètre | Description | Défaut |
|-----------|-------------|--------|
| `ASSETS` | Liste des cryptos à trader | BTC, ETH, SOL, ARB, MATIC |
| `INITIAL_CAPITAL` | Capital de départ | $1000 |
| `LEVERAGE` | Levier utilisé | 2x |
| `RISK_PER_TRADE` | Risque par trade (% du capital) | 1% |
| `STOP_LOSS_PCT` | Stop loss initial | 1% |
| `MIN_CONFIRMATIONS` | Signaux minimum requis (sur 7) | 5 |
| `MIN_TRADE_DURATION` | Durée minimum d'un trade | 5 min |
| `MAX_TRADE_DURATION` | Durée maximum d'un trade | 120 min |

### Indicateurs techniques

Le bot utilise 20+ indicateurs :
- RSI, EMA (8, 21, 50, 200), MACD
- Bollinger Bands, Stochastic, ATR, ADX
- CCI, ROC, Williams %R, OBV, VWAP
- Volume Ratio, Volatility, Momentum, SuperTrend

### Système de signaux

Le bot génère des signaux basés sur 7 confirmations :
- **LONG** : Si 5+ indicateurs sont bull
- **SHORT** : Si 5+ indicateurs sont bear
- **AUCUN** : Si pas assez de confirmations

## 📈 Base de données

Le bot crée automatiquement une base SQLite (`trading_simulation.db`) avec :

- **Table `trades`** : Historique complet des trades avec tous les indicateurs
- **Table `portfolio`** : Snapshots du portfolio au fil du temps

### Requêtes utiles

```sql
-- Voir les trades fermés
SELECT * FROM trades WHERE status='CLOSED' ORDER BY id DESC LIMIT 10;

-- Statistiques
SELECT 
    COUNT(*) as total_trades,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl,
    COUNT(CASE WHEN pnl > 0 THEN 1 END) as winning_trades
FROM trades WHERE status='CLOSED';
```

## 🔍 Logs

Les logs sont affichés dans la console et sauvegardés dans `logs/bot.log` (en production).

Format des logs :
- 🟢 Trade ouvert/gagnant
- 🔴 Trade fermé/perdant
- ⚪ Analyse de marché
- 📊 Statistiques périodiques

## 🛡️ Gestion du risque

- **Position sizing** : Calculé automatiquement basé sur le risque souhaité
- **Stop loss** : Protection initiale
- **Trailing stop** : Protection dynamique après profit
- **Durée max** : Fermeture forcée après 2h

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## ⚠️ Avertissement

**Ce bot est à des fins éducatives et de simulation uniquement.**

- ⚠️ Le trading de cryptomonnaies comporte des risques élevés
- ⚠️ Ne tradez jamais plus que ce que vous pouvez vous permettre de perdre
- ⚠️ Testez toujours en simulation avant d'utiliser de l'argent réel
- ⚠️ Ce bot n'est pas garanti pour générer des profits

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Ouvrez une [issue](https://github.com/votre-username/hyper-bot/issues)
- Consultez les guides dans le repository

## 🙏 Remerciements

- API Hyperliquid pour les données de marché
- La communauté Python pour les excellentes bibliothèques

---

**Bon trading ! 📈🚀**

# hyper-bot
