import time
import requests
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import json

# ==================== CONFIGURATION ====================
ASSETS = ["BTC", "ETH", "SOL", "ARB", "MATIC"]  # Cryptos à trader
INITIAL_CAPITAL = 1000         # Capital de simulation
LEVERAGE = 2
RISK_PER_TRADE = 0.01         # 1% risque par trade
LOOP_INTERVAL = 60            # Check toutes les 1 minute
MIN_CONFIRMATIONS = 5         # Signal min 5/7 (réduit pour plus de trades)

# Configuration pour trades de 5min à 2h
STOP_LOSS_PCT = 0.01          # 1% stop loss initial (plus large pour laisser respirer)
MIN_TRADE_DURATION = 5        # Minimum 5 minutes avant de pouvoir fermer (sauf stop loss)
MAX_TRADE_DURATION = 120      # Maximum 2h avant fermeture forcée

TRAILING_CONFIGS = [
    {"min_profit": 0.00, "trail_pct": 0.015},   # 1.5% dès le début
    {"min_profit": 0.015, "trail_pct": 0.012},  # 1.2% à partir de 1.5%
    {"min_profit": 0.03, "trail_pct": 0.010},   # 1% à partir de 3%
    {"min_profit": 0.05, "trail_pct": 0.008},   # 0.8% à partir de 5%
]

DB_FILE = "trading_simulation.db"
# =======================================================

