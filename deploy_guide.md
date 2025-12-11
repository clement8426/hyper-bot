# 🚀 Guide de déploiement sur VPS

Ce guide vous montre comment déployer le bot sur votre VPS sans perturber Nginx et les autres services.

## 📋 Prérequis

- VPS avec Linux (Ubuntu/Debian recommandé)
- Accès SSH
- Python 3.8+ installé
- Votre serveur avec Nginx déjà configuré (ne sera pas affecté)

## 🔒 ISOLATION COMPLÈTE (IMPORTANT si vous avez déjà un bot Python)

**⚠️ CRITIQUE** : Pour éviter tout conflit avec votre bot de scraping existant, le bot de trading utilise :
- ✅ Son **propre environnement virtuel Python** (complètement séparé)
- ✅ Son **propre dossier** isolé
- ✅ Son **propre service systemd** distinct
- ✅ Ses **propres dépendances** (pas de partage avec votre autre bot)

Les deux bots peuvent tourner **en parallèle** sans problème !

---

## 🔧 Méthode 1 : Déploiement manuel (Recommandé)

### 1. Se connecter au VPS

```bash
ssh votre_utilisateur@votre-vps-ip
```

### 2. Vérifier votre bot de scraping (ne le touchez pas !)

```bash
# Vérifier qu'il tourne toujours
ps aux | grep python

# Vérifier son environnement (pour info seulement, ne pas toucher)
# Notez son dossier et ne mettez PAS le nouveau bot au même endroit
```

### 3. Créer le dossier du bot de trading (SÉPARÉ)

```bash
cd ~
mkdir -p hyper-bot  # Dossier complètement séparé de votre bot de scraping
cd hyper-bot
mkdir -p logs
```

### 3. Transférer les fichiers depuis votre machine locale

**Option A : Avec SCP (depuis votre machine locale)**

```bash
scp main.py requirements.txt run_bot.sh votre_utilisateur@votre-vps-ip:~/hyper-bot/
```

**Option B : Avec Git (si vous avez un repo)**

```bash
cd ~/hyper-bot
git clone https://votre-repo.git .
```

**Option C : Créer les fichiers manuellement**

Copiez le contenu de `main.py` et `requirements.txt` dans les fichiers sur le serveur.

### 4. Créer l'environnement virtuel ISOLÉ

```bash
# IMPORTANT : Ne pas utiliser le même venv que votre bot de scraping !
# Créer un NOUVEL environnement virtuel dans ce dossier
python3 -m venv venv

# Activer l'environnement (celui-ci est isolé de votre autre bot)
source venv/bin/activate

# Vérifier que vous êtes dans le bon venv
which python  # Devrait afficher: /home/votre_user/hyper-bot/venv/bin/python

# Installer les dépendances (seulement pour ce bot)
pip install --upgrade pip
pip install -r requirements.txt

# Désactiver l'environnement
deactivate
```

**✅ Garanties d'isolation :**
- Chaque bot a son propre `venv/` dans son propre dossier
- Les dépendances sont installées séparément
- Aucun conflit possible

### 5. Tester le bot (sans affecter votre autre bot)

```bash
# Activer l'environnement virtuel du bot de trading
cd ~/hyper-bot
source venv/bin/activate

# Tester que tout fonctionne
python main.py
```

Appuyez sur `Ctrl+C` pour arrêter après avoir vérifié.

**✅ Votre bot de scraping continue de tourner normalement pendant ce test**

### 6. Créer le service systemd (SÉPARÉ de votre autre bot)

Cela permet au bot de tourner en arrière-plan et de redémarrer automatiquement.
**Le service aura un nom différent** de celui de votre bot de scraping.

```bash
sudo nano /etc/systemd/system/hyper-bot.service
```

