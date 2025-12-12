#!/bin/bash

DB_FILE="sp500_daytrading.db"

echo "======================================================================"
echo "📊 POSITIONS OUVERTES - BOT S&P 500 DAY TRADING"
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
.width 6 8 8 10 8 8 8 8 6
SELECT 
  id,
  symbol,
  side,
  ROUND(entry_price, 2) as "Entry",
  shares as "Shares",
  ROUND(entry_price * shares, 2) as "Value",
  ROUND(opening_score, 0) as "Score",
  ROUND(gap_pct, 2) as "Gap%",
  substr(timestamp, 12, 5) as "Time"
FROM trades 
WHERE status='OPEN'
ORDER BY opening_score DESC;
SQL

echo ""
echo "=== Résumé ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
SELECT 
  COUNT(*) as "Total Positions",
  SUM(entry_price * shares) as "Capital Utilisé",
  ROUND(AVG(opening_score), 0) as "Score Moyen",
  COUNT(CASE WHEN side='LONG' THEN 1 END) as "Longs",
  COUNT(CASE WHEN side='SHORT' THEN 1 END) as "Shorts"
FROM trades 
WHERE status='OPEN';
SQL

echo ""
echo "=== Top 5 par score ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
SELECT 
  symbol,
  side,
  ROUND(opening_score, 0) as score,
  ROUND(gap_pct, 2) as "gap%",
  ROUND(volume_ratio, 1) as "vol_x",
  ROUND(first_5min_move, 2) as "5min%"
FROM trades 
WHERE status='OPEN'
ORDER BY opening_score DESC
LIMIT 5;
SQL

echo ""
echo "======================================================================"