# Initialisation SQLite
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# Création des tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    side TEXT NOT NULL,
    entry_price REAL NOT NULL,
    exit_price REAL,
    size REAL NOT NULL,
    leverage INTEGER,
    pnl REAL,
    pnl_pct REAL,
    duration_minutes INTEGER,
    exit_reason TEXT,
    status TEXT DEFAULT 'OPEN',
    
    -- 30+ Indicateurs au moment de l'entrée
    rsi REAL,
    ema8 REAL,
    ema21 REAL,
    ema50 REAL,
    ema200 REAL,
    macd REAL,
    macd_signal REAL,
    macd_histogram REAL,
    stoch_k REAL,
    stoch_d REAL,
    bb_upper REAL,
    bb_middle REAL,
    bb_lower REAL,
    bb_width REAL,
    atr REAL,
    adx REAL,
    cci REAL,
    roc REAL,
    williams_r REAL,
    obv REAL,
    vwap REAL,
    volume_ratio REAL,
    volatility REAL,
    momentum REAL,
    supertrend REAL,
    supertrend_dir INTEGER,
    price_vs_ema8 REAL,
    price_vs_ema21 REAL,
    price_vs_ema50 REAL,
    price_vs_vwap REAL,
    
    -- Scores des signaux
    bull_score INTEGER,
    bear_score INTEGER,
    
    -- Contexte marché
    trend_short TEXT,
    trend_medium TEXT,
    trend_long TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    total_capital REAL,
    available_capital REAL,
    total_pnl REAL,
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate REAL,
    avg_win REAL,
    avg_loss REAL,
    max_drawdown REAL,
    sharpe_ratio REAL
)
""")

conn.commit()

# Variables globales
portfolio = {
    "capital": INITIAL_CAPITAL,
    "positions": {},  # {asset: {...}}
    "total_pnl": 0,
    "total_trades": 0,
    "winning_trades": 0,
    "losing_trades": 0
}


def get_tradable_assets():
    """Récupère la liste des actifs tradables sur Hyperliquid"""
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "meta"}
        r = requests.post(url, json=payload, timeout=5)
        
        if r.status_code != 200:
            return ASSETS
        
        data = r.json()
        
        if isinstance(data, dict) and "universe" in data:
            universe = data["universe"]
            assets = [a["name"] for a in universe if a.get("maxLeverage", 0) >= 2]
            filtered = [a for a in assets if a in ASSETS]
            return filtered
        else:
            return ASSETS
    except Exception:
        return ASSETS  # Fallback


def get_ohlcv(asset):
    """Récupère les données OHLCV réelles depuis Hyperliquid"""
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = {
            "type": "candleSnapshot",
            "req": {"coin": asset, "interval": "5m", "startTime": 0}
        }
        
        r = requests.post(url, json=payload, timeout=10)
        
        if r.status_code != 200:
            return None
        
        response = r.json()
        
        # L'API Hyperliquid retourne un dictionnaire avec 'data' contenant les bougies
        data = None
        if isinstance(response, dict):
            if 'data' in response:
                data = response['data']
            else:
                # Essayer d'autres clés possibles
                for key in ['candles', 'candle', 'snapshot', 'result']:
                    if key in response:
                        data = response[key]
                        break
        elif isinstance(response, list):
            data = response
        
        if not data or len(data) == 0:
            return None
        
        # Créer le DataFrame
        try:
            if len(data) > 0 and isinstance(data[0], dict):
                mapped_data = []
                for row in data:
                    if isinstance(row, dict):
                        mapped_row = {
                            'timestamp': row.get('t', row.get('timestamp')),
                            'open': row.get('o', row.get('open')),
                            'high': row.get('h', row.get('high')),
                            'low': row.get('l', row.get('low')),
                            'close': row.get('c', row.get('close')),
                            'volume': row.get('v', row.get('volume'))
                        }
                        mapped_data.append(mapped_row)
                
                df = pd.DataFrame(mapped_data)
            else:
                df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        except Exception as e:
            return None
        
        # Vérifier que les colonnes nécessaires existent
        required_cols = ["timestamp", "open", "high", "low", "close", "volume"]
        if not all(col in df.columns for col in required_cols):
            return None
        
        # Convertir en float (sauf timestamp)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df["timestamp"] = pd.to_numeric(df["timestamp"], errors='coerce')
        df = df.dropna()
        
        if len(df) < 50:
            return None
        
        return df.iloc[-300:]  # Garde 300 dernières bougies
        
    except Exception:
        return None
        
    except Exception as e:
        print(f"  ❌ [{asset}] Erreur récupération données: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_all_indicators(df):
    """Calcule 30+ indicateurs techniques"""
    if df is None or len(df) < 50:
        return None
    
    c = df["close"]
    h = df["high"]
    l = df["low"]
    v = df["volume"]
    
    indicators = {"price": c.iloc[-1]}
    
    # === 1. RSI ===
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    indicators["rsi"] = rsi.iloc[-1]
    
    # === 2. EMAs (8, 21, 50, 200) ===
    for period in [8, 21, 50, 200]:
        ema = c.ewm(span=period, adjust=False).mean()
        indicators[f"ema{period}"] = ema.iloc[-1]
        indicators[f"price_vs_ema{period}"] = (c.iloc[-1] - ema.iloc[-1]) / ema.iloc[-1] * 100
    
    # === 3. MACD ===
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    macd_histogram = macd - macd_signal
    indicators["macd"] = macd.iloc[-1]
    indicators["macd_signal"] = macd_signal.iloc[-1]
    indicators["macd_histogram"] = macd_histogram.iloc[-1]
    
    # === 4. Stochastic ===
    low14 = l.rolling(14).min()
    high14 = h.rolling(14).max()
    k = 100 * (c - low14) / (high14 - low14 + 1e-10)
    d = k.rolling(3).mean()
    indicators["stoch_k"] = k.iloc[-1]
    indicators["stoch_d"] = d.iloc[-1]
    
    # === 5. Bollinger Bands ===
    bb_mid = c.rolling(20).mean()
    bb_std = c.rolling(20).std()
    bb_upper = bb_mid + 2 * bb_std
    bb_lower = bb_mid - 2 * bb_std
    indicators["bb_upper"] = bb_upper.iloc[-1]
    indicators["bb_middle"] = bb_mid.iloc[-1]
    indicators["bb_lower"] = bb_lower.iloc[-1]
    indicators["bb_width"] = (bb_upper.iloc[-1] - bb_lower.iloc[-1]) / bb_mid.iloc[-1] * 100
    
    # === 6. ATR (Average True Range) ===
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    indicators["atr"] = atr.iloc[-1]
    
    # === 7. ADX (Average Directional Index) ===
    plus_dm = h.diff().clip(lower=0)
    minus_dm = -l.diff().clip(upper=0)
    tr_sum = tr.rolling(14).sum()
    plus_di = 100 * (plus_dm.rolling(14).sum() / tr_sum)
    minus_di = 100 * (minus_dm.rolling(14).sum() / tr_sum)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-10)
    adx = dx.rolling(14).mean()
    indicators["adx"] = adx.iloc[-1]
    
    # === 8. CCI (Commodity Channel Index) ===
    tp = (h + l + c) / 3
    cci = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std() + 1e-10)
    indicators["cci"] = cci.iloc[-1]
    
    # === 9. ROC (Rate of Change) ===
    roc = ((c - c.shift(10)) / c.shift(10) * 100)
    indicators["roc"] = roc.iloc[-1]
    
    # === 10. Williams %R ===
    williams_r = -100 * (high14 - c) / (high14 - low14 + 1e-10)
    indicators["williams_r"] = williams_r.iloc[-1]
    
    # === 11. OBV (On Balance Volume) ===
    obv = (v * np.sign(c.diff())).cumsum()
    indicators["obv"] = obv.iloc[-1]
    
    # === 12. VWAP ===
    vwap = (v * (h + l + c) / 3).cumsum() / v.cumsum()
    indicators["vwap"] = vwap.iloc[-1]
    indicators["price_vs_vwap"] = (c.iloc[-1] - vwap.iloc[-1]) / vwap.iloc[-1] * 100
    
    # === 13. Volume ===
    vol_avg = v.rolling(20).mean()
    indicators["volume_ratio"] = v.iloc[-1] / vol_avg.iloc[-1]
    
    # === 14. Volatilité ===
    indicators["volatility"] = c.pct_change(fill_method=None).rolling(20).std().iloc[-1] * 100
    
    # === 15. Momentum ===
    indicators["momentum"] = c.iloc[-1] - c.iloc[-10]
    
    # === 16. SuperTrend ===
    hl2 = (h + l) / 2
    upper_band = hl2 + 3 * atr
    lower_band = hl2 - 3 * atr
    supertrend = pd.Series(index=c.index, dtype=float)
    supertrend_dir = pd.Series(index=c.index, dtype=int)
    
    for i in range(1, len(c)):
        if c.iloc[i] > upper_band.iloc[i-1]:
            supertrend.iloc[i] = lower_band.iloc[i]
            supertrend_dir.iloc[i] = 1
        elif c.iloc[i] < lower_band.iloc[i-1]:
            supertrend.iloc[i] = upper_band.iloc[i]
            supertrend_dir.iloc[i] = -1
        else:
            supertrend.iloc[i] = supertrend.iloc[i-1]
            supertrend_dir.iloc[i] = supertrend_dir.iloc[i-1]
    
    indicators["supertrend"] = supertrend.iloc[-1]
    indicators["supertrend_dir"] = supertrend_dir.iloc[-1]
    
    # === 17. Trends (court/moyen/long terme) ===
    indicators["trend_short"] = "UP" if indicators["ema8"] > indicators["ema21"] else "DOWN"
    indicators["trend_medium"] = "UP" if indicators["ema21"] > indicators["ema50"] else "DOWN"
    indicators["trend_long"] = "UP" if indicators["ema50"] > indicators["ema200"] else "DOWN"
    
    return indicators


def get_signal(ind):
    """Génère signal LONG/SHORT avec score"""
    
    bull_conditions = [
        ind["rsi"] < 36,
        ind["ema8"] > ind["ema21"],
        ind["macd"] > ind["macd_signal"] and ind["macd_histogram"] > 0,
        ind["stoch_k"] < 25 and ind["stoch_k"] > ind["stoch_d"],
        ind["price"] < ind["bb_lower"],
        ind["volume_ratio"] > 1.3,
        ind["supertrend_dir"] == 1
    ]
    bull_score = sum(bull_conditions)
    
    bear_conditions = [
        ind["rsi"] > 64,
        ind["ema8"] < ind["ema21"],
        ind["macd"] < ind["macd_signal"] and ind["macd_histogram"] < 0,
        ind["stoch_k"] > 75 and ind["stoch_k"] < ind["stoch_d"],
        ind["price"] > ind["bb_upper"],
        ind["volume_ratio"] > 1.3,
        ind["supertrend_dir"] == -1
    ]
    bear_score = sum(bear_conditions)
    
    signal = None
    if bull_score >= MIN_CONFIRMATIONS:
        signal = "LONG"
    elif bear_score >= MIN_CONFIRMATIONS:
        signal = "SHORT"
    
    return signal, bull_score, bear_score


def open_position_simulation(asset, side, price, indicators):
    """Simule l'ouverture d'une position"""
    # Calcul de la taille basée sur le risque (si stop loss touché, on perd RISK_PER_TRADE % du capital)
    # Formule: size_usd × STOP_LOSS_PCT × LEVERAGE = capital × RISK_PER_TRADE
    # Donc: size_usd = (capital × RISK_PER_TRADE) / (STOP_LOSS_PCT × LEVERAGE)
    size_risk_based = (portfolio["capital"] * RISK_PER_TRADE) / (STOP_LOSS_PCT * LEVERAGE)
    
    # Limiter par le capital disponible avec levier (on ne peut pas trader plus que capital × levier)
    size_max_available = portfolio["capital"] * LEVERAGE
    
    # Prendre le minimum des deux (respecter le risque ET le capital disponible)
    size_usd = min(size_risk_based, size_max_available)
    
    size_asset = size_usd / price
    
    position = {
        "asset": asset,
        "side": side,
        "entry_price": price,
        "entry_time": datetime.now(),
        "size": size_asset,
        "size_usd": size_usd,
        "highest_profit": 0.0,
        "trailing_stop": None,
        "indicators": indicators
    }
    
    portfolio["positions"][asset] = position
    
    # Sauvegarder en BDD
    cursor.execute("""
        INSERT INTO trades (
            asset, timestamp, side, entry_price, size, leverage,
            rsi, ema8, ema21, ema50, ema200,
            macd, macd_signal, macd_histogram,
            stoch_k, stoch_d,
            bb_upper, bb_middle, bb_lower, bb_width,
            atr, adx, cci, roc, williams_r, obv, vwap,
            volume_ratio, volatility, momentum,
            supertrend, supertrend_dir,
            price_vs_ema8, price_vs_ema21, price_vs_ema50, price_vs_vwap,
            bull_score, bear_score,
            trend_short, trend_medium, trend_long
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        asset, datetime.now().isoformat(), side, price, size_asset, LEVERAGE,
        indicators["rsi"], indicators["ema8"], indicators["ema21"], indicators["ema50"], indicators["ema200"],
        indicators["macd"], indicators["macd_signal"], indicators["macd_histogram"],
        indicators["stoch_k"], indicators["stoch_d"],
        indicators["bb_upper"], indicators["bb_middle"], indicators["bb_lower"], indicators["bb_width"],
        indicators["atr"], indicators["adx"], indicators["cci"], indicators["roc"], indicators["williams_r"],
        indicators["obv"], indicators["vwap"], indicators["volume_ratio"], indicators["volatility"], indicators["momentum"],
        indicators["supertrend"], indicators["supertrend_dir"],
        indicators["price_vs_ema8"], indicators["price_vs_ema21"], indicators["price_vs_ema50"], indicators["price_vs_vwap"],
        indicators.get("bull_score", 0), indicators.get("bear_score", 0),
        indicators["trend_short"], indicators["trend_medium"], indicators["trend_long"]
    ))
    conn.commit()
    
    # Calcul du risque réel
    actual_risk_pct = (size_usd * STOP_LOSS_PCT * LEVERAGE / portfolio["capital"]) * 100
    actual_risk_usd = size_usd * STOP_LOSS_PCT * LEVERAGE
    
    # Affichage amélioré du trade ouvert
    print(f"\n{'='*70}")
    print(f"🟢 TRADE OUVERT: {side} {asset}")
    print(f"   Prix d'entrée: ${price:.2f} | Size: {size_asset:.4f} {asset} (${size_usd:.2f})")
    print(f"   Risque souhaité: {RISK_PER_TRADE*100:.1f}% | Risque réel: {actual_risk_pct:.1f}% (${actual_risk_usd:.2f})")
    print(f"   Stop Loss: {STOP_LOSS_PCT*100:.1f}% | Levier: {LEVERAGE}x")
    print(f"   Signal: Bull={indicators.get('bull_score', 0)}/7, Bear={indicators.get('bear_score', 0)}/7")
    print(f"{'='*70}\n")


