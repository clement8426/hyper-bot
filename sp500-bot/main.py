import time
import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import pytz

# ==================== CONFIGURATION ====================
# Charger la liste complète du S&P 500
from sp500_tickers import SP500_TICKERS

INITIAL_CAPITAL = 10000       # $10,000
MAX_POSITIONS = 20            # Top 20 actions seulement
LEVERAGE = 1                  # Pas de levier
LOOP_INTERVAL = 180          # Check toutes les 3 minutes

# Horaires day trading
MARKET_OPEN_TIME = "09:30"
ANALYSIS_START_TIME = "09:45"  # Attendre 15 min après ouverture
FORCE_CLOSE_TIME = "15:30"     # Fermer 30 min avant clôture
MAX_TRADE_DURATION = 240       # 4 heures max

# Critères de notation
MIN_SCORE = 60                # Score minimum sur 100 pour trader
STOP_LOSS_PCT = 0.02         # 2% stop loss
TRAILING_STOP_PCT = 0.015    # 1.5% trailing stop

DB_FILE = "sp500_daytrading.db"
# =======================================================

# Initialisation SQLite
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    side TEXT NOT NULL,
    entry_price REAL NOT NULL,
    exit_price REAL,
    shares REAL NOT NULL,
    pnl REAL,
    pnl_pct REAL,
    duration_minutes INTEGER,
    exit_reason TEXT,
    status TEXT DEFAULT 'OPEN',
    
    -- Scores et métriques d'ouverture
    opening_score REAL,
    gap_pct REAL,
    volume_ratio REAL,
    first_5min_move REAL,
    opening_range REAL,
    
    -- Indicateurs techniques
    rsi REAL,
    macd REAL,
    bb_position REAL,
    trend TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS daily_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    symbol TEXT NOT NULL,
    score REAL,
    gap_pct REAL,
    volume_ratio REAL,
    first_5min_move REAL,
    opening_range REAL,
    selected BOOLEAN
)
""")

conn.commit()

portfolio = {
    "capital": INITIAL_CAPITAL,
    "positions": {},
    "total_pnl": 0,
    "total_trades": 0,
    "winning_trades": 0,
    "today_date": None,
    "scan_done": False
}


def get_current_time():
    """Heure actuelle à New York"""
    return datetime.now(pytz.timezone('US/Eastern'))


def is_market_open():
    """Vérifie si le marché est ouvert"""
    now = get_current_time()
    
    if now.weekday() >= 5:  # Weekend
        return False
    
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_open <= now <= market_close


def is_ready_to_scan():
    """Vérifie si on peut scanner (9h45 passé)"""
    now = get_current_time()
    
    if now.weekday() >= 5:
        return False
    
    scan_time = now.replace(hour=9, minute=45, second=0, microsecond=0)
    return now >= scan_time


def should_force_close():
    """Vérifie si on doit fermer toutes les positions (15h30)"""
    now = get_current_time()
    close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return now >= close_time


def get_premarket_close(symbol):
    """Récupère le prix de clôture de la veille"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d", interval="1d")
        if not df.empty and len(df) >= 2:
            return df['Close'].iloc[-2]  # Veille
        return None
    except:
        return None


def get_opening_data(symbol):
    """Récupère les données des 15 premières minutes"""
    try:
        ticker = yf.Ticker(symbol)
        # Récupérer les données d'aujourd'hui en 1 minute
        df = ticker.history(period="1d", interval="1m")
        
        if df.empty or len(df) < 15:
            return None
        
        # Prendre les 15 premières minutes
        opening_df = df.head(15)
        
        data = {
            "symbol": symbol,
            "open_price": opening_df['Open'].iloc[0],
            "current_price": opening_df['Close'].iloc[-1],
            "first_5min_high": opening_df['High'].head(5).max(),
            "first_5min_low": opening_df['Low'].head(5).min(),
            "first_5min_close": opening_df['Close'].iloc[4],
            "volume_15min": opening_df['Volume'].sum(),
            "avg_volume": ticker.info.get('averageVolume', 1),
            "previous_close": get_premarket_close(symbol)
        }
        
        return data
    
    except Exception as e:
        return None


