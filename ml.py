import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================
DB_FILE = "trading_simulation.db"
MIN_TRADES = 50  # Minimum de trades pour analyse ML
# =======================================================

conn = sqlite3.connect(DB_FILE)

# ==================== 1. CHARGEMENT DONNÉES ====================
print("="*70)
print("📊 ANALYSE DES DONNÉES DE TRADING")
print("="*70)

df_trades = pd.read_sql_query("SELECT * FROM trades WHERE status='CLOSED'", conn)
df_portfolio = pd.read_sql_query("SELECT * FROM portfolio ORDER BY timestamp", conn)

print(f"\n✅ {len(df_trades)} trades chargés")
print(f"✅ {len(df_portfolio)} snapshots portfolio")

if len(df_trades) == 0:
    print("\n⚠️  Aucun trade fermé. Lance d'abord le bot de simulation!")
    exit()

# ==================== 2. STATISTIQUES GLOBALES ====================
print("\n" + "="*70)
print("📈 STATISTIQUES GLOBALES")
print("="*70)

winning_trades = df_trades[df_trades['pnl'] > 0]
losing_trades = df_trades[df_trades['pnl'] <= 0]

print(f"Total trades: {len(df_trades)}")
print(f"Gagnants: {len(winning_trades)} ({len(winning_trades)/len(df_trades)*100:.1f}%)")
print(f"Perdants: {len(losing_trades)} ({len(losing_trades)/len(df_trades)*100:.1f}%)")
print(f"\nPnL Total: ${df_trades['pnl'].sum():.2f}")
print(f"PnL Moyen: ${df_trades['pnl'].mean():.2f}")
print(f"PnL Max: ${df_trades['pnl'].max():.2f}")
print(f"PnL Min: ${df_trades['pnl'].min():.2f}")
print(f"\nDurée moyenne: {df_trades['duration_minutes'].mean():.1f} min")
print(f"Durée max: {df_trades['duration_minutes'].max():.1f} min")

# Stats par asset
print("\n📊 Par Asset:")
asset_stats = df_trades.groupby('asset').agg({
    'pnl': ['count', 'sum', 'mean'],
    'pnl_pct': 'mean'
}).round(2)
print(asset_stats)

# Stats par side
print("\n📊 Par Side:")
side_stats = df_trades.groupby('side').agg({
    'pnl': ['count', 'sum', 'mean'],
    'pnl_pct': 'mean'
}).round(2)
print(side_stats)

# ==================== 3. ANALYSE DES INDICATEURS ====================
print("\n" + "="*70)
print("🔍 ANALYSE DES INDICATEURS (Gagnants vs Perdants)")
print("="*70)

# Indicateurs numériques
numeric_indicators = ['rsi', 'ema8', 'ema21', 'ema50', 'macd', 'macd_histogram',
                     'stoch_k', 'bb_width', 'atr', 'adx', 'cci', 'volume_ratio',
                     'volatility', 'bull_score', 'bear_score']

comparison = pd.DataFrame({
    'Gagnants': winning_trades[numeric_indicators].mean(),
    'Perdants': losing_trades[numeric_indicators].mean(),
    'Différence': winning_trades[numeric_indicators].mean() - losing_trades[numeric_indicators].mean()
})
print(comparison.round(2))

# ==================== 4. VISUALISATIONS ====================
print("\n📊 Génération des graphiques...")

fig, axes = plt.subplots(3, 2, figsize=(15, 12))
fig.suptitle('Analyse des Trades', fontsize=16, fontweight='bold')

# 1. Distribution des PnL
axes[0, 0].hist(df_trades['pnl'], bins=30, alpha=0.7, color='blue', edgecolor='black')
axes[0, 0].axvline(0, color='red', linestyle='--', linewidth=2)
axes[0, 0].set_title('Distribution des PnL ($)')
axes[0, 0].set_xlabel('PnL ($)')
axes[0, 0].set_ylabel('Fréquence')

