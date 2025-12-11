# 🔒 Guide d'isolation pour bots multiples

Ce guide explique comment faire tourner le bot de trading **sans affecter** votre bot de scraping existant.

## ✅ Isolation garantie

### Architecture isolée

```
Votre VPS
├── bot-scraping/          ← Votre bot existant (NE PAS TOUCHER)
│   ├── venv/             ← Son environnement Python
│   ├── main.py
│   └── requirements.txt
│
└── hyper-bot/            ← Nouveau bot de trading (COMPLÈTEMENT SÉPARÉ)
    ├── venv/             ← Son propre environnement Python
    ├── main.py
    ├── requirements.txt
    └── logs/
```

### Points d'isolation

| Aspect | Bot de Scraping | Bot de Trading | Conflit ? |
|--------|----------------|----------------|-----------|
| **Dossier** | `~/bot-scraping/` | `~/hyper-bot/` | ❌ Non |
| **Environnement virtuel** | `~/bot-scraping/venv/` | `~/hyper-bot/venv/` | ❌ Non |
| **Service systemd** | `scraping-bot.service` | `hyper-bot.service` | ❌ Non |
| **Ports utilisés** | Dépend de votre bot | Aucun (HTTP sortant) | ❌ Non |
| **Dépendances Python** | Installées dans son venv | Installées dans son venv | ❌ Non |

## 📋 Checklist de déploiement sécurisé

### Avant de commencer

- [ ] Vérifier que votre bot de scraping tourne : `sudo systemctl status votre-service`
- [ ] Noter le nom de votre service de scraping (pour vérifier après)
- [ ] Noter le dossier de votre bot de scraping (pour ne pas confondre)

### Pendant le déploiement

- [ ] Créer un **nouveau dossier** séparé : `~/hyper-bot/`
- [ ] Créer un **nouvel environnement virtuel** : `python3 -m venv ~/hyper-bot/venv`
- [ ] Installer les dépendances **seulement dans le nouveau venv**
- [ ] Créer un **service systemd avec un nom différent** : `hyper-bot.service`
- [ ] Vérifier que les chemins dans le service pointent vers `~/hyper-bot/`

### Après le déploiement

- [ ] Vérifier que le bot de scraping tourne toujours : `sudo systemctl status votre-service`
- [ ] Vérifier que les deux bots tournent : `ps aux | grep python`
- [ ] Vérifier les logs du bot de scraping (pas d'erreur)
- [ ] Vérifier les logs du bot de trading

## 🔍 Commandes de vérification

### Voir tous les bots Python qui tournent

```bash
ps aux | grep python | grep -v grep
```

Vous devriez voir quelque chose comme :
```
user   1234  python /home/user/bot-scraping/venv/bin/python scraping_main.py
user   5678  python /home/user/hyper-bot/venv/bin/python main.py
```

### Voir tous les services systemd liés à Python

```bash
sudo systemctl list-units --type=service --all | grep -E "(bot|scraping|trading)"
```

Exemple :
```
scraping-bot.service    loaded active running   Bot de Scraping
hyper-bot.service       loaded active running   Hyperliquid Trading Bot
```

### Vérifier les environnements virtuels utilisés

```bash
# Lister tous les processus Python avec leur environnement
ps aux | grep python | grep venv | awk '{print $11, $NF}'
```

### Vérifier les dépendances installées

```bash
# Dépendances du bot de scraping
source ~/bot-scraping/venv/bin/activate
pip list
deactivate

# Dépendances du bot de trading
source ~/hyper-bot/venv/bin/activate
pip list
deactivate
```

## ⚠️ Ce qu'il ne faut JAMAIS faire

❌ **NE PAS** utiliser le même `venv/` pour les deux bots
❌ **NE PAS** installer les dépendances globalement (`pip install` sans venv)
❌ **NE PAS** modifier le service de votre bot de scraping
❌ **NE PAS** mettre les deux bots dans le même dossier
❌ **NE PAS** utiliser le même nom de service systemd

## ✅ Ce qui est sûr de faire

✅ Créer un nouveau dossier séparé
✅ Créer un nouvel environnement virtuel
✅ Créer un nouveau service systemd
✅ Les deux bots peuvent tourner en parallèle 24/7
✅ Les deux bots peuvent être redémarrés indépendamment
✅ Les deux bots ont leurs propres logs

## 🛠️ Commandes pour gérer les deux bots séparément

### Bot de scraping

```bash
# Voir le statut
sudo systemctl status scraping-bot  # Remplacez par votre nom de service

# Redémarrer
sudo systemctl restart scraping-bot

# Voir les logs
journalctl -u scraping-bot -f
```

### Bot de trading

```bash
# Voir le statut
sudo systemctl status hyper-bot

# Redémarrer
sudo systemctl restart hyper-bot

# Voir les logs
tail -f ~/hyper-bot/logs/bot.log
```

## 🔄 Mise à jour sécurisée

Pour mettre à jour le bot de trading **sans toucher** au bot de scraping :

```bash
# 1. Arrêter seulement le bot de trading
sudo systemctl stop hyper-bot

# 2. Activer son environnement virtuel (pas celui du scraping !)
cd ~/hyper-bot
source venv/bin/activate

# 3. Mettre à jour
git pull  # ou copier les nouveaux fichiers
pip install -r requirements.txt --upgrade

# 4. Redémarrer
deactivate
sudo systemctl start hyper-bot

# ✅ Votre bot de scraping n'a pas été touché !
```

## 🆘 En cas de problème

Si votre bot de scraping ne fonctionne plus après le déploiement :

1. **Vérifier qu'il tourne toujours** :
   ```bash
   sudo systemctl status votre-service-scraping
   ```

2. **Redémarrer votre bot de scraping** :
   ```bash
   sudo systemctl restart votre-service-scraping
   ```

3. **Vérifier les logs** :
   ```bash
   sudo journalctl -u votre-service-scraping -n 50
   ```

4. **Vérifier qu'il n'y a pas eu de modification accidentelle** :
   ```bash
   # Vérifier les permissions
   ls -la ~/bot-scraping/
   
   # Vérifier que son venv existe toujours
   ls -la ~/bot-scraping/venv/
   ```

5. **Si problème persiste** : Le problème vient probablement d'autre chose (espace disque, mémoire, etc.), pas du nouveau bot.

## 📊 Ressources système

Les deux bots partagent les ressources du serveur. Surveillez :

```bash
# CPU et RAM
htop

# Espace disque
df -h

# Connexions réseau
netstat -an | grep ESTABLISHED | wc -l
```

Si votre serveur manque de ressources, vous pouvez limiter un des bots ou ajouter plus de RAM/CPU.

