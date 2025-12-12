# 📁 Structure des fichiers du projet

## ✅ FICHIERS ESSENTIELS (à garder)

### Code source
- `main.py` - Bot de trading principal
- `ml.py` - Script d'analyse ML
- `requirements.txt` - Dépendances Python

### Scripts de lancement
- `run_bot.sh` - Lancer le bot en local
- `setup.sh` - Setup initial sur VPS
- `hyper-bot.service` - Configuration systemd (24/7)

### Scripts d'analyse
- `view_indicators.sh` - Affiche tous les indicateurs des trades
- `view_history.sh` - Résumé de l'historique des trades

### Documentation
- `README.md` - Documentation principale
- `.gitignore` - Fichiers à ignorer par Git

---

## 🗑️ FICHIERS DOCUMENTATION (peuvent être supprimés)

Ces fichiers sont utiles pour la première installation mais peuvent être supprimés après :

- `CHANGELOG.md` - Historique des versions
- `DEPLOY_UPDATE.md` - Guide de mise à jour
- `QUICK_DEPLOY.sh` - Script de déploiement rapide
- `deploy_guide.md` - Guide de déploiement détaillé
- `deploy.sh` - Script de déploiement
- `GIT_SETUP.md` - Guide Git
- `ISOLATION_GUIDE.md` - Guide d'isolation multi-bots
- `QUICK_START.md` - Guide de démarrage rapide
- `TROUBLESHOOTING.md` - Guide de dépannage

---

## 📦 FICHIERS GÉNÉRÉS (ne pas commit)

Ces fichiers sont générés automatiquement et ignorés par Git :

- `venv/` - Environnement virtuel Python
- `logs/` - Logs du bot
- `trading_simulation.db` - Base de données SQLite
- `__pycache__/` - Cache Python
- `*.pyc` - Bytecode Python

---

## 🧹 POUR NETTOYER

### Option 1 : Script automatique
```bash
./CLEANUP.sh
```

### Option 2 : Manuel
```bash
rm CHANGELOG.md DEPLOY_UPDATE.md QUICK_DEPLOY.sh deploy_guide.md deploy.sh
rm GIT_SETUP.md ISOLATION_GUIDE.md QUICK_START.md TROUBLESHOOTING.md
mv README_SIMPLE.md README.md  # Remplacer par version simple
```

---

## 📊 STRUCTURE FINALE (après nettoyage)

```
hyper-bot/
├── main.py               # 🔧 Bot principal
├── ml.py                 # 📊 Analyse ML
├── requirements.txt      # 📦 Dépendances
├── run_bot.sh           # 🚀 Lancer local
├── setup.sh             # ⚙️ Setup VPS
├── hyper-bot.service    # 🔄 Service systemd
├── view_indicators.sh   # 📈 Voir indicateurs
├── view_history.sh      # 📜 Voir historique
├── README.md            # 📖 Documentation
├── .gitignore           # 🚫 Git ignore
├── venv/                # 🐍 Environnement virtuel (généré)
├── logs/                # 📝 Logs (généré)
└── trading_simulation.db # 💾 Base de données (généré)
```

**10 fichiers essentiels + 3 dossiers générés = Projet propre et minimal** ✨