# 2. PnL cumulé
df_trades_sorted = df_trades.sort_values('timestamp')
df_trades_sorted['cumulative_pnl'] = df_trades_sorted['pnl'].cumsum()
axes[0, 1].plot(df_trades_sorted['cumulative_pnl'], linewidth=2)
axes[0, 1].set_title('PnL Cumulé')
axes[0, 1].set_xlabel('Trade #')
axes[0, 1].set_ylabel('PnL Cumulé ($)')
axes[0, 1].grid(True, alpha=0.3)

# 3. RSI - Gagnants vs Perdants
axes[1, 0].hist(winning_trades['rsi'], bins=20, alpha=0.6, label='Gagnants', color='green')
axes[1, 0].hist(losing_trades['rsi'], bins=20, alpha=0.6, label='Perdants', color='red')
axes[1, 0].set_title('RSI Distribution')
axes[1, 0].set_xlabel('RSI')
axes[1, 0].legend()

# 4. Volume Ratio
axes[1, 1].hist(winning_trades['volume_ratio'], bins=20, alpha=0.6, label='Gagnants', color='green')
axes[1, 1].hist(losing_trades['volume_ratio'], bins=20, alpha=0.6, label='Perdants', color='red')
axes[1, 1].set_title('Volume Ratio')
axes[1, 1].set_xlabel('Volume Ratio')
axes[1, 1].legend()

# 5. Exit Reason
exit_counts = df_trades['exit_reason'].value_counts()
axes[2, 0].bar(exit_counts.index, exit_counts.values, color=['green', 'red', 'orange'])
axes[2, 0].set_title('Raisons de Sortie')
axes[2, 0].set_xlabel('Raison')
axes[2, 0].set_ylabel('Count')
axes[2, 0].tick_params(axis='x', rotation=45)

# 6. Bull Score vs Bear Score
scatter_colors = ['green' if pnl > 0 else 'red' for pnl in df_trades['pnl']]
axes[2, 1].scatter(df_trades['bull_score'], df_trades['bear_score'], 
                   c=scatter_colors, alpha=0.6, s=50)
axes[2, 1].set_title('Bull Score vs Bear Score')
axes[2, 1].set_xlabel('Bull Score')
axes[2, 1].set_ylabel('Bear Score')

