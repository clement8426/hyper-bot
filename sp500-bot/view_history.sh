#!/bin/bash

DB_FILE="sp500_daytrading.db"

echo "======================================================================"
echo "📜 HISTORIQUE DES TRADES - BOT S&P 500 DAY TRADING"
echo "======================================================================"
echo ""

if [ ! -f "$DB_FILE" ]; then
    echo "❌ Base de données non trouvée: $DB_FILE"
    exit 1
fi

echo "=== Tous les trades fermés ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
SELECT 
  id,
  symbol,
  side,
  ROUND(entry_price, 2) as entry,
  ROUND(exit_price, 2) as exit,
  ROUND(pnl, 2) as pnl,
  ROUND(opening_score, 0) as score,
  duration_minutes as "dur(min)",
  exit_reason as reason,
  date
FROM trades 
WHERE status='CLOSED'
ORDER BY timestamp DESC
LIMIT 50;
SQL

echo ""
echo "=== Statistiques globales ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
SELECT 
  COUNT(*) as "Total Trades",
  ROUND(SUM(pnl), 2) as "P&L Total",
  ROUND(AVG(pnl), 2) as "P&L Moyen",
  COUNT(CASE WHEN pnl > 0 THEN 1 END) as "Gagnants",
  COUNT(CASE WHEN pnl <= 0 THEN 1 END) as "Perdants",
  ROUND(COUNT(CASE WHEN pnl > 0 THEN 1 END) * 100.0 / COUNT(*), 1) as "Win Rate %"
FROM trades 
WHERE status='CLOSED';
SQL

echo ""
echo "=== Performance quotidienne ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
SELECT 
  date,
  COUNT(*) as trades,
  ROUND(SUM(pnl), 2) as "P&L",
  COUNT(CASE WHEN pnl > 0 THEN 1 END) as wins
FROM trades 
WHERE status='CLOSED'
GROUP BY date
ORDER BY date DESC;
SQL

echo ""
echo "=== Meilleures actions tradées ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
SELECT 
  symbol,
  COUNT(*) as trades,
  ROUND(SUM(pnl), 2) as "P&L Total",
  ROUND(AVG(opening_score), 0) as "Avg Score"
FROM trades 
WHERE status='CLOSED'
GROUP BY symbol
ORDER BY SUM(pnl) DESC
LIMIT 10;
SQL

echo ""
echo "======================================================================"

