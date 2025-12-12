#!/bin/bash

echo "======================================================================"
echo "📊 TOUS LES INDICATEURS TECHNIQUES PAR TRADE"
echo "======================================================================"
echo ""

# Afficher les indicateurs pour les derniers trades
sqlite3 ~/hyper-bot/trading_simulation.db <<SQL
.mode column
.headers on
.width 5 6 6 8 8 8 8 8 8 8 8 8 8 8 8 8

SELECT 
  id,
  asset,
  side,
  ROUND(rsi, 2) as rsi,
  ROUND(ema8, 2) as ema8,
  ROUND(ema21, 2) as ema21,
  ROUND(ema50, 2) as ema50,
  ROUND(macd, 4) as macd,
  ROUND(stoch_k, 2) as stoch_k,
  ROUND(stoch_d, 2) as stoch_d,
  ROUND(adx, 2) as adx,
  ROUND(cci, 2) as cci,
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
echo "======================================================================"
echo "📋 DÉTAILS COMPLETS PAR TRADE (tous les indicateurs)"
echo "======================================================================"

# Pour chaque trade, afficher tous les indicateurs
for trade_id in $(sqlite3 ~/hyper-bot/trading_simulation.db "SELECT id FROM trades WHERE status='CLOSED' ORDER BY timestamp DESC LIMIT 5;"); do
  echo ""
  echo "--- Trade #$trade_id ---"
  sqlite3 ~/hyper-bot/trading_simulation.db <<SQL
.mode line
SELECT 
  id, asset, side,
  entry_price, exit_price, pnl, pnl_pct,
  duration_minutes, exit_reason,
  timestamp
FROM trades WHERE id=$trade_id;
SQL
  
  echo ""
  echo "📈 Indicateurs de tendance:"
  sqlite3 ~/hyper-bot/trading_simulation.db <<SQL
.mode line
SELECT 
  ROUND(ema8, 2) as EMA_8,
  ROUND(ema21, 2) as EMA_21,
  ROUND(ema50, 2) as EMA_50,
  ROUND(ema200, 2) as EMA_200,
  ROUND(vwap, 2) as VWAP,
  trend_short as "Tendance Court",
  trend_medium as "Tendance Moyen",
  trend_long as "Tendance Long"
FROM trades WHERE id=$trade_id;
SQL
  
  echo ""
  echo "📊 Oscillateurs:"
  sqlite3 ~/hyper-bot/trading_simulation.db <<SQL
.mode line
SELECT 
  ROUND(rsi, 2) as RSI,
  ROUND(stoch_k, 2) as "Stoch %K",
  ROUND(stoch_d, 2) as "Stoch %D",
  ROUND(williams_r, 2) as "Williams %R",
  ROUND(cci, 2) as CCI,
  ROUND(roc, 2) as ROC
FROM trades WHERE id=$trade_id;
SQL
  
  echo ""
  echo "💹 MACD:"
  sqlite3 ~/hyper-bot/trading_simulation.db <<SQL
.mode line
SELECT 
  ROUND(macd, 4) as MACD,
  ROUND(macd_signal, 4) as "MACD Signal",
  ROUND(macd_histogram, 4) as "MACD Histogram"
FROM trades WHERE id=$trade_id;
SQL
  
  echo ""
  echo "📦 Bollinger Bands:"
  sqlite3 ~/hyper-bot/trading_simulation.db <<SQL
.mode line
SELECT 
  ROUND(bb_upper, 2) as "BB Upper",
  ROUND(bb_middle, 2) as "BB Middle",
  ROUND(bb_lower, 2) as "BB Lower",
  ROUND(bb_width, 4) as "BB Width"
FROM trades WHERE id=$trade_id;
SQL
  
  echo ""
  echo "⚡ Autres indicateurs:"
  sqlite3 ~/hyper-bot/trading_simulation.db <<SQL
.mode line
SELECT 
  ROUND(atr, 2) as ATR,
  ROUND(adx, 2) as ADX,
  ROUND(obv, 0) as OBV,
  ROUND(volume_ratio, 2) as "Volume Ratio",
  ROUND(volatility, 2) as Volatility,
  ROUND(momentum, 2) as Momentum,
  ROUND(supertrend, 2) as SuperTrend,
  supertrend_dir as "SuperTrend Dir"
FROM trades WHERE id=$trade_id;
SQL
  
  echo ""
  echo "🎯 Scores et position prix:"
  sqlite3 ~/hyper-bot/trading_simulation.db <<SQL
.mode line
SELECT 
  bull_score as "Bull Score",
  bear_score as "Bear Score",
  ROUND(price_vs_ema8, 2) as "Price vs EMA8",
  ROUND(price_vs_ema21, 2) as "Price vs EMA21",
  ROUND(price_vs_ema50, 2) as "Price vs EMA50",
  ROUND(price_vs_vwap, 2) as "Price vs VWAP"
FROM trades WHERE id=$trade_id;
SQL
  
  echo ""
  echo "======================================================================"
done

echo ""
echo "💾 Pour exporter tous les indicateurs en CSV:"
echo "sqlite3 ~/hyper-bot/trading_simulation.db -header -csv 'SELECT * FROM trades WHERE status=\"CLOSED\"' > trades_indicators.csv"

