#!/bin/bash

DB_FILE="sp500_daytrading.db"

echo "======================================================================"
echo "📊 INDICATEURS TECHNIQUES - BOT S&P 500 DAY TRADING"
echo "======================================================================"
echo ""

if [ ! -f "$DB_FILE" ]; then
    echo "❌ Base de données non trouvée: $DB_FILE"
    echo "   Lancez d'abord le bot pour générer des données."
    exit 1
fi

TRADE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM trades WHERE status='CLOSED';" 2>/dev/null || echo "0")

if [ "$TRADE_COUNT" -eq 0 ]; then
    echo "ℹ️  Aucun trade fermé pour le moment."
    exit 0
fi

echo "=== Résumé des trades avec scores d'ouverture ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
SELECT 
  id,
  symbol,
  side,
  ROUND(opening_score, 0) as score,
  ROUND(gap_pct, 2) as "gap%",
  ROUND(volume_ratio, 1) as "vol_x",
  ROUND(first_5min_move, 2) as "5min%",
  ROUND(pnl, 2) as pnl,
  substr(date, 1, 10) as date
FROM trades 
WHERE status='CLOSED'
ORDER BY timestamp DESC
LIMIT 10;
SQL

echo ""
echo "=== Scan du jour (si disponible) ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
SELECT 
  symbol,
  ROUND(score, 0) as score,
  ROUND(gap_pct, 2) as "gap%",
  ROUND(volume_ratio, 1) as "vol_x",
  ROUND(first_5min_move, 2) as "5min%",
  CASE WHEN selected THEN '✓' ELSE ' ' END as tradé
FROM daily_scans 
WHERE date = (SELECT MAX(date) FROM daily_scans)
ORDER BY score DESC
LIMIT 20;
SQL

echo ""
echo "======================================================================"
echo "💾 Export CSV: sqlite3 $DB_FILE -header -csv 'SELECT * FROM trades' > trades.csv"
echo "======================================================================"