def close_position_simulation(asset, exit_price, reason):
    """Simule la fermeture d'une position"""
    pos = portfolio["positions"].get(asset)
    if not pos:
        return
    
    entry_price = pos["entry_price"]
    side = pos["side"]
    duration = (datetime.now() - pos["entry_time"]).total_seconds() / 60
    
    # Calcul PnL
    if side == "LONG":
        pnl_pct = (exit_price - entry_price) / entry_price
    else:
        pnl_pct = (entry_price - exit_price) / entry_price
    
    pnl_usd = pnl_pct * pos["size_usd"] * LEVERAGE
    
    # Mise à jour portfolio
    portfolio["capital"] += pnl_usd
    portfolio["total_pnl"] += pnl_usd
    portfolio["total_trades"] += 1
    
    if pnl_usd > 0:
        portfolio["winning_trades"] += 1
    else:
        portfolio["losing_trades"] += 1
    
    # Mise à jour BDD
    cursor.execute("""
        UPDATE trades 
        SET exit_price = ?, pnl = ?, pnl_pct = ?, duration_minutes = ?, 
            exit_reason = ?, status = 'CLOSED'
        WHERE asset = ? AND status = 'OPEN'
        ORDER BY id DESC LIMIT 1
    """, (exit_price, pnl_usd, pnl_pct * 100, duration, reason, asset))
    conn.commit()
    
    win_rate = portfolio["winning_trades"] / portfolio["total_trades"] * 100 if portfolio["total_trades"] > 0 else 0
    
    # Affichage amélioré du trade fermé
    pnl_emoji = "🟢" if pnl_usd > 0 else "🔴"
    duration_str = f"{int(duration)}min" if duration < 60 else f"{int(duration/60)}h{int(duration%60)}min"
    
    print(f"\n{'='*70}")
    print(f"{pnl_emoji} TRADE FERMÉ: {side} {asset}")
    print(f"   Entrée: ${entry_price:.2f} | Sortie: ${exit_price:.2f} | Durée: {duration_str}")
    print(f"   P&L: ${pnl_usd:+.2f} ({pnl_pct*100:+.2f}%) | Raison: {reason}")
    print(f"   💰 Capital: ${portfolio['capital']:.2f} | Win Rate: {win_rate:.1f}% ({portfolio['winning_trades']}/{portfolio['total_trades']})")
    print(f"{'='*70}\n")
    
    del portfolio["positions"][asset]


