"""
Script pour récupérer la liste complète des actions du S&P 500
depuis Wikipedia et la sauvegarder dans un fichier
"""

import pandas as pd
import json
import requests

def get_sp500_tickers():
    """Récupère la liste des tickers S&P 500 depuis Wikipedia"""
    try:
        # URL de la page Wikipedia du S&P 500
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        
        # Ajouter un user-agent pour éviter le blocage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Récupérer la page HTML
        response = requests.get(url, headers=headers)
        
        # Lire les tables HTML
        tables = pd.read_html(response.text)
        
        # La première table contient les tickers
        df = tables[0]
        
        # Extraire les tickers (colonne "Symbol")
        tickers = df['Symbol'].tolist()
        
        # Nettoyer les tickers (remplacer les points par des tirets pour Yahoo Finance)
        tickers = [ticker.replace('.', '-') for ticker in tickers]
        
        print(f"✅ {len(tickers)} tickers récupérés du S&P 500")
        
        return tickers
    
    except Exception as e:
        print(f"❌ Erreur lors de la récupération: {e}")
        return None


def save_tickers_to_file(tickers, filename="sp500_tickers.json"):
    """Sauvegarde les tickers dans un fichier JSON"""
    with open(filename, 'w') as f:
        json.dump(tickers, f, indent=2)
    print(f"✅ Tickers sauvegardés dans {filename}")


def save_tickers_to_python(tickers, filename="sp500_tickers.py"):
    """Sauvegarde les tickers dans un fichier Python"""
    with open(filename, 'w') as f:
        f.write("# Liste complète des tickers S&P 500\n")
        f.write("# Généré automatiquement depuis Wikipedia\n\n")
        f.write("SP500_TICKERS = [\n")
        for ticker in tickers:
            f.write(f'    "{ticker}",\n')
        f.write("]\n")
    print(f"✅ Tickers sauvegardés dans {filename}")


def display_sample(tickers, n=20):
    """Affiche un échantillon de tickers"""
    print(f"\n📊 Échantillon de {n} tickers:")
    for i, ticker in enumerate(tickers[:n], 1):
        print(f"  {i:2}. {ticker}")
    print(f"  ... ({len(tickers) - n} autres)")


if __name__ == "__main__":
    print("="*70)
    print("📈 RÉCUPÉRATION DE LA LISTE S&P 500")
    print("="*70)
    print()
    
    # Récupérer les tickers
    tickers = get_sp500_tickers()
    
    if tickers:
        # Afficher un échantillon
        display_sample(tickers)
        
        # Sauvegarder dans différents formats
        print()
        save_tickers_to_file(tickers)
        save_tickers_to_python(tickers)
        
        print()
        print("="*70)
        print("✅ TERMINÉ")
        print("="*70)
        print()
        print("Vous pouvez maintenant utiliser ces fichiers :")
        print("  - sp500_tickers.json (format JSON)")
        print("  - sp500_tickers.py (format Python)")
        print()
        print("Pour utiliser dans main_sp500.py :")
        print("  from sp500_tickers import SP500_TICKERS")
        print("  STOCKS = SP500_TICKERS  # ou SP500_TICKERS[:50] pour les 50 premiers")
    else:
        print("❌ Échec de la récupération")

