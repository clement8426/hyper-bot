#!/bin/bash

echo "======================================================================"
echo "📊 HISTORIQUE DES TRADES DEPUIS HIER"
echo "======================================================================"
echo ""

echo "=== Tous les trades fermés ==="
sqlite3 ~/hyper-bot/trading_simulation.db <<EOF
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
  timestamp
FROM trades 
WHERE status='CLOSED' 
ORDER BY timestamp DESC
LIMIT 50;
EOF

echo ""
echo "=== Statistiques globales depuis hier ==="
sqlite3 ~/hyper-bot/trading_simulation.db <<EOF
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
WHERE status='CLOSED' 
  AND datetime(timestamp) >= datetime('now', '-1 day');
EOF

echo ""
echo "=== Par asset ==="
sqlite3 ~/hyper-bot/trading_simulation.db <<EOF
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
  AND datetime(timestamp) >= datetime('now', '-1 day')
GROUP BY asset
ORDER BY SUM(pnl) DESC;
EOF

echo ""
echo "======================================================================"