Copiez ce contenu (remplacez `votre_utilisateur` par votre nom d'utilisateur) :

```ini
[Unit]
Description=Hyperliquid Trading Bot
After=network.target

[Service]
Type=simple
User=votre_utilisateur
Group=votre_utilisateur
WorkingDirectory=/home/votre_utilisateur/hyper-bot
Environment="PATH=/home/votre_utilisateur/hyper-bot/venv/bin"
ExecStart=/home/votre_utilisateur/hyper-bot/venv/bin/python main.py
Restart=always
RestartSec=10

# Logs
StandardOutput=append:/home/votre_utilisateur/hyper-bot/logs/bot.log
StandardError=append:/home/votre_utilisateur/hyper-bot/logs/bot_error.log

[Install]
WantedBy=multi-user.target
```

Sauvegardez avec `Ctrl+X`, puis `Y`, puis `Enter`.

### 7. Activer et démarrer le service

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer le service (démarre au boot)
sudo systemctl enable hyper-bot

# Démarrer le bot de trading
sudo systemctl start hyper-bot

# Vérifier le statut du bot de trading
sudo systemctl status hyper-bot

# Vérifier que votre bot de scraping tourne toujours
sudo systemctl status votre-bot-scraping  # Remplacez par le nom de votre service
```

**✅ Les deux bots peuvent tourner en parallèle sans problème !**

### 8. Gérer le bot

```bash
# Voir les logs en temps réel
tail -f ~/hyper-bot/logs/bot.log

# Voir les erreurs
tail -f ~/hyper-bot/logs/bot_error.log

# Arrêter le bot
sudo systemctl stop hyper-bot

# Redémarrer le bot
sudo systemctl restart hyper-bot

# Voir le statut
sudo systemctl status hyper-bot
```

## 🔧 Méthode 2 : Avec screen (plus simple, moins robuste)

Si vous ne voulez pas utiliser systemd :

```bash
# Installer screen
sudo apt-get install screen

# Démarrer une session screen
screen -S trading-bot

# Dans la session screen
cd ~/hyper-bot
source venv/bin/activate
python main.py

# Détacher avec Ctrl+A puis D

# Revenir à la session
screen -r trading-bot

# Voir toutes les sessions
screen -ls
```

## 🔍 Vérifications

### Vérifier que Nginx fonctionne toujours

```bash
sudo systemctl status nginx
curl http://localhost
```

### Vérifier les processus Python (vous devriez voir les DEUX bots)

```bash
ps aux | grep python
```

Vous devriez voir :
- ✅ Votre bot de scraping (son processus)
- ✅ Le bot de trading (son processus)
- ✅ Les deux utilisent des `venv` différents

### Vérifier les services systemd

```bash
# Voir tous les services Python qui tournent
sudo systemctl list-units --type=service | grep -E "(bot|scraping|python)"

# Statut de chaque bot séparément
sudo systemctl status hyper-bot
sudo systemctl status votre-bot-scraping  # Votre autre bot
```

### Vérifier les ports utilisés

```bash
sudo netstat -tulpn | grep LISTEN
```

Le bot n'écoute sur aucun port (il fait des requêtes HTTP), donc il ne devrait pas interférer.

## 📊 Monitoring

### Logs du bot

```bash
# Voir les dernières lignes
tail -n 50 ~/hyper-bot/logs/bot.log

# Chercher des erreurs
grep -i error ~/hyper-bot/logs/bot_error.log

# Taille des logs
ls -lh ~/hyper-bot/logs/
```

### Rotation des logs (optionnel)

Pour éviter que les logs deviennent trop gros :

```bash
sudo nano /etc/logrotate.d/hyper-bot
```

Contenu :
```
/home/votre_utilisateur/hyper-bot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## 🔒 Sécurité

### Firewall

Le bot n'a pas besoin de port ouvert (il fait des requêtes sortantes). Assurez-vous que votre firewall ne bloque pas les connexions sortantes HTTPS (port 443).

### Permissions

```bash
# S'assurer que les fichiers sont sécurisés
chmod 600 ~/hyper-bot/main.py
chmod 700 ~/hyper-bot
```

## ❌ Désinstaller

```bash
# Arrêter et désactiver le service
sudo systemctl stop hyper-bot
sudo systemctl disable hyper-bot

# Supprimer le service
sudo rm /etc/systemd/system/hyper-bot.service
sudo systemctl daemon-reload

# Supprimer les fichiers (optionnel)
rm -rf ~/hyper-bot
```

## 🐛 Dépannage

### Le bot ne démarre pas

```bash
# Voir les erreurs
sudo journalctl -u hyper-bot -n 50 --no-pager

# Tester manuellement
cd ~/hyper-bot
source venv/bin/activate
python main.py
```

### Problème de permissions

```bash
# Vérifier les permissions
ls -la ~/hyper-bot/

# Corriger si nécessaire
chown -R votre_utilisateur:votre_utilisateur ~/hyper-bot
```

### Le bot s'arrête constamment

Vérifiez les logs d'erreur et les ressources système (RAM, CPU).

```bash
# Utilisation ressources
htop
df -h  # Espace disque
free -h  # RAM
```

## 📝 Notes importantes

- ✅ Le bot n'affecte PAS Nginx ou vos autres services
- ✅ Le bot utilise uniquement des requêtes HTTP sortantes (pas de port à ouvrir)
- ✅ Le bot est isolé dans son propre dossier et environnement virtuel
- ✅ Les logs sont stockés localement
- ✅ Le bot redémarre automatiquement en cas de crash (avec systemd)

## 🆘 Support

En cas de problème, vérifiez :
1. Les logs : `tail -f ~/hyper-bot/logs/bot_error.log`
2. Le statut : `sudo systemctl status hyper-bot`
3. Les ressources système : `htop`, `df -h`

