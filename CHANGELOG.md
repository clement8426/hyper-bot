# Changelog

## Version 1.1.0 - 2025-12-12

### 🎯 Améliorations majeures

#### Filtres de sécurité pour éviter les trades à contre-tendance
- **Ajout de filtres avant ouverture de position** :
  - ❌ **LONG refusé** si RSI > 70 (marché surchauffé)
  - ❌ **LONG refusé** si tendance court ET moyen terme baissières
  - ❌ **SHORT refusé** si RSI < 30 (marché survendu)
  - ❌ **SHORT refusé** si tendance court ET moyen terme haussières

#### Affichage amélioré
- **Indication des signaux filtrés** : Le bot affiche maintenant pourquoi un signal a été rejeté
  - Exemple : `⚠️ SHORT filtré (tendance haussière)`
  - Exemple : `⚠️ LONG filtré (RSI surchauffé)`

### 📊 Analyse des problèmes résolus

**Problème identifié** : Trade #1 (ETH SHORT) a perdu -$10.67 car :
- RSI était à 74.8 (surchauffe haussière)
- Tendance court/moyen terme : UP
- Prix au-dessus des Bollinger Bands
- MACD positif
- → **SHORT pris à contre-tendance**

**Solution** : Avec les nouveaux filtres, ce trade aurait été **automatiquement rejeté** avec le message :
`⚠️ SHORT filtré (tendance haussière)`

### 🔧 Corrections techniques

- ✅ Vérification des scores `bull_score` et `bear_score` avant sauvegarde en base
- ✅ Validation des conditions de marché avant ouverture de position
- ✅ Affichage en temps réel des raisons de filtrage

### 📈 Impact attendu

- **Réduction des trades perdants** : Évite les positions à contre-tendance
- **Meilleure qualité des signaux** : Seulement les setups avec conditions favorables
- **Plus de transparence** : Logs indiquent pourquoi un signal est rejeté

---

## Version 1.0.0 - 2025-12-11

### Première version déployée
- Bot de trading multi-indicateurs (30+ indicateurs techniques)
- Gestion des positions avec stop-loss et trailing stop
- Sauvegarde dans base SQLite pour analyse ML
- Configuration pour trades de 5min à 2h
- Risque limité à 1% par trade

