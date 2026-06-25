"""
PROJET  : Émergence Énergétique — Quels critères ? Où en est le Congo ?
          Quand peut-il atteindre le statut de pays émergent énergétique ?

Date    : Mai - Juin 2025
Bibliothèques  : Pandas · NumPy · Matplotlib · Seaborn · Scikit-learn


QUESTIONS TRAITÉES :
  1. Quels sont les critères qui définissent un pays "émergent énergétique" ?
  2. Quels points communs partagent 16 pays sélectionnés ?
  3. Où se situe le Congo-Brazzaville par rapport à ces critères ?
  4. Que doit faire le Congo pour atteindre ce statut ?
  5. En combien de temps peut-il y parvenir ? (forecast)

NOTIONS DATA SCIENCE COUVERTES :
  - Appel API Banque Mondiale (requests)
  - Scoring multicritères & normalisation Min-Max
  - Analyse en Composantes Principales (PCA) — scikit-learn
  - Clustering K-Means
  - Régression linéaire pour forecast
  - Visualisations avancées : radar chart, heatmap, scatter annotés
  - Gestion des données manquantes (stratégie de remplacement)

SOURCES :
  [1] Banque Mondiale WDI   https://data.worldbank.org/indicator
  [2] IEA Energy Outlook    https://www.iea.org/reports/africa-energy-outlook-2022
  [3] IEA SDG7 2024         https://www.iea.org/reports/sdg7-data-and-projections
  [4] IRENA Stats 2024      https://www.irena.org/Data/Downloads/IRENASTAT
  [5] Energy for Growth Hub https://energyforgrowth.org (seuil 1000 kWh/hab)
  [6] ONU DESA WPP 2024     https://population.un.org/wpp/
  [7] Ember Climate 2024    https://ember-climate.org/data/
"""


# IMPORTATION DES BIBLIOTHÈQUES

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import requests
import os
import warnings

warnings.filterwarnings('ignore')

# Style global
plt.rcParams['figure.dpi']       = 150
plt.rcParams['font.family']      = 'DejaVu Sans'
plt.rcParams['axes.spines.top']  = False
plt.rcParams['axes.spines.right']= False

OUTPUT_DIR = r'Your folder'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Bibliotheques importees avec SUCCES")
print(f"Pandas {pd.__version__} & NumPy {np.__version__}")


# Récupération des données via l'API Banque Mondiale
# Indicateurs WDI utilisés :
#   EG.ELC.ACCS.ZS   : Accès à l'électricité (% population)
#   EG.USE.ELEC.KH.PC: Consommation élec. par habitant (kWh)
#   EG.ELC.RNEW.ZS   : Part des renouvelables dans la production élec. (%)
#   EG.ELC.LOSS.ZS   : Pertes électriques (% production)
#   NY.GDP.PCAP.CD   : PIB par habitant (USD courants)
#   SP.POP.TOTL      : Population totale
#
# Codes pays : 15 pays émergents énergétiques + Congo-Brazzaville 
#   CG = Congo-Brazzaville     AE = Émirats Arabes Unis      EG = Égypte            ET = Éthiopie
#   GH = Ghana                 IN = Inde                     KE = Kenya             KZ = Kazakhstan 
#   MA = Maroc                 RW = Rwanda                   CL = Chili             TR = Turquie              
#   ZA = Afrique du Sud        BD = Bangladesh               BR = Brésil            VN = Vietnam
#
# API URL : https://api.worldbank.org/v2/country/{code}/indicator/{indic}?format=json

def recuperer_donnees(code_pays: str, indicateur: str,
             debut: int, fin: int) -> dict:
   
    url = (f"https://api.worldbank.org/v2/country/{code_pays}"
           f"/indicator/{indicateur}"
           f"?date={debut}:{fin}&format=json&per_page=200")
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        if len(data) < 2 or not data[1]:
            return {}
        return {
            int(item['date']): item['value']
            for item in data[1]
            if item['value'] is not None
        }
    except Exception:
        return {}


def derniere_valeur(serie: dict) -> float:
    """Retourne la valeur de l'année la plus récente disponible."""
    if not serie:
        return np.nan
    return serie[max(serie.keys())]


def valeur_annee(serie: dict, annee: int) -> float:
    """Retourne la valeur pour une année donnée, ou NaN si absente."""
    return serie.get(annee, np.nan)

# Sélection de 15 pays + Congo-Brazzaville

PAYS = {
    # Pays      : (Nom complet, Continent, Raison du choix)
    'EG' : ('Égypte',              'Afrique',      'Grande puissance énergétique, mix diversifié'),
    'ET' : ('Éthiopie',            'Afrique',      'Grand Barrage Renaissance'),
    'GH' : ('Ghana',               'Afrique',      '89,5% accès 2023, modèle Afrique de l\'Ouest'),
    'KE' : ('Kenya',               'Afrique',      '90% renouvelables, géothermie leader'),
    'MA' : ('Maroc',               'Afrique',      'Leader africain renouvelables, mix solaire+éolien+hydro'),
    'RW' : ('Rwanda',              'Afrique',      'Modèle de politique publique'),
    'ZA' : ('Afrique du Sud',      'Afrique',      'Grande puissance énergétique, mix diversifié'),
    'AE' : ('Émirats Arabes Unis', 'Moyen-Orient', 'Transition rapide vers les renouvelables'),
    'CL' : ('Chili',               'Amérique',     'Potentiel H2 vert'),
    'BD' : ('Bangladesh',          'Asie',         'Accès universel 2023'),
    'BR' : ('Brésil',              'Amérique',     'Leader latino-américain, mix diversifié'),
    'IN' : ('Inde',                'Asie',         'Grand marché, investissements massifs'),
    'KZ' : ('Kazakhstan',           'Asie',        'Accès universel'),
    'TR' : ('Turquie',             'Europe/Asie',  'Accès universel, mix diversifié'),
    'VN' : ('Vietnam',             'Asie',         'Accès universel, modèle mondial'),
    
    # Congo pour comparaison
    'CG' : ('Congo-Brazzaville',   'Afrique',      'Pays analysé — statut à évaluer'),
}