def check_stop_loss(asset, current_price):
    """Vérifie stop-loss, trailing stop et durée maximale"""
    pos = portfolio["positions"].get(asset)
    if not pos:
        return False
    
    entry_price = pos["entry_price"]
    side = pos["side"]
    duration = (datetime.now() - pos["entry_time"]).total_seconds() / 60
    
    # Vérifier durée maximale (fermeture forcée après 2h)
    if duration >= MAX_TRADE_DURATION:
        close_position_simulation(asset, current_price, f"Durée max ({MAX_TRADE_DURATION}min)")
        return True
    
    # Calcul profit actuel
    if side == "LONG":
        profit_pct = (current_price - entry_price) / entry_price
    else:
        profit_pct = (entry_price - current_price) / entry_price
    
    # Trailing stop dynamique (seulement si durée > MIN_TRADE_DURATION)
    if duration >= MIN_TRADE_DURATION:
        if profit_pct > pos["highest_profit"]:
            pos["highest_profit"] = profit_pct
            trail_distance = next((c["trail_pct"] for c in reversed(TRAILING_CONFIGS) if profit_pct >= c["min_profit"]), TRAILING_CONFIGS[0]["trail_pct"])
            
            if side == "LONG":
                new_trail = current_price * (1 - trail_distance)
            else:
                new_trail = current_price * (1 + trail_distance)
            
            if pos["trailing_stop"] is None:
                pos["trailing_stop"] = new_trail
            else:
                if side == "LONG":
                    pos["trailing_stop"] = max(pos["trailing_stop"], new_trail)
                else:
                    pos["trailing_stop"] = min(pos["trailing_stop"], new_trail)
        
        # Check trailing stop
        if pos["trailing_stop"]:
            if (side == "LONG" and current_price <= pos["trailing_stop"]) or \
               (side == "SHORT" and current_price >= pos["trailing_stop"]):
                close_position_simulation(asset, current_price, "Trailing Stop")
                return True
    
    # Check stop-loss initial (toujours actif)
    initial_stop = entry_price * (1 - STOP_LOSS_PCT) if side == "LONG" else entry_price * (1 + STOP_LOSS_PCT)
    if (side == "LONG" and current_price <= initial_stop) or \
       (side == "SHORT" and current_price >= initial_stop):
        close_position_simulation(asset, current_price, "Stop-Loss Initial")
        return True
    
    return False