def calculate_opening_score(data):
    """Calcule un score de 0 à 100 basé sur l'ouverture"""
    if not data or not data.get('previous_close'):
        return 0
    
    score = 0
    
    # 1. Gap à l'ouverture (30 points)
    gap_pct = ((data['open_price'] - data['previous_close']) / data['previous_close']) * 100
    data['gap_pct'] = gap_pct
    
    if abs(gap_pct) > 2:  # Gap > 2%
        score += 30
    elif abs(gap_pct) > 1:  # Gap > 1%
        score += 20
    elif abs(gap_pct) > 0.5:  # Gap > 0.5%
        score += 10
    
    # 2. Volume relatif (25 points)
    volume_ratio = data['volume_15min'] / (data['avg_volume'] / 26)  # 26 = 6.5h * 4 (périodes de 15min)
    data['volume_ratio'] = volume_ratio
    
    if volume_ratio > 3:  # 3x le volume normal
        score += 25
    elif volume_ratio > 2:
        score += 20
    elif volume_ratio > 1.5:
        score += 15
    elif volume_ratio > 1:
        score += 10
    
    # 3. Mouvement des 5 premières minutes (25 points)
    first_5min_move = ((data['first_5min_close'] - data['open_price']) / data['open_price']) * 100
    data['first_5min_move'] = first_5min_move
    
    if abs(first_5min_move) > 1:  # Mouvement > 1%
        score += 25
    elif abs(first_5min_move) > 0.5:
        score += 20
    elif abs(first_5min_move) > 0.3:
        score += 15
    
    # 4. Opening range (volatilité initiale) (20 points)
    opening_range = ((data['first_5min_high'] - data['first_5min_low']) / data['open_price']) * 100
    data['opening_range'] = opening_range
    
    if opening_range > 1:  # Range > 1%
        score += 20
    elif opening_range > 0.5:
        score += 15
    elif opening_range > 0.3:
        score += 10
    
    data['score'] = score
    return score


