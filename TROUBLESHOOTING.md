# 🔧 Dépannage

## ❌ Erreur: "No space left on device"

### Diagnostiquer le problème

```bash
# Voir l'espace utilisé (tous les systèmes de fichiers)
df -h

# Identifier si c'est /tmp qui est plein
df -h /tmp

# Si /tmp est plein (>90%), c'est le problème !
```

### ⚠️ IMPORTANT : Impact sur votre autre bot

**✅ SÉCURISÉ** : Utiliser `~/tmp` pour pip n'impacte **AUCUNEMENT** votre autre bot
- C'est juste un répertoire temporaire pour le téléchargement pip
- Votre bot de scraping utilise son propre code et son propre venv
- Aucun conflit possible

**⚠️ ATTENTION** : Nettoyer `/tmp` peut impacter votre bot si :
- Il écrit actuellement dans `/tmp`
- Vous supprimez des fichiers qu'il utilise

**✅ SOLUTION SÉCURISÉE** : Utiliser `~/tmp` au lieu de `/tmp` pour pip

### Solutions pour libérer de l'espace `/tmp`

#### ✅ Solution SÉCURISÉE (recommandée) : Utiliser ~/tmp pour pip

**Cette solution n'impacte PAS votre autre bot** :

```bash
cd ~/hyper-bot
source venv/bin/activate

# Créer un répertoire temporaire alternatif (dans votre home)
mkdir -p ~/tmp

# Installer avec TMPDIR personnalisé (utilise ~/tmp au lieu de /tmp)
TMPDIR=~/tmp pip install --no-cache-dir -r requirements.txt
```

**Pourquoi c'est sûr :**
- ✅ `/tmp` n'est pas modifié
- ✅ Votre autre bot continue d'utiliser `/tmp` normalement
- ✅ Pip utilise juste `~/tmp` pour ses téléchargements temporaires
- ✅ Après l'installation, vous pouvez même supprimer `~/tmp`

#### ⚠️ Solution ALTERNATIVE : Nettoyer /tmp (plus risqué)

**Attention : Peut impacter votre autre bot si il utilise `/tmp` activement**

```bash
# Nettoyer SEULEMENT les fichiers de plus de 24h (plus sûr)
sudo find /tmp -type f -mtime +1 -delete

# Vérifier l'espace après
df -h /tmp

# Réessayer l'installation
./setup.sh
```

**Alternative moins risquée** :
```bash
# Voir ce qui occupe de l'espace dans /tmp
sudo du -sh /tmp/* | sort -hr | head -10

# Supprimer seulement les dossiers spécifiques (si vous êtes sûr)
# Par exemple, si vous voyez des dossiers pip-* ou tmp.*
```

### Solutions pour libérer de l'espace disque principal

#### 1. Nettoyer les packages apt

```bash
sudo apt-get clean
sudo apt-get autoremove
sudo apt-get autoclean
```

#### 2. Nettoyer les logs système

```bash
# Voir la taille des logs
sudo du -sh /var/log/*

# Nettoyer les logs anciens (attention, gardez les récents)
sudo journalctl --vacuum-time=7d  # Garde seulement 7 jours
sudo journalctl --vacuum-size=100M  # Limite à 100MB

# Nettoyer les logs de votre bot de scraping
# (À adapter selon votre configuration)
sudo find /var/log -name "*.log" -type f -mtime +30 -delete
```

#### 3. Nettoyer les caches pip (si d'autres projets Python)

```bash
# Voir les caches pip
du -sh ~/.cache/pip

# Nettoyer les caches pip
pip cache purge  # Si dans un venv actif
# ou
rm -rf ~/.cache/pip
```

#### 4. Nettoyer les anciens kernels (Linux)

```bash
# Voir les kernels installés
dpkg -l | grep linux-image

# Supprimer les anciens kernels (gardez les 2 plus récents)
sudo apt-get purge linux-image-OLD-VERSION
```

#### 5. Vérifier les fichiers temporaires

```bash
# Nettoyer /tmp
sudo find /tmp -type f -atime +10 -delete

# Nettoyer ~/tmp
rm -rf ~/tmp/*
```

#### 6. Vérifier les gros fichiers

```bash
# Trouver les fichiers > 100MB
find ~ -type f -size +100M -exec ls -lh {} \; 2>/dev/null
```

### Solution rapide : Installer les dépendances minimales

Si vous ne pouvez pas libérer assez d'espace, installez seulement les dépendances essentielles :

```bash
cd ~/hyper-bot
source venv/bin/activate

# Installer seulement les dépendances critiques (sans ML pour le moment)
pip install pandas numpy requests eth-account hyperliquid-python-sdk

# Commenter temporairement matplotlib, seaborn, scikit-learn dans requirements.txt
# Ces packages sont uniquement pour ml.py (analyse ML future)
```

Puis modifiez `requirements.txt` temporairement :

```txt
pandas
numpy
requests
# matplotlib  # Commenté pour économiser de l'espace
# seaborn     # Commenté pour économiser de l'espace
# scikit-learn # Commenté pour économiser de l'espace
eth-account
hyperliquid-python-sdk
```

### Vérifier l'espace après nettoyage

```bash
df -h
```

Vous devriez avoir au moins **500MB libres** pour installer les dépendances Python.

## 🔍 Autres problèmes courants

### Problème : Permission denied

```bash
# Donner les permissions d'exécution
chmod +x setup.sh
chmod +x run_bot.sh
```

### Problème : Python 3 non trouvé

```bash
# Installer Python 3
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
```

### Problème : pip install échoue

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer avec plus de mémoire
pip install --no-cache-dir -r requirements.txt
```

### Problème : Le bot ne démarre pas

```bash
# Vérifier les logs
tail -f logs/bot.log
tail -f logs/bot_error.log

# Vérifier les permissions
ls -la ~/hyper-bot/

# Tester manuellement
cd ~/hyper-bot
source venv/bin/activate
python main.py
```

### Problème : Connexion API échoue

```bash
# Tester la connexion
curl https://api.hyperliquid.xyz/info

# Vérifier le firewall
sudo ufw status
```

---

**Besoin d'aide ?** Consultez les logs et vérifiez l'espace disque d'abord !

