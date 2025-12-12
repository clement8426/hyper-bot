#!/bin/bash

DB_FILE="trading_simulation.db"

echo "======================================================================"
echo "📊 POSITIONS OUVERTES - BOT CRYPTO"
echo "======================================================================"
echo ""

if [ ! -f "$DB_FILE" ]; then
    echo "❌ Base de données non trouvée: $DB_FILE"
    exit 1
fi

OPEN_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM trades WHERE status='OPEN';" 2>/dev/null || echo "0")

if [ "$OPEN_COUNT" -eq 0 ]; then
    echo "ℹ️  Aucune position ouverte pour le moment."
    exit 0
fi

echo "=== Positions ouvertes ($OPEN_COUNT) ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
.width 5 6 6 10 12 8 8 8 8
SELECT 
  id,
  asset,
  side,
  ROUND(entry_price, 2) as "Entry",
  ROUND(size_usd, 2) as "Size USD",
  leverage as "Lev",
  ROUND(stop_loss, 2) as "Stop Loss",
  ROUND(trailing_stop, 2) as "Trail Stop",
  substr(timestamp, 12, 5) as "Time"
FROM trades 
WHERE status='OPEN'
ORDER BY timestamp DESC;
SQL

echo ""
echo "=== Résumé ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
SELECT 
  COUNT(*) as "Total Positions",
  SUM(size_usd) as "Capital Utilisé",
  COUNT(CASE WHEN side='LONG' THEN 1 END) as "Longs",
  COUNT(CASE WHEN side='SHORT' THEN 1 END) as "Shorts"
FROM trades 
WHERE status='OPEN';
SQL

echo ""
echo "=== Détails par asset ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
SELECT 
  asset,
  COUNT(*) as positions,
  SUM(size_usd) as "Total USD",
  ROUND(AVG(bull_score + bear_score), 1) as "Avg Score"
FROM trades 
WHERE status='OPEN'
GROUP BY asset
ORDER BY SUM(size_usd) DESC;
SQL

echo ""
echo "======================================================================"

