#!/bin/bash

DB_FILE="trading_simulation.db"

echo "======================================================================"
echo "📜 HISTORIQUE DES TRADES - BOT CRYPTO"
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
  asset,
  side,
  ROUND(entry_price, 2) as entry,
  ROUND(exit_price, 2) as exit,
  ROUND(pnl, 2) as pnl,
  ROUND(pnl_pct, 2) as "pnl_%",
  duration_minutes as "dur(min)",
  exit_reason as reason,
  substr(timestamp, 1, 16) as date
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
echo "=== Performance par asset ==="
sqlite3 "$DB_FILE" <<SQL
.mode column
.headers on
SELECT 
  asset,
  COUNT(*) as trades,
  ROUND(SUM(pnl), 2) as "P&L Total",
  ROUND(AVG(pnl), 2) as "P&L Moyen",
  COUNT(CASE WHEN pnl > 0 THEN 1 END) as wins
FROM trades 
WHERE status='CLOSED'
GROUP BY asset
ORDER BY SUM(pnl) DESC;
SQL

echo ""
echo "======================================================================"