def scan_all_stocks():
    """Scanner tous les 502 tickers et retourner les 20 meilleurs"""
    print("\n" + "="*70)
    print("🔍 SCAN DES 502 ACTIONS DU S&P 500")
    print("="*70)
    print("⏳ Attente 15 min après ouverture (9h45)...")
    print("📊 Analyse des 15 premières minutes de trading...")
    print()
    
    results = []
    today = get_current_time().strftime('%Y-%m-%d')
    
    for i, symbol in enumerate(SP500_TICKERS, 1):
        if i % 50 == 0:
            print(f"   Progression: {i}/{len(SP500_TICKERS)} ({i/len(SP500_TICKERS)*100:.1f}%)")
        
        data = get_opening_data(symbol)
        
        if data:
            score = calculate_opening_score(data)
            
            if score > 0:
                results.append({
                    "symbol": symbol,
                    "score": score,
                    "gap_pct": data.get('gap_pct', 0),
                    "volume_ratio": data.get('volume_ratio', 0),
                    "first_5min_move": data.get('first_5min_move', 0),
                    "opening_range": data.get('opening_range', 0),
                    "current_price": data['current_price']
                })
                
                # Sauvegarder dans la base
                cursor.execute("""
                    INSERT INTO daily_scans 
                    (date, timestamp, symbol, score, gap_pct, volume_ratio, first_5min_move, opening_range, selected)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    today,
                    datetime.now().isoformat(),
                    symbol,
                    score,
                    data.get('gap_pct', 0),
                    data.get('volume_ratio', 0),
                    data.get('first_5min_move', 0),
                    data.get('opening_range', 0),
                    False
                ))
    
    conn.commit()
    
    # Trier par score et prendre les 20 meilleurs
    results.sort(key=lambda x: x['score'], reverse=True)
    top_20 = results[:MAX_POSITIONS]
    
    # Marquer comme sélectionnés
    for stock in top_20:
        cursor.execute("""
            UPDATE daily_scans 
            SET selected = TRUE 
            WHERE date = ? AND symbol = ?
        """, (today, stock['symbol']))
    conn.commit()
    
    # Afficher les résultats
    print()
    print("="*70)
    print(f"🏆 TOP {MAX_POSITIONS} ACTIONS SÉLECTIONNÉES")
    print("="*70)
    print(f"{'Rang':<5} {'Symbol':<8} {'Score':<8} {'Gap%':<10} {'Vol Ratio':<12} {'5min Move%':<12}")
    print("-"*70)
    
    for i, stock in enumerate(top_20, 1):
        print(f"{i:<5} {stock['symbol']:<8} {stock['score']:<8.0f} {stock['gap_pct']:>+8.2f}% {stock['volume_ratio']:>10.1f}x {stock['first_5min_move']:>+10.2f}%")
    
    print("="*70)
    print()
    
    return top_20


def get_current_data(symbol):
    """Récupère les données actuelles pour un ticker"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="5m")
        
        if df.empty or len(df) < 10:
            return None
        
        price = df['Close'].iloc[-1]
        
        # Calcul RSI rapide
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return {
            "price": price,
            "rsi": rsi.iloc[-1] if not rsi.empty else 50,
            "volume": df['Volume'].iloc[-1]
        }
    except:
        return None


def open_position(stock_data):
    """Ouvre une position sur une action"""
    symbol = stock_data['symbol']
    price = stock_data['current_price']
    score = stock_data['score']
    
    # Calculer la taille de position (capital / nombre max de positions)
    position_size_usd = portfolio['capital'] / MAX_POSITIONS
    shares = int(position_size_usd / price)
    
    if shares == 0:
        return
    
    # Déterminer le side (LONG si gap up ou mouvement positif, SHORT sinon)
    if stock_data['gap_pct'] > 0 or stock_data['first_5min_move'] > 0:
        side = "LONG"
    else:
        side = "SHORT"
    
    position = {
        "symbol": symbol,
        "side": side,
        "entry_price": price,
        "entry_time": datetime.now(),
        "shares": shares,
        "size_usd": shares * price,
        "highest_profit": 0.0,
        "trailing_stop": None,
        "score": score
    }
    
    portfolio['positions'][symbol] = position
    
    # Sauvegarder en BDD
    today = get_current_time().strftime('%Y-%m-%d')
    cursor.execute("""
        INSERT INTO trades (
            symbol, date, timestamp, side, entry_price, shares,
            opening_score, gap_pct, volume_ratio, first_5min_move, opening_range
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        symbol, today, datetime.now().isoformat(), side, price, shares,
        score, stock_data['gap_pct'], stock_data['volume_ratio'],
        stock_data['first_5min_move'], stock_data['opening_range']
    ))
    conn.commit()
    
    print(f"\n{'='*70}")
    print(f"🟢 POSITION OUVERTE: {side} {symbol}")
    print(f"   Prix: ${price:.2f} | Actions: {shares} (${shares * price:.2f})")
    print(f"   Score: {score}/100 | Gap: {stock_data['gap_pct']:+.2f}% | Vol: {stock_data['volume_ratio']:.1f}x")
    print(f"{'='*70}\n")


def close_position(symbol, exit_price, reason):
    """Ferme une position"""
    pos = portfolio['positions'].get(symbol)
    if not pos:
        return
    
    entry_price = pos['entry_price']
    side = pos['side']
    shares = pos['shares']
    duration = (datetime.now() - pos['entry_time']).total_seconds() / 60
    
    # Calcul P&L
    if side == "LONG":
        pnl_pct = (exit_price - entry_price) / entry_price
    else:
        pnl_pct = (entry_price - exit_price) / entry_price
    
    pnl_usd = pnl_pct * pos['size_usd']
    
    portfolio['capital'] += pnl_usd
    portfolio['total_pnl'] += pnl_usd
    portfolio['total_trades'] += 1
    
    if pnl_usd > 0:
        portfolio['winning_trades'] += 1
    
    # Mise à jour BDD
    cursor.execute("""
        UPDATE trades 
        SET exit_price = ?, pnl = ?, pnl_pct = ?, duration_minutes = ?, 
            exit_reason = ?, status = 'CLOSED'
        WHERE symbol = ? AND status = 'OPEN'
        ORDER BY id DESC LIMIT 1
    """, (exit_price, pnl_usd, pnl_pct * 100, duration, reason, symbol))
    conn.commit()
    
    win_rate = portfolio["winning_trades"] / portfolio["total_trades"] * 100 if portfolio["total_trades"] > 0 else 0
    pnl_emoji = "🟢" if pnl_usd > 0 else "🔴"
    duration_str = f"{int(duration)}min" if duration < 60 else f"{int(duration/60)}h{int(duration%60)}min"
    
    print(f"\n{'='*70}")
    print(f"{pnl_emoji} POSITION FERMÉE: {side} {symbol}")
    print(f"   Entrée: ${entry_price:.2f} | Sortie: ${exit_price:.2f} | Durée: {duration_str}")
    print(f"   P&L: ${pnl_usd:+.2f} ({pnl_pct*100:+.2f}%) | Raison: {reason}")
    print(f"   💰 Capital: ${portfolio['capital']:.2f} | Win Rate: {win_rate:.1f}%")
    print(f"{'='*70}\n")
    
    del portfolio['positions'][symbol]


def check_exit_conditions(symbol, current_price):
    """Vérifie les conditions de sortie"""
    pos = portfolio['positions'].get(symbol)
    if not pos:
        return False
    
    entry_price = pos['entry_price']
    side = pos['side']
    duration = (datetime.now() - pos['entry_time']).total_seconds() / 60
    
    # Force close en fin de journée
    if should_force_close():
        close_position(symbol, current_price, "Fin de journée (15h30)")
        return True
    
    # Durée maximale
    if duration >= MAX_TRADE_DURATION:
        close_position(symbol, current_price, f"Durée max ({MAX_TRADE_DURATION}min)")
        return True
    
    # Calcul profit
    if side == "LONG":
        profit_pct = (current_price - entry_price) / entry_price
    else:
        profit_pct = (entry_price - current_price) / entry_price
    
    # Trailing stop
    if profit_pct > pos['highest_profit']:
        pos['highest_profit'] = profit_pct
        if side == "LONG":
            pos['trailing_stop'] = current_price * (1 - TRAILING_STOP_PCT)
        else:
            pos['trailing_stop'] = current_price * (1 + TRAILING_STOP_PCT)
    
    if pos['trailing_stop']:
        if (side == "LONG" and current_price <= pos['trailing_stop']) or \
           (side == "SHORT" and current_price >= pos['trailing_stop']):
            close_position(symbol, current_price, "Trailing Stop")
            return True
    
    # Stop-loss initial
    initial_stop = entry_price * (1 - STOP_LOSS_PCT) if side == "LONG" else entry_price * (1 + STOP_LOSS_PCT)
    if (side == "LONG" and current_price <= initial_stop) or \
       (side == "SHORT" and current_price >= initial_stop):
        close_position(symbol, current_price, "Stop-Loss")
        return True
    
    return False


# ==================== BOUCLE PRINCIPALE ====================
print("\n" + "="*70)
print("📈 S&P 500 DAY TRADING BOT - STRATÉGIE OUVERTURE")
print("="*70)
print(f"Capital: ${INITIAL_CAPITAL:,}")
print(f"Max positions: {MAX_POSITIONS}")
print(f"Univers: {len(SP500_TICKERS)} actions")
print(f"Database: {DB_FILE}")
print("="*70)
print()
print("⏰ Horaires:")
print("   - 9h30 : Ouverture du marché")
print("   - 9h45 : Début du scan (attente 15 min)")
print("   - 15h30 : Fermeture forcée de toutes les positions")
print("="*70)
print()

while True:
    try:
        now = get_current_time()
        today = now.strftime('%Y-%m-%d')
        
        # Nouveau jour : reset
        if portfolio['today_date'] != today:
            portfolio['today_date'] = today
            portfolio['scan_done'] = False
            portfolio['capital'] = INITIAL_CAPITAL
            portfolio['total_pnl'] = 0
            portfolio['total_trades'] = 0
            portfolio['winning_trades'] = 0
            portfolio['positions'] = {}
            print(f"\n🌅 Nouveau jour de trading: {today}\n")
        
        # Vérifier si le marché est ouvert
        if not is_market_open():
            print(f"[{now.strftime('%H:%M:%S')}] 💤 Marché fermé. Attente...")
            time.sleep(60)
            continue
        
        # Scanner à 9h45
        if not portfolio['scan_done'] and is_ready_to_scan():
            top_stocks = scan_all_stocks()
            portfolio['scan_done'] = True
            
            # Ouvrir des positions sur les top 20
            for stock in top_stocks:
                if stock['score'] >= MIN_SCORE:
                    open_position(stock)
            
            print(f"\n✅ {len(portfolio['positions'])} positions ouvertes\n")
        
        # Gérer les positions ouvertes
        if portfolio['positions']:
            print(f"[{now.strftime('%H:%M:%S')}] 📊 Suivi des positions ({len(portfolio['positions'])} actives)")
            
            for symbol in list(portfolio['positions'].keys()):
                data = get_current_data(symbol)
                
                if data:
                    pos = portfolio['positions'][symbol]
                    duration = (datetime.now() - pos['entry_time']).total_seconds() / 60
                    
                    if pos['side'] == "LONG":
                        pnl_pct = (data['price'] - pos['entry_price']) / pos['entry_price'] * 100
                    else:
                        pnl_pct = (pos['entry_price'] - data['price']) / pos['entry_price'] * 100
                    
                    pnl_usd = pnl_pct * pos['size_usd'] / 100
                    pnl_emoji = "🟢" if pnl_usd > 0 else "🔴" if pnl_usd < 0 else "⚪"
                    
                    print(f"   {pnl_emoji} {pos['side']:5} {symbol:6} | P&L: ${pnl_usd:+7.2f} ({pnl_pct:+.2f}%) | Durée: {int(duration)}min | Prix: ${data['price']:.2f}")
                    
                    check_exit_conditions(symbol, data['price'])
        
        # Afficher le résumé
        if portfolio['total_trades'] > 0:
            win_rate = portfolio["winning_trades"] / portfolio["total_trades"] * 100
            print(f"\n💰 Capital: ${portfolio['capital']:.2f} | P&L jour: ${portfolio['total_pnl']:+.2f} | Win Rate: {win_rate:.1f}%\n")
        
        time.sleep(LOOP_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du bot...")
        
        # Fermer toutes les positions
        for symbol in list(portfolio['positions'].keys()):
            data = get_current_data(symbol)
            if data:
                close_position(symbol, data['price'], "Arrêt manuel")
        
        print(f"\n💰 Capital final: ${portfolio['capital']:.2f}")
        print(f"📊 P&L total: ${portfolio['total_pnl']:+.2f}")
        conn.close()
        break
    
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        time.sleep(60)