INDICATEURS = {
    'EG.ELC.ACCS.ZS'   : 'acces_pct',
    'EG.USE.ELEC.KH.PC': 'kwh_hab',
    'EG.ELC.RNEW.ZS'   : 'renouv_pct',
    'EG.ELC.LOSS.ZS'   : 'pertes_pct',
    'NY.GDP.PCAP.CD'   : 'pib_hab',
    'SP.POP.TOTL'      : 'population',
}

print("\nRécupération des données API Banque Mondiale...")


# Données réelles 2021 et 2023 extraites del'API de la banque mondiale

donnees_brutes = {
    'EG': {'acces_pct': dict(sorted(recuperer_donnees('EG', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab': dict(sorted(recuperer_donnees('EG', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct': dict(sorted(recuperer_donnees('EG', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct': dict(sorted(recuperer_donnees('EG', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab': dict(sorted(recuperer_donnees('EG', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population': dict(sorted(recuperer_donnees('EG', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'ET': {'acces_pct': dict(sorted(recuperer_donnees('ET', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab': dict(sorted(recuperer_donnees('ET', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct': dict(sorted(recuperer_donnees('ET', 'EG.ELC.RNEW.ZS', debut=2020, fin=2020).items())),
           'pertes_pct': dict(sorted(recuperer_donnees('ET', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab': dict(sorted(recuperer_donnees('ET', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population': dict(sorted(recuperer_donnees('ET', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'GH': {'acces_pct': dict(sorted(recuperer_donnees('GH', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab': dict(sorted(recuperer_donnees('GH', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct': dict(sorted(recuperer_donnees('GH', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct': dict(sorted(recuperer_donnees('GH', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab': dict(sorted(recuperer_donnees('GH', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population': dict(sorted(recuperer_donnees('GH', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'KE': {'acces_pct': dict(sorted(recuperer_donnees('KE', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab': dict(sorted(recuperer_donnees('KE', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct': dict(sorted(recuperer_donnees('KE', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct': dict(sorted(recuperer_donnees('KE', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab': dict(sorted(recuperer_donnees('KE', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population': dict(sorted(recuperer_donnees('KE', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'MA': {'acces_pct': dict(sorted(recuperer_donnees('MA', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab': dict(sorted(recuperer_donnees('MA', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct': dict(sorted(recuperer_donnees('MA', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct': dict(sorted(recuperer_donnees('MA', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab': dict(sorted(recuperer_donnees('MA', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population': dict(sorted(recuperer_donnees('MA', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'RW': {'acces_pct':dict(sorted(recuperer_donnees('RW', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('RW', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('RW', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('RW', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('RW', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('RW', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'ZA': {'acces_pct':dict(sorted(recuperer_donnees('ZA', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('ZA', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('ZA', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('ZA', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('ZA', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('ZA', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'AE': {'acces_pct':dict(sorted(recuperer_donnees('AE', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('AE', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('AE', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('AE', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('AE', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('AE', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'CL': {'acces_pct':dict(sorted(recuperer_donnees('CL', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('CL', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('CL', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('CL', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('CL', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('CL', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'BD': {'acces_pct':dict(sorted(recuperer_donnees('BD', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('BD', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('BD', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('BD', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('BD', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('BD', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'BR': {'acces_pct':dict(sorted(recuperer_donnees('BR', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('BR', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('BR', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('BR', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('BR', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('BR', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},
    
    'IN': {'acces_pct':dict(sorted(recuperer_donnees('IN', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('IN', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('IN', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('IN', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('IN', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('IN', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'KZ': {'acces_pct':dict(sorted(recuperer_donnees('KZ', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('KZ', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('KZ', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('KZ', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('KZ', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('KZ', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'TR': {'acces_pct':dict(sorted(recuperer_donnees('TR', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('TR', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('TR', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('TR', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('TR', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('TR', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},

    'VN': {'acces_pct':dict(sorted(recuperer_donnees('VN', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('VN', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('VN', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('VN', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('VN', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('VN', 'SP.POP.TOTL', debut=2023, fin=2023).items()))},
    
    'CG': {'acces_pct':dict(sorted(recuperer_donnees('CG', 'EG.ELC.ACCS.ZS', debut=2023, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('CG', 'EG.USE.ELEC.KH.PC', debut=2023, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('CG', 'EG.ELC.RNEW.ZS', debut=2021, fin=2021).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('CG', 'EG.ELC.LOSS.ZS', debut=2023, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('CG', 'NY.GDP.PCAP.CD', debut=2023, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('CG', 'SP.POP.TOTL', debut=2023, fin=2023).items()))}

}

# Remplacer la valeur manquante de 2021 par celle de 2020 pour l'Éthiopie
donnees_brutes['ET']['renouv_pct'][2021] = donnees_brutes['ET']['renouv_pct'].get(2020)
# Supprimer l’ancienne clé 2020
donnees_brutes['ET']['renouv_pct'].pop(2020, None) 

# Créer le DataFrame principal
df = pd.DataFrame(donnees_brutes).T
df.index.name = 'code_pays'


# Ajouter les métadonnées (nom, continent, note)
df['nom']       = [PAYS[c][0] for c in df.index]
df['continent'] = [PAYS[c][1] for c in df.index]
df['note']      = [PAYS[c][2] for c in df.index]
df['est_congo'] = df.index == 'CG'

print(f"Dataset chargé : {len(df)} pays × {len(df.columns)} variables")
print(f"\n{'Pays':<25} {'Accès%':>16} {'kWh/hab':>9} {'ENR%':>16} {'Pertes%':>16} {'PIB/hab':>16}")
print("\n")
for code, row in df.iterrows():
    flag = " - CONGO" if code == 'CG' else ""
    print(f"{row['nom']:<25} {row['acces_pct'][2023]:>16} {row['kwh_hab'][2023]:>9} "
          f"{row['renouv_pct'][2021]:>16} {row['pertes_pct'][2023]:>16} {row['pib_hab'][2023]:>16}{flag}")

# DÉFINITION DES PAYS ÉMERGENTS ÉNERGÉTIQUES
# Méthodologie de sélection :
# Un "pays émergent énergétique" est défini ici comme un pays à revenu
# intermédiaire ou faible qui a réalisé des PROGRÈS RAPIDES ET MESURABLES
# sur au moins 4 des 5 critères énergétiques clés dans les 10-15 dernières
# années. Ce n'est PAS une liste de pays déjà développés.

# Défintion et scoring des critères d'émergence énergétique
# Les 5 critères retenus sont fondés sur :
#   - Energy for Growth Hub : seuil 1000 kWh/hab (développement humain)
#   - IEA SDG7 2024 : accès universel = ODD7 cible
#   - IEA Africa Energy Outlook : mix ENR comme indicateur de durabilité
#   - Banque Mondiale : pertes réseau < 15% = efficacité minimale
#   - Définition pays émergent Energy for Growth Hub : PIB/hab > 2500 USD

CRITERES = {
    'acces_pct'  : {'label': 'Accès électricité',        'seuil': 90,    'unite': '%',      'poids': 0.30},
    'kwh_hab'    : {'label': 'Consommation/hab',         'seuil': 1000,  'unite': 'kWh/an', 'poids': 0.25},
    'renouv_pct' : {'label': 'Part renouvelables',       'seuil': 60,    'unite': '%',      'poids': 0.20},
    'pertes_pct' : {'label': 'Pertes réseau (inverser)', 'seuil': 15,    'unite': '%',      'poids': 0.15},
    'pib_hab'    : {'label': 'PIB/habitant',             'seuil': 2500,  'unite': 'USD',    'poids': 0.10},
}
# Note : pour les pertes réseau, un score élevé = mauvais.
# On inversera lors du scoring : score_pertes = 1 - valeur_normalisée

print("\n")
print("CRITÈRES D'ÉMERGENCE ÉNERGÉTIQUE — DÉFINITION")
print("\n")
print(f"\n{'Critère':<28} {'Seuil émergence':>18} {'Poids':>8}")
print("\n")
for col, meta in CRITERES.items():
    seuil_str = f"> {meta['seuil']} {meta['unite']}" if col != 'pertes_pct' else f"< {meta['seuil']} {meta['unite']}"
    print(f"  {meta['label']:<26} {seuil_str:>18} {meta['poids']:>7.0%}")
print("\n")
print("  Somme pondérée sur [0, 1]")
print("  Seuil 'émergent' : score ≥ 0.60")


def calculer_score(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df.copy()
    scaler = MinMaxScaler()  # Normalise chaque colonne entre 0 et 1

    cols_norm = ['acces_pct', 'kwh_hab', 'renouv_pct', 'pertes_pct', 'pib_hab']    
    
    valeurs = df[cols_norm].applymap(
    lambda d: float(list(d.values())[0]) if isinstance(d, dict) else float(d)
    )

    # Normalisation Min-Max
    valeurs_norm = scaler.fit_transform(valeurs.to_numpy())

    df['s_acces']   = valeurs_norm[:, 0]
    df['s_kwh']     = valeurs_norm[:, 1]
    df['s_renouv']  = valeurs_norm[:, 2]
    df['s_pertes']  = 1 - valeurs_norm[:, 3]  # ← INVERSER : moins de pertes = mieux
    df['s_pib']     = valeurs_norm[:, 4]

    # Score composite pondéré
    df['score'] = (
        df['s_acces']  * CRITERES['acces_pct']['poids']   +
        df['s_kwh']    * CRITERES['kwh_hab']['poids']     +
        df['s_renouv'] * CRITERES['renouv_pct']['poids']  +
        df['s_pertes'] * CRITERES['pertes_pct']['poids']  +
        df['s_pib']    * CRITERES['pib_hab']['poids']
    )

    df['statut'] = df['score'].apply(
        lambda s: 'Émergent'     if s >= 0.50 else
                  'En transition' if s >= 0.25 else
                  'Pré-émergent'
    )

    return df.sort_values('score', ascending=False)


df = calculer_score(df)

print("\nCLASSEMENT DES PAYS — Score d'émergence énergétique")
print(f"\n{'Rang':<5} {'Pays':<25} {'Score':>7} {'Statut':<18}")
print("\n")
for rang, (code, row) in enumerate(df.iterrows(), 1):
    flag = " - OBJET D'ÉTUDE" if code == 'CG' else ""
    print(f"  {rang:<3} {row['nom']:<25} {row['score']:>7.3f}  {row['statut']}{flag}")



# ANALYSE DES POINTS COMMUNS — PCA + CLUSTERING

# La PCA (Analyse en Composantes Principales) réduit la dimensionnalité des
# données pour visualiser les groupes de pays dans un espace 2D.
# Le K-Means identifie des clusters (groupes) de pays similaires.

def analyser_clusters(df: pd.DataFrame):
    """
    Réalise une PCA sur les 5 indicateurs normalisés et un clustering K-Means.

    Retourne les coordonnées PCA et les labels de clusters.
    """
    features = ['s_acces', 's_kwh', 's_renouv', 's_pertes', 's_pib']
    X = df[features].values

    # PCA
    # PCA projette les données de 5 dimensions vers 2 dimensions
    # PC1 et PC2 capturent le maximum de variance
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
    variance_expliquee = pca.explained_variance_ratio_

    print(f"\nPCA — Variance expliquée :")
    print(f"PC1 : {variance_expliquee[0]:.1%}")
    print(f"PC2 : {variance_expliquee[1]:.1%}")
    print(f"Total : {sum(variance_expliquee):.1%}")

    # K-Means
    # 3 clusters : émergents avancés / en transition / pré-émergents
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)

    df = df.copy()
    df['pca_x']   = coords[:, 0]
    df['pca_y']   = coords[:, 1]
    df['cluster'] = clusters

    # Points communs par cluster
    print("\nPOINTS COMMUNS PAR GROUPE (K-Means) :")
    for c in sorted(df['cluster'].unique()):
        membres = df[df['cluster'] == c]['nom'].tolist()
        df[["acces_pct","kwh_hab","renouv_pct","pertes_pct"]] = df[["acces_pct","kwh_hab","renouv_pct","pertes_pct"]].applymap(
        lambda d: float(list(d.values())[0]) if isinstance(d, dict) else float(d))
        moy = df[df['cluster'] == c][['acces_pct','kwh_hab','renouv_pct','pertes_pct']].mean()
        print(f"\nGroupe {c+1} : {', '.join(membres)}")
        print(f"Accès moy: {moy['acces_pct']:.0f}% | "
              f"kWh/hab: {moy['kwh_hab']:.0f} | "
              f"ENR: {moy['renouv_pct']:.0f}% | "
              f"Pertes: {moy['pertes_pct']:.0f}%")

    return df, variance_expliquee

df, variance_pca = analyser_clusters(df)



# ANALYSE DU GAP CONGO — Que manque-t-il ?

def analyser_gap_congo(df: pd.DataFrame) -> dict:
    """
    Calcule l'écart entre le Congo et les seuils d'émergence,
    et identifie les actions prioritaires.
    """
    congo = df.loc['CG']

    print("\n")
    print("ANALYSE DU GAP — CONGO-BRAZZAVILLE vs SEUILS D'ÉMERGENCE")
    print("="*65)

    gaps = {}
    for col, meta in CRITERES.items():
        val_congo = congo[col]

        if isinstance(val_congo, dict):
            val_congo = float(list(val_congo.values())[0])
        else:
            val_congo = float(val_congo)

        seuil     = meta['seuil']
        if col == 'pertes_pct':
            gap      = val_congo - seuil          # On veut réduire
            atteint  = val_congo <= seuil
            direction = "↓ réduire à"
        else:
            gap      = seuil - val_congo          # On veut augmenter
            atteint  = val_congo >= seuil
            direction = "↑ atteindre"

        statut = "OK" if atteint else "A améliorer"
        gaps[col] = {
            'valeur_congo': val_congo, 'seuil': seuil,
            'gap': gap, 'atteint': atteint,
            'label': meta['label'], 'unite': meta['unite']
        }

        print(f"\n{statut} {meta['label']}")
        print(f"Congo actuel : {val_congo:.1f} {meta['unite']}")
        print(f"Seuil cible  : {seuil} {meta['unite']}")
        if not atteint:
            print(f"Gap      : {direction} {seuil} {meta['unite']} ({abs(gap):.1f} {meta['unite']} d'écart)")

    # Médiane des pays émergents (≥ 0.60) sur chaque indicateur
    emergents = df[df['score'] >= 0.50].drop('CG', errors='ignore')
    print(f"\nMédiane des pays émergents de référence :")
    for col, meta in CRITERES.items():
        emergents[col] = emergents[col].apply(
        lambda d: float(list(d.values())[0]) if isinstance(d, dict) else float(d))
        med = emergents[col].median()
        print(f"{meta['label']:<28}: {med:.1f} {meta['unite']}")

    return gaps

gaps_congo = analyser_gap_congo(df)


# FORECAST — En combien de temps le Congo peut-il émerger ?
# Méthode : régression linéaire sur les tendances historiques WB (2010-2023)
# pour estimer l'année d'atteinte de chaque seuil.
#
# Données historiques Congo - API Banque Mondiale

HISTORIQUE_CONGO = {
    'acces_pct':dict(sorted(recuperer_donnees('CG', 'EG.ELC.ACCS.ZS', debut=2009, fin=2023).items())),
           'kwh_hab':dict(sorted(recuperer_donnees('CG', 'EG.USE.ELEC.KH.PC', debut=2009, fin=2023).items())),
           'renouv_pct':dict(sorted(recuperer_donnees('CG', 'EG.ELC.RNEW.ZS', debut=2009, fin=2023).items())),
           'pertes_pct':dict(sorted(recuperer_donnees('CG', 'EG.ELC.LOSS.ZS', debut=2009, fin=2023).items())),
           'pib_hab':dict(sorted(recuperer_donnees('CG', 'NY.GDP.PCAP.CD', debut=2009, fin=2023).items())),
           'population':dict(sorted(recuperer_donnees('CG', 'SP.POP.TOTL', debut=2009, fin=2023).items()))
}

SCENARIOS_FORECAST = {
    'tendance_actuelle': {
        'label': 'Tendance actuelle',
        'multiplicateur': 1.0,
        'couleur': '#B71C1C',
        'description': 'Aucune politique supplémentaire',
    },
}


def forecast_indicateur(historique: dict, seuil: float,
                         annee_ref: int = 2023,
                         horizon: int = 2060,
                         multiplicateurs: dict = None) -> dict:
    
    annees = np.array(sorted(historique.keys())).reshape(-1, 1)
    valeurs = np.array([
        float(list(historique[a].values())[0]) if isinstance(historique[a], dict) else float(historique[a])
        for a in sorted(historique.keys())
    ])

    # Régression linéaire sur les données historiques
    reg = LinearRegression()
    reg.fit(annees, valeurs)

    pente_base = reg.coef_[0]   # Variation annuelle historique
    intercept  = reg.intercept_

    resultats = {
        'pente_base' : pente_base,
        'intercept'  : intercept,
        'valeur_2023': historique.get(2023, valeurs[-1]),
        'seuil'      : seuil,
        'scenarios'  : {},
    }

    for nom, multi in (multiplicateurs or {'base': 1.0}).items():
        pente_ajustee = pente_base * multi
        if pente_ajustee <= 0:
            # Indicateur qui doit baisser (pertes réseau) : pente négative voulue
            pente_ajustee = abs(pente_base) * multi * (-1)

        # Générer la trajectoire année par année depuis 2024
        annees_proj = np.arange(annee_ref + 1, horizon + 1)
        valeur_depart = historique.get(annee_ref, valeurs[-1])
        trajectoire = valeur_depart + pente_ajustee * (annees_proj - annee_ref)

        # Trouver l'année d'atteinte du seuil
        annee_atteinte = None
        if pente_base > 0 and seuil > valeur_depart:
            # Progression : chercher quand on dépasse le seuil
            idx = np.where(trajectoire >= seuil)[0]
            if len(idx) > 0:
                annee_atteinte = int(annees_proj[idx[0]])
        elif pente_base < 0 or (pente_base > 0 and seuil < valeur_depart):
            # Déjà au-dessus du seuil, ou besoin de baisser
            idx = np.where(trajectoire <= seuil)[0]
            if len(idx) > 0:
                annee_atteinte = int(annees_proj[idx[0]])

        resultats['scenarios'][nom] = {
            'pente_ajustee'  : pente_ajustee,
            'trajectoire'    : dict(zip(annees_proj.tolist(), trajectoire.tolist())),
            'annee_atteinte' : annee_atteinte,
        }

    return resultats


print("\n")
print("FORECAST — ATTEINTE DES SEUILS D'ÉMERGENCE (Congo)")
print("\n")

forecasts = {}
for indicateur, hist in HISTORIQUE_CONGO.items():
    if indicateur not in CRITERES:
        continue

    seuil = CRITERES[indicateur]['seuil']
    multi_map = {s: v['multiplicateur'] for s, v in SCENARIOS_FORECAST.items()}
    forecasts[indicateur] = forecast_indicateur(
        hist, seuil, multiplicateurs=multi_map
    )

    print(f"\n{CRITERES[indicateur]['label']}")
    print(f"Valeur 2023  : {forecasts[indicateur]['valeur_2023']:.1f} {CRITERES[indicateur]['unite']}")
    print(f"Seuil cible  : {seuil} {CRITERES[indicateur]['unite']}")
    for scenario_nom, scenario_data in forecasts[indicateur]['scenarios'].items():
        label = SCENARIOS_FORECAST[scenario_nom]['label']
        annee = scenario_data['annee_atteinte']
        if annee:
            delai = annee - 2023
            print(f"     {label:<30}: {annee} ({delai} ans)")
        else:
            print(f"     {label:<30}: > 2060 (hors horizon)")


# VISUALISATIONS

C = {
    'vert'    : '#1B5E20', 'vert_clair': '#4CAF50',
    'orange'  : '#E65100', 'orange_clair': '#FF8F00',
    'rouge'   : '#B71C1C', 'rouge_clair': '#EF5350',
    'bleu'    : '#0D47A1', 'bleu_clair': '#42A5F5',
    'violet'  : '#4A148C',
    'or'      : '#F9A825', 'or_clair': '#FFF176',
    'fond'    : '#FAFAFA', 'fond_sombre': '#0A0E1A',
    'gris'    : '#757575', 'gris_clair': '#EEEEEE',
    'congo'   : '#CC0000',
}


def fig1_classement_et_radar(df):
    """
    Figure 1 : Classement scores + Radar chart Congo vs médiane émergents
    """
    fig = plt.figure(figsize=(18, 8))
    fig.patch.set_facecolor(C['fond'])
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.4, 1], wspace=0.35)

    # Panel gauche : classement horizontal
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(C['fond'])

    df_sorted = df.sort_values('score')
    noms    = [f"{'--> ' if c == 'CG' else ''}{r['nom']}" for c, r in df_sorted.iterrows()]
    scores  = df_sorted['score'].values
    couleurs = []
    for code, row in df_sorted.iterrows():
        if code == 'CG':
            couleurs.append(C['congo'])
        elif row['score'] >= 0.60:
            couleurs.append(C['vert'])
        elif row['score'] >= 0.35:
            couleurs.append(C['orange'])
        else:
            couleurs.append(C['rouge'])

    bars = ax1.barh(noms, scores, color=couleurs, alpha=0.85,
                    height=0.65, edgecolor='white', linewidth=0.8)
    for bar, sc in zip(bars, scores):
        ax1.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                 f'{sc:.3f}', va='center', fontsize=9, fontweight='bold')

    ax1.axvline(0.60, color=C['vert'],  ls='--', lw=1.8, alpha=0.7, label='Seuil émergent (0.60)')
    ax1.axvline(0.35, color=C['orange'],ls=':',  lw=1.5, alpha=0.7, label='Seuil transition (0.35)')
    ax1.set_title("Score d'émergence énergétique composite\n(5 critères pondérés — données Banque Mondiale / IEA 2022-2023)",
                  fontweight='bold', fontsize=11, pad=12)
    ax1.set_xlabel("Score normalisé [0 → 1]")
    ax1.legend(fontsize=8, loc='lower right')
    ax1.set_xlim(0, 1.05)

    # Légende couleurs
    patches = [
        mpatches.Patch(color=C['vert'],   label='Émergent (≥ 0.60)'),
        mpatches.Patch(color=C['orange'], label='En transition (≥ 0.35)'),
        mpatches.Patch(color=C['rouge'],  label='Pré-émergent (< 0.35)'),
        mpatches.Patch(color=C['congo'],  label='Congo-Brazzaville'),
    ]
    ax1.legend(handles=patches, fontsize=8, loc='lower right')

    # Panel droit : Radar chart
    ax2 = fig.add_subplot(gs[1], projection='polar')
    ax2.set_facecolor(C['fond'])

    categories = ['Accès\nélectricité', 'kWh/\nhabitant', 'Part\nENR', 'Efficacité\nréseau', 'PIB/\nhabitant']
    N = len(categories)

    # Valeurs normalisées Congo
    congo_vals = [
        df.loc['CG', 's_acces'],
        df.loc['CG', 's_kwh'],
        df.loc['CG', 's_renouv'],
        df.loc['CG', 's_pertes'],
        df.loc['CG', 's_pib'],
    ]

    # Médiane des pays émergents (score ≥ 0.50 hors Congo)
    emerg = df[(df['score'] >= 0.50) & (df.index != 'CG')]
    emerg_vals = [
        emerg['s_acces'].median(),
        emerg['s_kwh'].median(),
        emerg['s_renouv'].median(),
        emerg['s_pertes'].median(),
        emerg['s_pib'].median(),
    ]

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    # Fermer le polygone
    congo_vals += [congo_vals[0]]
    emerg_vals  += [emerg_vals[0]]
    angles      += [angles[0]]

    ax2.plot(angles, emerg_vals, color=C['vert'], lw=2.5, label='Médiane émergents')
    ax2.fill(angles, emerg_vals, color=C['vert'], alpha=0.15)
    ax2.plot(angles, congo_vals, color=C['congo'], lw=2.5, ls='--', label='Congo-Brazzaville')
    ax2.fill(angles, congo_vals, color=C['congo'], alpha=0.20)

    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(categories, fontsize=9)
    ax2.set_ylim(0, 1)
    ax2.set_yticks([0.25, 0.50, 0.75, 1.0])
    ax2.set_yticklabels(['25%', '50%', '75%', '100%'], fontsize=7, color=C['gris'])
    ax2.set_title("Congo vs Médiane émergents\n(scores normalisés [0-1])",
                  fontweight='bold', fontsize=11, pad=20)
    ax2.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=9)
    ax2.grid(color=C['gris'], alpha=0.3)

    plt.suptitle("Analyse d'Émergence Énergétique — 15 pays modèles + Congo-Brazzaville\n"
                 "Sources : Banque Mondiale",
                 fontsize=12, fontweight='bold', y=1.01)

    plt.savefig(f'{OUTPUT_DIR}/01_classement_radar.png',
                dpi=150, bbox_inches='tight', facecolor=C['fond'])
    plt.close()
    print(f"\nFigure 1 sauvegardée : 01_classement_radar.png")


def fig2_heatmap_criteres(df):
    """
    Figure 2 : Heatmap des scores normalisés — matrice pays × critères
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(C['fond'])

    df_sorted = df.sort_values('score', ascending=False)
    cols_scores = ['s_acces', 's_kwh', 's_renouv', 's_pertes', 's_pib']
    labels_cols = ['Accès\nélec.', 'kWh/\nhab.', 'Part\nENR', 'Efficacité\nréseau', 'PIB/\nhab.']

    mat = df_sorted[cols_scores].values
    noms_pays = [f"{'--> ' if c == 'CG' else ''}{r['nom']}" for c, r in df_sorted.iterrows()]

    sns.heatmap(
        mat, ax=ax,
        xticklabels=labels_cols,
        yticklabels=noms_pays,
        cmap='RdYlGn', vmin=0, vmax=1,
        annot=True, fmt='.2f', annot_kws={'size': 10, 'weight': 'bold'},
        linewidths=0.5, linecolor='white',
        cbar_kws={'label': 'Score normalisé [0 = min, 1 = max]', 'shrink': 0.8}
    )

    # Encadrer la ligne Congo en rouge
    idx_congo = list(df_sorted.index).index('CG')
    for col_idx in range(len(cols_scores)):
        ax.add_patch(plt.Rectangle(
            (col_idx, idx_congo), 1, 1,
            fill=False, edgecolor=C['congo'], lw=2.5
        ))

    ax.set_title("Matrice des scores par critère — Comparaison internationale\n"
                 "Le rouge = faible performance · Le vert = forte performance · Congo encadré",
                 fontweight='bold', fontsize=12, pad=15)
    ax.set_xlabel("Critères d'émergence énergétique", fontsize=11)
    ax.tick_params(axis='y', labelsize=10)
    ax.tick_params(axis='x', labelsize=10)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/02_heatmap_criteres.png',
                dpi=150, bbox_inches='tight', facecolor=C['fond'])
    plt.close()
    print(f"Figure 2 sauvegardée : 02_heatmap_criteres.png")


def fig3_pca_clusters(df):
    """
    Figure 3 : Scatter PCA avec clusters colorés
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(C['fond'])
    ax.set_facecolor(C['fond'])

    cluster_colors = {0: C['vert'], 1: C['orange'], 2: C['bleu']}
    cluster_labels = {}

    for code, row in df.iterrows():
        c = row['cluster']
        if c not in cluster_labels:
            cluster_labels[c] = f"Groupe {c+1}"
        color = C['congo'] if code == 'CG' else cluster_colors.get(c, C['gris'])
        size  = 250 if code == 'CG' else 120
        marker = '*' if code == 'CG' else 'o'

        ax.scatter(row['pca_x'], row['pca_y'], color=color, s=size,
                   marker=marker, zorder=5, edgecolors='white', linewidths=0.8)

        offset_x = 0.04 if code != 'CG' else -0.08
        offset_y = 0.04 if code != 'CG' else  0.06
        ax.annotate(
            row['nom'],
            (row['pca_x'] + offset_x, row['pca_y'] + offset_y),
            fontsize=8.5,
            fontweight='bold' if code == 'CG' else 'normal',
            color=C['congo'] if code == 'CG' else C['gris'],
        )

    ax.set_xlabel(f"Composante Principale 1 ({variance_pca[0]:.1%} de variance)", fontsize=11)
    ax.set_ylabel(f"Composante Principale 2 ({variance_pca[1]:.1%} de variance)", fontsize=11)
    ax.set_title(
        "Cartographie des pays — Analyse en Composantes Principales (PCA)\n"
        "Axe horizontal ≈ niveau global d'électrification · Axe vertical ≈ mix ENR vs efficacité",
        fontweight='bold', fontsize=12
    )
    ax.grid(alpha=0.2, color=C['gris'])

    legend_els = [
        plt.scatter([], [], color=C['vert'],   s=80, marker='o', label='Groupe en tranition'),
        plt.scatter([], [], color=C['orange'], s=80, marker='o', label='Groupe pré-émergent'),
        plt.scatter([], [], color=C['bleu'],   s=80, marker='o', label='Groupe émergent'),
        plt.scatter([], [], color=C['congo'],  s=150, marker='*', label='🇨🇬 Congo-Brazzaville'),
    ]
    ax.legend(handles=legend_els, fontsize=9, loc='lower right')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/03_pca_clusters.png',
                dpi=150, bbox_inches='tight', facecolor=C['fond'])
    plt.close()
    print(f"Figure 3 sauvegardée : 03_pca_clusters.png")


def fig4_forecast_dark(forecasts):
    """
    Figure 4 (dark mode) : Trajectoires de forecast par indicateur + année d'atteinte
    """
    indicateurs_plot = {
        'acces_pct' : ('Accès électricité (%)',        51.5,  80,  [2009, 2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]),
        'kwh_hab'   : ('Consommation/hab (kWh/an)',    340,   1000,[2009, 2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]),
        'pertes_pct': ('Pertes réseau (%)',            40.0,  15,  [2009, 2010,2012,2014,2016,2018,2020,2022,2023]),
    }

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    fig.patch.set_facecolor(C['fond_sombre'])

    for ax_idx, (indic, (titre, val_depart, seuil, annees_hist)) in enumerate(indicateurs_plot.items()):
        ax = axes[ax_idx]
        ax.set_facecolor(C['fond_sombre'])

        hist_data = HISTORIQUE_CONGO[indic]
        vals_hist = [hist_data.get(a, np.nan) for a in annees_hist]
        vals_hist_clean = [(a, v) for a, v in zip(annees_hist, vals_hist) if not np.isnan(v)]
        ah, vh = zip(*vals_hist_clean)

        # Données historiques
        ax.plot(ah, vh, color='white', lw=2.5, marker='o', ms=4, label='Réel', zorder=5)

        # Scénarios
        for scen_nom, scen_data in SCENARIOS_FORECAST.items():
            traj = forecasts[indic]['scenarios'][scen_nom]['trajectoire']
            annees_p = sorted(traj.keys())
            vals_p   = [traj[a] for a in annees_p]
            aa_att   = forecasts[indic]['scenarios'][scen_nom]['annee_atteinte']

            ax.plot([2023] + annees_p, [val_depart] + vals_p,
                    color=scen_data['couleur'], lw=2, ls='--',
                    label=f"{scen_data['label']}"
                          f"{' → ' + str(aa_att) if aa_att else ' → >2060'}",
                    alpha=0.9)

            if aa_att and aa_att <= 2060:
                ax.axvline(aa_att, color=scen_data['couleur'], lw=0.8, alpha=0.3)
                ax.text(aa_att, seuil * 1.02,
                        f"{aa_att}", color=scen_data['couleur'],
                        fontsize=7.5, rotation=90, va='bottom', ha='center')

        # Ligne seuil
        ax.axhline(seuil, color=C['or'], ls=':', lw=2, alpha=0.9,
                   label=f'Seuil émergent : {seuil}')
        ax.axvline(2023, color='white', ls='-', lw=0.5, alpha=0.3)

        ax.set_title(titre, color='white', fontweight='bold', fontsize=11, pad=10)
        ax.set_xlabel("Année", color='white', fontsize=10)
        ax.tick_params(colors='white', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#333333')
        ax.legend(fontsize=7, loc='upper left', facecolor='#1A1A2E',
                  edgecolor='#333333', labelcolor='white')
        ax.grid(alpha=0.12, color='white')

    fig.suptitle(
        "Forecast : Trajectoires du Congo-Brazzaville vers l'Émergence Énergétique\n"
        "3 scénarios — Banque Mondiale historique · Régression linéaire",
        color='white', fontsize=13, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/04_forecast_trajectoires.png',
                dpi=150, bbox_inches='tight', facecolor=C['fond_sombre'])
    plt.close()
    print(f"Figure 4 sauvegardée : 04_forecast_trajectoires.png")


def fig5_feuille_de_route(df, gaps_congo):
    """
    Figure 5 : Synthèse visuelle — feuille de route Congo vers émergence
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor(C['fond'])

    # Panel gauche : Gap analysis (barres gap vs atteint)
    ax1 = axes[0]
    ax1.set_facecolor(C['fond'])

    items = list(gaps_congo.items())
    labels_gap = [v['label'] for _, v in items]
    vals_congo = [v['valeur_congo'] for _, v in items]
    seuils     = [v['seuil'] for _, v in items]
    atteints   = [v['atteint'] for _, v in items]

    # Normaliser pour comparaison visuelle
    progress_pct = []
    for col, g in items:
        if col == 'pertes_pct':
            # Pour les pertes : 100% = au seuil (15%), 0% = très élevé (50%+)
            p = max(0, min(100, (50 - g['valeur_congo']) / (50 - 15) * 100))
        else:
            p = min(100, g['valeur_congo'] / g['seuil'] * 100)
        progress_pct.append(p)

    couleurs_bars = [C['vert_clair'] if a else C['rouge_clair'] for a in atteints]
    y_pos = range(len(labels_gap))

    bars1 = ax1.barh(y_pos, progress_pct, color=couleurs_bars, alpha=0.8,
                     height=0.55, edgecolor='white')
    ax1.axvline(100, color=C['or'], ls='--', lw=2, label='Seuil d\'émergence (100%)')

    for i, (bar, pct, atteint, g) in enumerate(zip(bars1, progress_pct, atteints, items)):
        col, meta = g
        statut = "Atteint" if atteint else f"{pct:.0f}% du seuil"
        ax1.text(min(pct, 100) + 1.5, bar.get_y() + bar.get_height()/2.,
                 statut, va='center', fontsize=9,
                 color=C['vert'] if atteint else C['rouge'],
                 fontweight='bold')

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(labels_gap, fontsize=10)
    ax1.set_xlim(0, 140)
    ax1.set_xlabel("% du seuil d'émergence atteint")
    ax1.set_title("État des lieux Congo-Brazzaville\nvs Seuils d'émergence énergétique",
                  fontweight='bold', fontsize=11, pad=12)
    ax1.legend(fontsize=9)

    # anel droit : Timeline des actions prioritaires
    ax2 = axes[1]
    ax2.set_facecolor('#F8F9FA')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')

    
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/05_gap_feuille_de_route.png',
                dpi=150, bbox_inches='tight', facecolor=C['fond'])
    plt.close()
    print(f"Figure 5 sauvegardée : 05_gap_feuille_de_route.png")


print("\nCRÉATION DES VISUALISATIONS...")
fig1_classement_et_radar(df)
fig2_heatmap_criteres(df)
fig3_pca_clusters(df)
fig4_forecast_dark(forecasts)
fig5_feuille_de_route(df, gaps_congo)


# EXPORT DES DONNÉES

def exporter_resultats(df, forecasts, gaps_congo):
    """Exporte tous les résultats en CSV documentés."""

    # CSV 1 : Scores et classement
    df_export = df[['nom', 'continent', 'acces_pct', 'kwh_hab',
                    'renouv_pct', 'pertes_pct', 'pib_hab', 'score', 'statut']].copy()
    df_export.to_csv(f'{OUTPUT_DIR}/scores_emergence_energetique.csv',
                     sep=';', decimal=',', encoding='utf-8-sig')
    print(f"scores_emergence_energetique.csv")

    # CSV 2 : Forecast Congo
    rows_forecast = []
    for indic, fdata in forecasts.items():
        for scen_nom, scen_data in fdata['scenarios'].items():
            rows_forecast.append({
                'indicateur'     : CRITERES[indic]['label'],
                'scenario'       : SCENARIOS_FORECAST[scen_nom]['label'],
                'valeur_2023'    : fdata['valeur_2023'],
                'seuil_cible'    : fdata['seuil'],
                'annee_atteinte' : scen_data['annee_atteinte'] or '>2060',
            })
    pd.DataFrame(rows_forecast).to_csv(
        f'{OUTPUT_DIR}/forecast_congo_emergence.csv',
        sep=';', index=False, encoding='utf-8-sig')
    print(f"forecast_congo_emergence.csv")

    # CSV 3 : Synthèse gap Congo
    rows_gap = [{
        'critere'       : v['label'],
        'valeur_congo'  : v['valeur_congo'],
        'seuil_cible'   : v['seuil'],
        'gap'           : v['gap'],
        'statut'        : 'Atteint' if v['atteint'] else 'À atteindre',
    } for _, v in gaps_congo.items()]
    pd.DataFrame(rows_gap).to_csv(
        f'{OUTPUT_DIR}/gap_analyse_congo.csv',
        sep=';', index=False, encoding='utf-8-sig')
    print(f"gap_analyse_congo.csv")


print("\nEXPORT DES DONNÉES :")
exporter_resultats(df, forecasts, gaps_congo)