def save_portfolio_snapshot():
    """Sauvegarde l'état du portfolio"""
    win_rate = portfolio["winning_trades"] / portfolio["total_trades"] * 100 if portfolio["total_trades"] > 0 else 0
    
    cursor.execute("""
        INSERT INTO portfolio (timestamp, total_capital, available_capital, total_pnl, 
                              total_trades, winning_trades, losing_trades, win_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        portfolio["capital"],
        portfolio["capital"],
        portfolio["total_pnl"],
        portfolio["total_trades"],
        portfolio["winning_trades"],
        portfolio["losing_trades"],
        win_rate
    ))
    conn.commit()


def print_statistics():
    """Affiche les statistiques de trading"""
    cursor.execute("SELECT COUNT(*), AVG(pnl), SUM(pnl) FROM trades WHERE status='CLOSED'")
    total, avg_pnl, sum_pnl = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM trades WHERE status='CLOSED' AND pnl > 0")
    wins = cursor.fetchone()[0]
    
    if total and total > 0:
        print("\n" + "="*70)
        print("📊 STATISTIQUES DE SIMULATION")
        print("="*70)
        print(f"Capital actuel: ${portfolio['capital']:.2f} (Initial: ${INITIAL_CAPITAL})")
        print(f"PnL Total: ${sum_pnl:.2f} ({(sum_pnl/INITIAL_CAPITAL)*100:+.2f}%)")
        print(f"Trades: {total} | Gagnants: {wins} | Win Rate: {wins/total*100:.1f}%")
        print(f"PnL moyen: ${avg_pnl:.2f}")
        print(f"Positions ouvertes: {len(portfolio['positions'])}")
        print("="*70 + "\n")


# ==================== BOUCLE PRINCIPALE ====================
print("="*70)
print("🤖 BOT SIMULATION - Collecte de données ML")
print("="*70)
print(f"Capital: ${INITIAL_CAPITAL} | Assets: {', '.join(ASSETS)}")
print(f"Database: {DB_FILE}")
print("="*70 + "\n")

iteration = 0
while True:
    try:
        iteration += 1
        
        tradable_assets = get_tradable_assets()
        
        # Afficher un header toutes les 10 cycles
        if iteration % 10 == 1:
            cursor.execute("SELECT COUNT(*), SUM(pnl) FROM trades WHERE status='CLOSED'")
            result = cursor.fetchone()
            total_trades = result[0] if result[0] else 0
            total_pnl = result[1] if result[1] else 0.0
            
            print(f"\n{'='*70}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Cycle #{iteration} | Trades fermés: {total_trades} | P&L Total: ${total_pnl:+.2f}")
            print(f"{'='*70}")
        
        # Afficher un message de surveillance au début de chaque cycle
        if iteration % 2 == 0 and len(portfolio["positions"]) == 0:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔍 Analyse des signaux...")
        
        for asset in tradable_assets:
            df = get_ohlcv(asset)
            if df is None:
                continue
            
            indicators = calculate_all_indicators(df)
            if indicators is None:
                continue
            
            signal, bull_score, bear_score = get_signal(indicators)
            indicators["bull_score"] = bull_score
            indicators["bear_score"] = bear_score
            
            current_price = indicators["price"]
            has_position = asset in portfolio["positions"]
            
            # Gestion positions existantes
            if has_position:
                pos = portfolio["positions"][asset]
                duration = (datetime.now() - pos["entry_time"]).total_seconds() / 60
                
                if pos["side"] == "LONG":
                    pnl_pct = (current_price - pos["entry_price"]) / pos["entry_price"] * 100
                else:
                    pnl_pct = (pos["entry_price"] - current_price) / pos["entry_price"] * 100
                
                pnl_usd = pnl_pct * pos["size_usd"] * LEVERAGE / 100
                duration_str = f"{int(duration)}min" if duration < 60 else f"{int(duration/60)}h{int(duration%60)}min"
                pnl_emoji = "🟢" if pnl_usd > 0 else "🔴" if pnl_usd < 0 else "⚪"
                
                print(f"{pnl_emoji} {asset} {pos['side']}: ${current_price:.2f} | P&L: {pnl_pct:+.2f}% (${pnl_usd:+.2f}) | Durée: {duration_str}")
                
                check_stop_loss(asset, current_price)
            else:
                # Afficher les scores même sans position (pour voir ce qui se passe)
                rsi = indicators.get("rsi", 0)
                signal_emoji = "🟢" if signal == "LONG" else "🔴" if signal == "SHORT" else "⚪"
                bull_emoji = "✅" if bull_score >= MIN_CONFIRMATIONS else "⏳"
                bear_emoji = "✅" if bear_score >= MIN_CONFIRMATIONS else "⏳"
                
                # Afficher toutes les 2 itérations pour ne pas surcharger
                if iteration % 2 == 0:
                    print(f"{signal_emoji} {asset}: ${current_price:.2f} | RSI:{rsi:.1f} | Bull:{bull_emoji}{bull_score}/7 | Bear:{bear_emoji}{bear_score}/7 | Signal: {signal or 'AUCUN'}")
            
            # Signaux de trading
            if signal == "LONG" and not has_position:
                open_position_simulation(asset, "LONG", current_price, indicators)
            elif signal == "SHORT" and not has_position:
                open_position_simulation(asset, "SHORT", current_price, indicators)
        
        # Sauvegarde snapshot toutes les 10 itérations
        if iteration % 10 == 0:
            save_portfolio_snapshot()
            print_statistics()
        
        # Ligne vide pour séparer les cycles
        if len(portfolio["positions"]) == 0:
            print()  # Ligne vide pour aération
        
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du bot...")
        save_portfolio_snapshot()
        print_statistics()
        conn.close()
        break
    except Exception as e:
        print(f"❌ ERREUR: {e}")
    
    time.sleep(LOOP_INTERVAL)