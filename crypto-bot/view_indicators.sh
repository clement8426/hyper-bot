#!/bin/bash

DB_FILE="trading_simulation.db"

echo "======================================================================"
echo "📊 INDICATEURS TECHNIQUES - BOT CRYPTO"
echo "======================================================================"
echo ""

if [ ! -f "$DB_FILE" ]; then
    echo "❌ Base de données non trouvée: $DB_FILE"
    echo "   Lancez d'abord le bot pour générer des données."
    exit 1
fi

# Vérifier si des trades existent
TRADE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM trades WHERE status='CLOSED';" 2>/dev/null || echo "0")

if [ "$TRADE_COUNT" -eq 0 ]; then
    echo "ℹ️  Aucun trade fermé pour le moment."
    echo "   Attendez que le bot ferme des positions."
    exit 0
fi

echo "=== Résumé des trades (avec indicateurs) ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
.width 5 6 6 8 8 8 8 8 8 8 8 8 8 8
SELECT 
  id,
  asset,
  side,
  ROUND(rsi, 2) as rsi,
  ROUND(ema8, 2) as ema8,
  ROUND(ema21, 2) as ema21,
  ROUND(macd, 4) as macd,
  ROUND(adx, 2) as adx,
  ROUND(vwap, 2) as vwap,
  bull_score,
  bear_score,
  ROUND(pnl, 2) as pnl
FROM trades 
WHERE status='CLOSED'
ORDER BY timestamp DESC
LIMIT 10;
SQL

echo ""
echo "=== Détails du dernier trade ==="
sqlite3 "$DB_FILE" <<SQL
.mode line
SELECT 
  id, asset, side,
  entry_price, exit_price, pnl, pnl_pct,
  duration_minutes, exit_reason,
  timestamp,
  ROUND(rsi, 2) as RSI,
  ROUND(ema8, 2) as EMA_8,
  ROUND(ema21, 2) as EMA_21,
  ROUND(macd, 4) as MACD,
  ROUND(adx, 2) as ADX,
  bull_score as "Bull Score",
  bear_score as "Bear Score",
  trend_short as "Tendance Court",
  trend_medium as "Tendance Moyen"
FROM trades 
WHERE status='CLOSED'
ORDER BY timestamp DESC
LIMIT 1;
SQL

echo ""
echo "======================================================================"
echo "💾 Export CSV complet: sqlite3 $DB_FILE -header -csv 'SELECT * FROM trades' > trades.csv"
echo "======================================================================"

