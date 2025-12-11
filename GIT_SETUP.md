# 📦 Guide de mise en ligne sur GitHub

## 🚀 Étapes pour publier sur GitHub

### 1. Créer le repository sur GitHub

1. Allez sur [GitHub](https://github.com)
2. Cliquez sur **"New repository"** (ou **"+"** → **"New repository"**)
3. Nommez-le : `hyper-bot` (ou autre nom de votre choix)
4. **Ne cochez PAS** "Initialize with README" (on en a déjà un)
5. Cliquez sur **"Create repository"**

### 2. Initialiser Git dans le projet (sur votre machine locale)

```bash
cd /Users/soleadmaci9/test/hyper-bot

# Initialiser Git
git init

# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Premier commit
git commit -m "Initial commit: Bot de trading Hyperliquid avec collecte ML"

# Ajouter le remote GitHub
git remote add origin https://github.com/VOTRE-USERNAME/hyper-bot.git
# Remplacez VOTRE-USERNAME par votre nom d'utilisateur GitHub

# Push vers GitHub
git branch -M main
git push -u origin main
```

### 3. Vérifier sur GitHub

Allez sur votre repository GitHub et vérifiez que tous les fichiers sont bien là.

## 📋 Fichiers qui seront sur GitHub

✅ **Fichiers inclus :**
- `main.py` - Code principal
- `ml.py` - Analyse ML
- `requirements.txt` - Dépendances
- `run_bot.sh` - Script de lancement
- `setup.sh` - Script d'installation
- `deploy.sh` - Script de déploiement
- `hyper-bot.service` - Service systemd
- `README.md` - Documentation
- `deploy_guide.md` - Guide de déploiement
- `ISOLATION_GUIDE.md` - Guide d'isolation
- `.gitignore` - Exclusions Git

❌ **Fichiers exclus (par .gitignore) :**
- `venv/` - Environnement virtuel (à recréer)
- `*.db` - Base de données (créée automatiquement)
- `logs/` - Logs (créés automatiquement)
- `__pycache__/` - Cache Python

## 🔄 Après le clonage sur le VPS

### Sur votre VPS :

```bash
# Cloner le repo
git clone https://github.com/VOTRE-USERNAME/hyper-bot.git
cd hyper-bot

# Installation automatique
chmod +x setup.sh
./setup.sh

# Lancer le bot
./run_bot.sh
```

## 🔐 Avec authentification GitHub

Si vous utilisez une authentification GitHub :

### Option 1 : HTTPS avec Personal Access Token

```bash
git remote set-url origin https://VOTRE-TOKEN@github.com/VOTRE-USERNAME/hyper-bot.git
```

### Option 2 : SSH (recommandé)

```bash
# Générer une clé SSH si vous n'en avez pas
ssh-keygen -t ed25519 -C "votre_email@example.com"

# Ajouter la clé à votre agent SSH
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copier la clé publique
cat ~/.ssh/id_ed25519.pub
# Puis ajoutez-la sur GitHub : Settings → SSH and GPG keys → New SSH key

# Changer le remote en SSH
git remote set-url origin git@github.com:VOTRE-USERNAME/hyper-bot.git
```

## 📝 Commandes Git utiles

```bash
# Voir le statut
git status

# Ajouter des changements
git add .
git commit -m "Description des changements"

# Push vers GitHub
git push

# Voir l'historique
git log --oneline

# Créer une branche
git checkout -b feature/nouvelle-fonctionnalite

# Mettre à jour depuis GitHub
git pull
```

## 🔄 Mise à jour du code

### Depuis votre machine locale :

```bash
cd /Users/soleadmaci9/test/hyper-bot

# Faire des modifications...

# Commit et push
git add .
git commit -m "Description des changements"
git push
```

### Sur le VPS (mettre à jour) :

```bash
cd ~/hyper-bot

# Arrêter le bot
sudo systemctl stop hyper-bot

# Mettre à jour depuis GitHub
git pull

# Réinstaller les dépendances si requirements.txt a changé
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Redémarrer le bot
sudo systemctl start hyper-bot
```

## 🏷️ Créer une release (optionnel)

Quand le projet est stable :

```bash
# Créer un tag
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

Puis sur GitHub, allez dans **Releases** → **Draft a new release** et utilisez le tag.

## ✅ Checklist avant le push

- [ ] Vérifier que `.gitignore` exclut bien `venv/`, `*.db`, `logs/`
- [ ] Vérifier que `README.md` est à jour
- [ ] Vérifier que `requirements.txt` contient toutes les dépendances
- [ ] Tester que `setup.sh` fonctionne
- [ ] Vérifier qu'il n'y a pas de mots de passe/clés API dans le code

---

**C'est prêt ! 🚀**