plt.tight_layout()
plt.savefig('trading_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Graphiques sauvegardés: trading_analysis.png")

# ==================== 5. MACHINE LEARNING ====================
if len(df_trades) >= MIN_TRADES:
    print("\n" + "="*70)
    print("🤖 ANALYSE MACHINE LEARNING")
    print("="*70)
    
    # Préparation des données
    df_ml = df_trades.copy()
    df_ml['is_winner'] = (df_ml['pnl'] > 0).astype(int)
    
    # Features pour ML
    feature_cols = ['rsi', 'ema8', 'ema21', 'ema50', 'macd', 'macd_signal', 'macd_histogram',
                   'stoch_k', 'stoch_d', 'bb_width', 'atr', 'adx', 'cci', 'roc', 'williams_r',
                   'volume_ratio', 'volatility', 'momentum', 'supertrend_dir',
                   'price_vs_ema8', 'price_vs_ema21', 'price_vs_ema50', 'price_vs_vwap',
                   'bull_score', 'bear_score']
    
    # Enlever les NaN
    df_ml = df_ml.dropna(subset=feature_cols)
    
    X = df_ml[feature_cols]
    y = df_ml['is_winner']
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalisation
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # ===== Random Forest =====
    print("\n🌲 Random Forest Classifier:")
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    rf.fit(X_train_scaled, y_train)
    
    y_pred_rf = rf.predict(X_test_scaled)
    y_proba_rf = rf.predict_proba(X_test_scaled)[:, 1]
    
    print("\nPerformance:")
    print(classification_report(y_test, y_pred_rf, target_names=['Perdant', 'Gagnant']))
    print(f"ROC AUC Score: {roc_auc_score(y_test, y_proba_rf):.3f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n📊 Top 10 Indicateurs les plus importants:")
    print(feature_importance.head(10).to_string(index=False))
    
    # ===== Gradient Boosting =====
    print("\n\n🚀 Gradient Boosting Classifier:")
    gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    gb.fit(X_train_scaled, y_train)
    
    y_pred_gb = gb.predict(X_test_scaled)
    y_proba_gb = gb.predict_proba(X_test_scaled)[:, 1]
    
    print("\nPerformance:")
    print(classification_report(y_test, y_pred_gb, target_names=['Perdant', 'Gagnant']))
    print(f"ROC AUC Score: {roc_auc_score(y_test, y_proba_gb):.3f}")
    
    # ===== Patterns de trading gagnants =====
    print("\n" + "="*70)
    print("🎯 PATTERNS DE TRADES GAGNANTS")
    print("="*70)
    
    # Top 5% des trades les plus profitables
    top_trades = df_trades.nlargest(max(5, len(df_trades)//20), 'pnl')
    
    print("\n📈 Caractéristiques des meilleurs trades:")
    for col in ['rsi', 'volume_ratio', 'adx', 'bull_score', 'bear_score', 'volatility']:
        print(f"{col}: {top_trades[col].mean():.2f} (vs avg: {df_trades[col].mean():.2f})")
    
    # Patterns de trends
    print("\n📊 Trends des trades gagnants:")
    trend_win_rate = winning_trades.groupby(['trend_short', 'trend_medium', 'trend_long']).size()
    if len(trend_win_rate) > 0:
        print(trend_win_rate.sort_values(ascending=False).head())
    
    # Visualisation feature importance
    plt.figure(figsize=(12, 8))
    plt.barh(feature_importance['feature'].head(15), feature_importance['importance'].head(15))
    plt.xlabel('Importance')
    plt.title('Top 15 Indicateurs - Feature Importance (Random Forest)')
    plt.tight_layout()
    plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
    print("\n✅ Feature importance sauvegardée: feature_importance.png")
    
    # ===== Recommandations =====
    print("\n" + "="*70)
    print("💡 RECOMMANDATIONS POUR AMÉLIORER LA STRATÉGIE")
    print("="*70)
    
    # Analyser les indicateurs les plus importants
    top_features = feature_importance.head(5)['feature'].tolist()
    
    print("\n🔥 Focus sur ces 5 indicateurs (les plus prédictifs):")
    for i, feat in enumerate(top_features, 1):
        win_avg = winning_trades[feat].mean()
        lose_avg = losing_trades[feat].mean()
        print(f"{i}. {feat}: Gagnants={win_avg:.2f} vs Perdants={lose_avg:.2f}")
    
    # Analyser les trades perdants
    print("\n⚠️  Principales raisons d'échec:")
    losing_patterns = losing_trades.groupby('exit_reason').agg({
        'pnl': ['count', 'mean']
    })
    print(losing_patterns)
    
    print("\n✅ Suggestions:")
    print("1. Ajuste les seuils MIN_CONFIRMATIONS en fonction du bull_score/bear_score optimal")
    print("2. Évite de trader quand la volatilité est > " + f"{losing_trades['volatility'].quantile(0.75):.2f}")
    print("3. Privilégie les trades avec volume_ratio > " + f"{winning_trades['volume_ratio'].quantile(0.25):.2f}")
    
    if 'adx' in top_features:
        print("4. L'ADX est important: trade uniquement si ADX > " + f"{winning_trades['adx'].median():.0f}")
    
else:
    print(f"\n⚠️  Pas assez de trades ({len(df_trades)}/{MIN_TRADES}) pour l'analyse ML")
    print("   Continue à faire tourner le bot de simulation!")

# ==================== 6. EXPORT POUR ANALYSES EXTERNES ====================
print("\n" + "="*70)
print("💾 EXPORT DES DONNÉES")
print("="*70)

df_trades.to_csv('trades_export.csv', index=False)
print("✅ Trades exportés: trades_export.csv")

df_portfolio.to_csv('portfolio_export.csv', index=False)
print("✅ Portfolio exporté: portfolio_export.csv")

conn.close()
print("\n" + "="*70)
print("✅ ANALYSE TERMINÉE")
print("="*70)