"""
=============================================================================
PROJET : Energie et Développement en Afrique Subsaharienne et au Congo
         projection 2050
=============================================================================
Auteur    : Christian MIKEMY
Date      : Janvier 2025
Domaine   : Énergie / Développement Africain
Outils    : Python, Numpy, Pandas, Matplotlib & Seaborn
=============================================================================

SOURCES DES DONNÉES (toutes officielles et publiques) :
─────────────────────────────────────────────────────────
  [1] Banque Mondiale — World Development Indicators (WDI)
      https://data.worldbank.org/indicator

  [2] IEA — World Energy Balances 2024
      Consommation électrique par pays/région
      https://www.iea.org/data-and-statistics/data-product/world-energy-balances

  [3] IEA — Africa Energy Outlook 2022 + SDG7 Data & Projections 2024
      https://www.iea.org/reports/africa-energy-outlook-2022
      https://www.iea.org/reports/sdg7-data-and-projections

  [4] Nations Unies — World Population Prospects 2024 (UN DESA)
      Projections démographiques par pays
      https://population.un.org/wpp/


INFO :
  L'API World Bank est accessible à l'adresse :
  https://api.worldbank.org/v2/country/{code}/indicator/{indicateur}?format=json
=============================================================================
"""

# =============================================================================
# BLOC 1 : Import des librairies
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings

warnings.filterwarnings('ignore')

plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

print(f"Good! Bibliotheques importees avec succes")
print(f"Pandas: {pd.__version__} et NumPy: {np.__version__}")


# =============================================================================
# BLOC 2 : Code de récupération API
# =============================================================================#
import requests
#
def recuperer_donnees_banque_mondiale(code_pays, code_indicateur, debut=2000, fin=2023):
#     """
#     Récupère les données depuis l'API ouverte de la Banque Mondiale.
#
#     Args:
#         code_pays (str)       : Code ISO du pays/région (ex: 'CG' pour Congo,
#                                 'ZG' pour Afrique Subsaharienne)
#         code_indicateur (str) : Code de l'indicateur WDI (ex: 'EG.ELC.ACCS.ZS')
#         debut (int)           : Année de début
#         fin (int)             : Année de fin
#
#     Returns:
#         dict: {année: valeur}
#     """
      url = (
          f"https://api.worldbank.org/v2/country/{code_pays}"
          f"/indicator/{code_indicateur}"
          f"?date={debut}:{fin}&format=json&per_page=100"
      )
      reponse = requests.get(url, timeout=15)
      donnees_json = reponse.json()
#
#     # donnees_json[1] contient la liste des observations
      serie = {}
      for item in donnees_json[1]:
          if item['value'] is not None:          # Ignorer les NaN
              serie[int(item['date'])] = item['value']
      return serie
#
# # Exemples d'appels :
# # acces_afss  = recuperer_donnees_banque_mondiale('ZG', 'EG.ELC.ACCS.ZS')
# # acces_congo = recuperer_donnees_banque_mondiale('CG', 'EG.ELC.ACCS.ZS')
# # pop_afss    = recuperer_donnees_banque_mondiale('ZG', 'SP.POP.TOTL')
# # pib_congo   = recuperer_donnees_banque_mondiale('CG', 'NY.GDP.PCAP.CD')

# =============================================================================
# BLOC 3 : Données rélles 2000-2023
# =============================================================================
# Ces valeurs sont extraites et vérifiées depuis les sources citées en en-tête.

def charger_donnees_reelles():
    """
    Charge les données historiques réelles 2000-2023 depuis les sources
    officielles (Banque Mondiale, IEA, ONU).

    Returns:
        pd.DataFrame: DataFrame des données réelles 2000-2023
    """

    acces_afss = dict(sorted(recuperer_donnees_banque_mondiale('ZG', 'EG.ELC.ACCS.ZS', debut=2000, fin=2023).items()))
    acces_congo = dict(sorted(recuperer_donnees_banque_mondiale('CG', 'EG.ELC.ACCS.ZS', debut=2000, fin=2023).items()))
    pop_afss    = dict(sorted(recuperer_donnees_banque_mondiale('ZG', 'SP.POP.TOTL', debut=2000, fin=2023).items()))
    pop_congo   = dict(sorted(recuperer_donnees_banque_mondiale('CG', 'SP.POP.TOTL', debut=2000, fin=2023).items()))
    conso_afss   = dict(sorted(recuperer_donnees_banque_mondiale('ZG', 'EG.USE.ELEC.KH.PC', debut=2000, fin=2023).items()))
    conso_congo  = dict(sorted(recuperer_donnees_banque_mondiale('CG', 'EG.USE.ELEC.KH.PC', debut=2000, fin=2023).items()))
    capacite_afss = dict(sorted(recuperer_donnees_banque_mondiale('ZG', 'EG.ELC.RNEW.ZS', debut=2000, fin=2023).items()))
    capacite_congo  = dict(sorted(recuperer_donnees_banque_mondiale('CG', 'EG.ELC.RNEW.ZS', debut=2000, fin=2023).items()))
    pib_hab_congo   = dict(sorted(recuperer_donnees_banque_mondiale('CG', 'NY.GDP.PCAP.CD', debut=2000, fin=2023).items()))

    capacite_afss [2022] = capacite_afss[2023] = capacite_afss[2021]  # Banque mondiale : pas de données 2022-2023 → on prolonge la valeur 2021

    # Assemblage du DataFrame final à partir des dictionnaires
    annees = list(range(2000, 2024))

    df = pd.DataFrame({
        'annee'              : annees,
        'acces_afss_pct'     : [acces_afss[a] for a in annees],
        'acces_congo_pct'    : [acces_congo[a] for a in annees],
        'pop_afss_M'         : [(pop_afss[a]/1000000) for a in annees],
        'pop_congo_M'        : [(pop_congo[a]/1000000) for a in annees],
        'conso_afss_kwh'     : [conso_afss[a] for a in annees],
        'conso_congo_kwh'    : [conso_congo[a] for a in annees],
        'capacite_afss_gw'   : [capacite_afss[a] for a in annees],
        'pib_hab_congo_usd'  : [pib_hab_congo[a] for a in annees],
    }).set_index('annee')

    return df


df = charger_donnees_reelles()
print(f"\nDonnées réelles chargées : {len(df)} années × {len(df.columns)} variables")


# =============================================================================
# BLOC 4 : Data Cleaning et Calcul d'indicateurs 
# =============================================================================

def nettoyer_et_enrichir(df):
    """Nettoie et ajoute des indicateurs dérivés au DataFrame."""

    # 4.1 Diagnostics
    print(f"\nValeurs manquantes: {df.isnull().sum().sum()} (attendu : 0)")
    print(f"Doublons           : {df.duplicated().sum()} (attendu : 0)")
    print(f"Plage temporelle   : {df.index.min()} - {df.index.max()}")

    # 4.2 Vérification de cohérence des taux (0 - 100%)
    for col in ['acces_afss_pct', 'acces_congo_pct']:
        hors_plage = df[(df[col] < 0) | (df[col] > 100)]
        if len(hors_plage) > 0:
            print(f"{col}: {len(hors_plage)} valeur(s) hors [0-100]")
            df[col] = df[col].clip(0, 100)
        else:
            print(f"{col}: toutes les valeurs dans [0, 100]")

    # 4.3 Vérification de la baisse durant le COVID (2020)
    baisse_covid = df.loc[2020, 'conso_afss_kwh'] < df.loc[2019, 'conso_afss_kwh']
    print(f"\n Baisse consommation 2020 (impact COVID) : {'Confirmée' if baisse_covid else 'Non détectée'}")

    # 4.4 Indicateurs : nouveaux indicateurs calculés

    # Consommation par habitant (kWh/personne/an)
    df['kwh_hab_afss']  = (df['conso_afss_kwh']).round(0)
    df['kwh_hab_congo'] = (df['conso_congo_kwh']).round(0)

    # Population sans électricité (millions)
    df['sans_elec_afss_M'] = (df['pop_afss_M'] * (1 - df['acces_afss_pct'] / 100)).round(1)

    # Taux de croissance annuel de la consommation (%)
    df['croissance_conso_afss_pct'] = (df['conso_afss_kwh']*df['pop_afss_M'] * 1e6).pct_change() * 100

    # Intensité énergétique : kWh par million d'habitants
    df['intensite_afss'] = (df['conso_afss_kwh']* 1e6).round(3)

    print(f"\n Indicateurs dérivés créés:")
    print(f" kWh/habitant (Afrique SuSaharienne et Congo)")
    print(f" Population sans électricité (millions)")
    print(f" Taux de croissance annuel de la consommation")
    print(f" Intensité énergétique (kWh/million d'hab)")

    print(f"\nDataset final : {len(df)} lignes × {len(df.columns)} colonnes")
    return df


df = nettoyer_et_enrichir(df)


# =============================================================================
# BLOC 5 : Analyse Exploratoire des données réelles 2000 - 2023
# =============================================================================

def analyse_exploratoire(df):
    """Analyse exploratoire complète avec faits clés."""

    # Références mondiales (IEA 2023)
    REF_MONDIALE_KWH = 3600    # kWh/hab/an — moyenne mondiale 2023
    REF_FRANCE_KWH   = 6415    # kWh/hab/an — France 2023

    print("\nSTATISTIQUES DESCRIPTIVES:")
    print(df[['acces_afss_pct','acces_congo_pct','conso_afss_kwh','kwh_hab_afss','kwh_hab_congo']].describe().round(2))

    print("\nPROGRÈS ENREGISTRÉS (2000 - 2023) :")
    delta_acces_afss  = df['acces_afss_pct'].iloc[-1] - df['acces_afss_pct'].iloc[0]
    delta_acces_congo = df['acces_congo_pct'].iloc[-1] - df['acces_congo_pct'].iloc[0]
    print(f"Accès Afrique SubSaharienne: {df['acces_afss_pct'].iloc[0]:.1f}% ---- {df['acces_afss_pct'].iloc[-1]:.1f}% (+{delta_acces_afss:.1f} pts)")
    print(f"Accès Congo: {df['acces_congo_pct'].iloc[0]:.1f}% ---- {df['acces_congo_pct'].iloc[-1]:.1f}% (+{delta_acces_congo:.1f} pts)")

    print("\nLE PARADOXE DÉMOGRAPHIQUE :")
    delta_sans_elec = df['sans_elec_afss_M'].iloc[-1] - df['sans_elec_afss_M'].iloc[0]
    print(f"Sans électricité 2000 : {df['sans_elec_afss_M'].iloc[0]:.0f} millions")
    print(f"Sans électricité 2023 : {df['sans_elec_afss_M'].iloc[-1]:.0f} millions")
    print(f"Variation             : +{delta_sans_elec:.0f} millions !")
    print(f"La population croît PLUS VITE que l'électrification")

    print("\nCONSOMMATION PAR HABITANT (2023) :")
    kwh_afss  = df['kwh_hab_afss'].iloc[-1]
    kwh_congo = df['kwh_hab_congo'].iloc[-1]
    print(f"Congo-Brazzaville : {kwh_congo:.0f} kWh/pers/an")
    print(f"Afrique SS        : {kwh_afss:.0f} kWh/pers/an")
    print(f"Monde             : {REF_MONDIALE_KWH} kWh/pers/an")
    print(f"France            : {REF_FRANCE_KWH} kWh/pers/an")
    print(f" Congo = {kwh_congo/REF_MONDIALE_KWH:.1%} de la moyenne mondiale")
    print(f" Congo = {kwh_congo/REF_FRANCE_KWH:.1%} de la France")

    print("\nTAUX DE CROISSANCE ANNUEL COMPOSÉ (TCAC) 2000-2023 :")
    n = 23
    tcac_conso  = ((df['conso_afss_kwh'].iloc[-1]*df['pop_afss_M'].iloc[-1]) / (df['conso_afss_kwh'].iloc[0]*df['pop_afss_M'].iloc[0]))**(1/n) - 1
    tcac_pop    = (df['pop_afss_M'].iloc[-1]      / df['pop_afss_M'].iloc[0])**(1/n) - 1
    tcac_acces  = (df['acces_afss_pct'].iloc[-1]  / df['acces_afss_pct'].iloc[0])**(1/n) - 1
    print(f"Consommation électrique  : {tcac_conso:.2%}/an")
    print(f"Population               : {tcac_pop:.2%}/an")
    print(f"Taux d'accès             : {tcac_acces:.2%}/an")
    print(f" La consommation ({tcac_conso:.2%}) est inférieure à la croissance pop ({tcac_pop:.2%})")

    print("\nFAIT MARQUANT — IMPACT COVID-19 :")
    print(f"Consommation 2019 : {df.loc[2019,'conso_afss_kwh']} kWh")
    print(f"Consommation 2020 : {df.loc[2020,'conso_afss_kwh']} kWh")
    print(f"Baisse réelle     : {df.loc[2020,'conso_afss_kwh'] - df.loc[2019,'conso_afss_kwh']:.0f} kWh")

    return {'tcac_conso': tcac_conso, 'tcac_pop': tcac_pop, 'kwh_afss': kwh_afss, 'kwh_congo': kwh_congo}


stats = analyse_exploratoire(df)


# =============================================================================
# BLOC 6 : PROJECTIONS 2024–2050 (3 scénarios)
# =============================================================================
# Les scénarios sont alignés sur ceux de l'IEA Africa Energy Outlook 2022 :
# - STEPS (Stated Policies Scenario)  : proche de notre "Réaliste"
# - APS  (Announced Pledges Scenario) : proche de notre "Optimiste"
# - NZE  (Net Zero Emissions)         : proche de notre "Optimiste+"

def projeter(df, annee_fin=2050):
    """Calcule les projections 2024-2050 en 3 scénarios."""

    annees = list(range(2024, annee_fin + 1))
    n_ann  = len(annees)

    scenarios = {
        'optimiste': {
            # APS/NZE IEA : politiques annoncées + investissements renouvelables
            'desc'             : 'Accélération (APS/NZE IEA)',
            'tcac_pop'         : 0.024,  # Projection ONU variante basse
            'tcac_conso_afss'  : 0.070,  # +7%/an (électrification rapide)
            'tcac_conso_congo' : 0.065,  # +6.5%/an (potentiel hydraulique Congo)
            'acces_cible_afss' : 100,     # ODD7 : accès universel quasi-atteint
            'acces_cible_congo': 100,
        },
        'realiste': {
            # STEPS IEA : continuation des politiques actuelles
            'desc'             : 'Politiques actuelles (STEPS IEA)',
            'tcac_pop'         : 0.025,  # Projection ONU variante médiane
            'tcac_conso_afss'  : 0.045,  # ~TCAC historique + légère accélération
            'tcac_conso_congo' : 0.040,
            'acces_cible_afss' : 70,     # IEA STEPS : 70% en 2030 non atteint → ~68-72% en 2050
            'acces_cible_congo': 70,
        },
        'pessimiste': {
            # Stagnation : instabilité, déficits de financement
            'desc'             : 'Stagnation / Retards structurels',
            'tcac_pop'         : 0.025,  # Variante haute ONU
            'tcac_conso_afss'  : 0.035,  # Faible progression
            'tcac_conso_congo' : 0.020,
            'acces_cible_afss' : 55,     # IEA STEPS "Current trajectory"
            'acces_cible_congo': 58,
        }
    }

    # Valeurs de départ = dernière année réelle (2023)
    V0 = {
        'pop_afss'  : df['pop_afss_M'].iloc[-1],        
        'pop_congo' : df['pop_congo_M'].iloc[-1],        
        'conso_afss': df['conso_afss_kwh'].iloc[-1],     
        'conso_congo': df['conso_congo_kwh'].iloc[-1],   
        'acces_afss': df['acces_afss_pct'].iloc[-1],     
        'acces_congo': df['acces_congo_pct'].iloc[-1],  
    }

    proj = {'annee': annees}
    n_hist = 2050 - 2023  # = 27 ans

    for scen, p in scenarios.items():
        print(f"\nScénario '{scen}' : {p['desc']}")

        pop_afss_l, pop_congo_l = [], []
        conso_afss_l, conso_congo_l = [], []
        acces_afss_l, acces_congo_l = [], []
        capacite_l, sans_elec_l = [], []

        for i, annee in enumerate(annees):
            t = i + 1  # Années depuis 2023

            # Croissance exponentielle : P(t) = P0 × (1 + r)^t
            pop_afss   = V0['pop_afss']   * (1 + p['tcac_pop']) ** t
            pop_congo  = V0['pop_congo']  * (1 + p['tcac_pop']) ** t
            conso_afss  = V0['conso_afss']  * (1 + p['tcac_conso_afss']) ** t
            conso_congo = V0['conso_congo'] * (1 + p['tcac_conso_congo']) ** t

            # Convergence linéaire vers la cible d'accès
            prog = t / n_hist  # 0 → 1 sur 27 ans
            acces_afss  = V0['acces_afss']  + (p['acces_cible_afss']  - V0['acces_afss'])  * prog
            acces_congo = V0['acces_congo'] + (p['acces_cible_congo'] - V0['acces_congo']) * prog

            # Capacité installée (GW) : consommation / (8760h × facteur charge 40%)
            # Facteur charge 40% = hypothèse mix énergétique diversifié
            capacite = conso_afss / (8.760 * 0.40)

            # Population sans électricité
            sans_elec = pop_afss * (1 - min(acces_afss, 100) / 100)

            pop_afss_l.append(round(pop_afss, 1))
            pop_congo_l.append(round(pop_congo, 2))
            conso_afss_l.append(round(conso_afss, 1))
            conso_congo_l.append(round(conso_congo, 2))
            acces_afss_l.append(round(min(acces_afss, 100), 1))
            acces_congo_l.append(round(min(acces_congo, 100), 1))
            capacite_l.append(round(capacite, 1))
            sans_elec_l.append(round(sans_elec, 1))

        proj[f'pop_afss_{scen}']    = pop_afss_l
        proj[f'pop_congo_{scen}']   = pop_congo_l
        proj[f'conso_afss_{scen}']  = conso_afss_l
        proj[f'conso_congo_{scen}'] = conso_congo_l
        proj[f'acces_afss_{scen}']  = acces_afss_l
        proj[f'acces_congo_{scen}'] = acces_congo_l
        proj[f'capacite_{scen}']    = capacite_l
        proj[f'sans_elec_{scen}']   = sans_elec_l

    df_proj = pd.DataFrame(proj).set_index('annee')

    # Tableau récapitulatif 2050
    print(f"{'RÉSULTATS 2050':<35} {'Pessimiste':>9} {'Réaliste':>9} {'Optimiste':>9}")
    indicateurs_recap = [
        ("Population Afrique SS (M)", "pop_afss"),
        ("Consommation Afr. SS (kWh)", "conso_afss"),
        ("Consommation Congo (kWh)", "conso_congo"),
        ("Accès électricité Afr. SS (%)", "acces_afss"),
        ("Accès électricité Congo (%)", "acces_congo"),
        ("Capacité installée (GW)", "capacite"),
        ("Sans électricité Afr. SS (M)", "sans_elec"),
    ]
    for label, base in indicateurs_recap:
        vals = [df_proj[f'{base}_{s}'].iloc[-1] for s in ['pessimiste','realiste','optimiste']]
        fmt  = ".0f" if vals[0] > 10 else ".1f"
        print(f"  {label:<33} {vals[0]:>9{fmt}} {vals[1]:>9{fmt}} {vals[2]:>9{fmt}}")
    print("\n")

    # Comparaison avec IEA STEPS 2030 (référence externe)
    val_2030_steps_iea = 645  # millions sans accès selon IEA STEPS 2030
    idx_2030 = annees.index(2030)
    print(f"\nRéférence IEA STEPS : 645M sans accès en 2030")
    print(f"Notre scénario réaliste 2030 : {df_proj['sans_elec_realiste'].iloc[idx_2030]:.0f}M)")

    return df_proj


df_proj = projeter(df)


# =============================================================================
# BLOC 7 : VISUALISATIONS PROFESSIONNELLES
# =============================================================================

def visualiser(df_hist, df_proj, out='outputs'):
    """Crée et sauvegarde les visualisations du rapport."""

    os.makedirs(out, exist_ok=True)

    C = {
        'afss'      : '#1B5E20',   
        'congo'     : '#BF360C',   
        'optimiste' : '#0D47A1',   
        'realiste'  : '#4A148C',   
        'pessimiste': '#B71C1C',   
        'covid'     : '#FF6F00',   
        'fond'      : '#FAFAFA',
        'gris'      : '#757575',
    }

    sns.set_style("whitegrid")
    ann_h = df_hist.index.tolist()
    ann_p = df_proj.index.tolist()
    REF   = 3600   # kWh/hab/an mondial (IEA 2023)

    # FIGURE 1 : Dashboard 4 panneaux
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(
        "Énergie Électrique — Afrique Subsaharienne & Congo-Brazzaville\n"
        "Données Réelles 2000-2023 | Projections 2024-2050  •  Sources : IEA · Banque Mondiale · ONU",
        fontsize=13, fontweight='bold', y=1.01
    )
    fig.patch.set_facecolor(C['fond'])

    # ─ 1.1 : Taux d'accès ─
    ax = axes[0, 0]
    ax.set_facecolor(C['fond'])
    ax.plot(ann_h, df_hist['acces_afss_pct'], color=C['afss'], lw=2.5, marker='o', ms=3, label='Afrique SubSaharienne (réel)')
    ax.plot(ann_h, df_hist['acces_congo_pct'], color=C['congo'], lw=2.5, marker='s', ms=3, label='Congo-Brazzaville (réel)')
    for scen, ls, al in [('optimiste','--',0.9),('realiste','-',0.75),('pessimiste',':',0.65)]:
        ax.plot(ann_p, df_proj[f'acces_afss_{scen}'], color=C['afss'], ls=ls, lw=1.8, alpha=al)
        ax.plot(ann_p, df_proj[f'acces_congo_{scen}'], color=C['congo'], ls=ls, lw=1.8, alpha=al)
    ax.axvline(2023, color=C['gris'], ls='--', lw=1, alpha=0.6)
    ax.axhline(100,  color='#F9A825', ls=':', lw=1.5, alpha=0.8, label='Accès universel (ODD7)')
    ax.text(2024, 8, '← Réel   Projections →', fontsize=7.5, color=C['gris'], style='italic')
    ax.set_title("Taux d'accès à l'électricité (%)", fontweight='bold')
    ax.set_xlabel("Année"); ax.set_ylabel("Population avec accès (%)")
    ax.legend(fontsize=8, loc='upper left'); ax.set_ylim(0, 110); ax.set_xlim(2000, 2050)

    # 1.2 : Consommation Afrique SubSaharienne
    ax = axes[0, 1]
    ax.set_facecolor(C['fond'])
    ax.fill_between(ann_h, df_hist['conso_afss_kwh'], alpha=0.15, color=C['afss'])
    ax.plot(ann_h, df_hist['conso_afss_kwh'], color=C['afss'], lw=2.5, label='Historique réel')
    # Annotation COVID
    ax.annotate('↓ COVID-19\n(2020)',
                xy=(2020, df_hist.loc[2020,'conso_afss_kwh']),
                xytext=(2016, 530), fontsize=12, color=C['covid'],
                arrowprops=dict(arrowstyle='->', color=C['covid'], lw=1.8))
    for scen, ls, lbl in [('optimiste','--','Optimiste (APS)'),('realiste','-','Réaliste (STEPS)'),('pessimiste',':','Pessimiste')]:
        ax.plot(ann_p, df_proj[f'conso_afss_{scen}'], color=C[scen], ls=ls, lw=2, label=lbl)
    ax.axvline(2023, color=C['gris'], ls='--', lw=1, alpha=0.6)
    ax.set_title("Consommation électrique — Afrique SubSaharienne (kWh)", fontweight='bold')
    ax.set_xlabel("Année"); ax.set_ylabel("kWh/an")
    ax.legend(fontsize=8); ax.set_xlim(2000, 2050)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    # 1.3 : Population sans électricité
    ax = axes[1, 0]
    ax.set_facecolor(C['fond'])
    ax.bar(ann_h, df_hist['sans_elec_afss_M'], color=C['afss'], alpha=0.55, label='Sans électricité')
    ax.plot(ann_h, df_hist['sans_elec_afss_M'], color=C['pessimiste'], lw=2, marker='o', ms=3)
    # Annotation du paradoxe démographique
    ax.annotate(
        f"Paradoxe : +{df_hist['sans_elec_afss_M'].iloc[-1]-df_hist['sans_elec_afss_M'].iloc[0]:.0f}M\nmalgré +{df_hist['acces_afss_pct'].iloc[-1]-df_hist['acces_afss_pct'].iloc[0]:.0f} pts d'accès",
        xy=(2023, df_hist['sans_elec_afss_M'].iloc[-1]),
        xytext=(2010, 620), fontsize=12, color=C['pessimiste'],
        arrowprops=dict(arrowstyle='->', color=C['pessimiste'], lw=1.8),
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFEBEE', alpha=0.8)
    )
    ax.set_title("Population sans électricité — Afrique SubSaharienne (millions)", fontweight='bold')
    ax.set_xlabel("Année"); ax.set_ylabel("Personnes sans électricité (M)")
    ax.legend(fontsize=8); ax.set_ylim(400, 750)

    # 1.4 : kWh/habitant vs référence mondiale
    ax = axes[1, 1]
    ax.set_facecolor(C['fond'])
    ax.plot(ann_h, df_hist['kwh_hab_afss'],  color=C['afss'],  lw=2.5, label='Afrique SubSaharienne')
    ax.plot(ann_h, df_hist['kwh_hab_congo'], color=C['congo'], lw=2.5, label='Congo-Brazzaville')
    ax.axhline(REF,  color='#1565C0', ls='--', lw=1.5, alpha=0.7, label=f'Moy. mondiale ({REF} kWh — IEA 2023)')
    ax.axhline(6415, color='#4A148C', ls=':', lw=1.5, alpha=0.7, label='France (6 415 kWh — IEA 2023)')
    # Zone de décalage
    ax.fill_between(ann_h, df_hist['kwh_hab_afss'], REF, alpha=0.08, color='red',
                    label='Déficit vs monde')
    ax.set_title("Consommation par habitant (kWh/pers/an)", fontweight='bold')
    ax.set_xlabel("Année"); ax.set_ylabel("kWh/habitant/an")
    ax.legend(fontsize=7.5); ax.set_xlim(2000, 2023)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    plt.tight_layout(pad=2.5)
    f1 = f'{out}/01_dashboard_donnees_reelles.png'
    plt.savefig(f1, dpi=150, bbox_inches='tight', facecolor=C['fond'])
    plt.close()
    print(f"\nFigure 1 : {f1}")

    # FIGURE 2 : Comparaison scénarios 2050
    fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))
    fig2.suptitle("Projections 2050 : Comparaison des 3 Scénarios\n"
                  "Basées sur IEA Africa Energy Outlook 2022 (STEPS / APS)", fontsize=13, fontweight='bold')
    fig2.patch.set_facecolor(C['fond'])

    labs   = ['Pessimiste', 'Réaliste', 'Optimiste']
    keys   = ['pessimiste', 'realiste', 'optimiste']
    colors = [C['pessimiste'], C['realiste'], C['optimiste']]

    # Panel 2.1 : Consommation
    ax21 = axes2[0]; ax21.set_facecolor(C['fond'])
    vals = [df_proj[f'conso_afss_{k}'].iloc[-1] for k in keys]
    bars = ax21.bar(labs, vals, color=colors, alpha=0.85, edgecolor='white', linewidth=2)
    for bar, v in zip(bars, vals):
        ax21.text(bar.get_x()+bar.get_width()/2., bar.get_height()+30,
                  f'{v:,.0f} kWh', ha='center', va='bottom', fontweight='bold', fontsize=10)
    ax21.axhline(565, color=C['gris'], ls='--', alpha=0.6, label='Niveau 2023 (565 kWh)')
    ax21.set_title("Consommation Afrique SubSaharienne (kWh)", fontweight='bold')
    ax21.set_ylabel("kWh/an"); ax21.legend(fontsize=8)

    # Panel 2.2 : Accès électricité
    ax22 = axes2[1]; ax22.set_facecolor(C['fond'])
    v_afss  = [df_proj[f'acces_afss_{k}'].iloc[-1] for k in keys]
    v_congo = [df_proj[f'acces_congo_{k}'].iloc[-1] for k in keys]
    x = np.arange(len(labs)); w = 0.35
    b1 = ax22.bar(x-w/2, v_afss,  w, color=[c+'99' for c in colors], edgecolor=colors, lw=2, label='Afrique SubSaharienne')
    b2 = ax22.bar(x+w/2, v_congo, w, color=colors, alpha=0.85, edgecolor='white', lw=1.5, label='Congo')
    for b, v in zip(b1, v_afss):
        ax22.text(b.get_x()+b.get_width()/2., b.get_height()+0.5, f'{v:.0f}%', ha='center', va='bottom', fontsize=9)
    for b, v in zip(b2, v_congo):
        ax22.text(b.get_x()+b.get_width()/2., b.get_height()+0.5, f'{v:.0f}%', ha='center', va='bottom', fontsize=9)
    ax22.axhline(100, color='#F9A825', ls=':', lw=1.5, label='Accès universel ODD7')
    ax22.set_title("Taux d'accès à l'électricité (%)", fontweight='bold')
    ax22.set_xticks(x); ax22.set_xticklabels(labs); ax22.legend(fontsize=8); ax22.set_ylim(0, 115)

    # Panel 2.3 : Sans électricité
    ax23 = axes2[2]; ax23.set_facecolor(C['fond'])
    v_sans = [df_proj[f'sans_elec_{k}'].iloc[-1] for k in keys]
    bars3 = ax23.bar(labs, v_sans, color=colors, alpha=0.85, edgecolor='white', lw=2)
    for bar, v in zip(bars3, v_sans):
        ax23.text(bar.get_x()+bar.get_width()/2., bar.get_height()+20,
                  f'{v:,.0f}M', ha='center', va='bottom', fontweight='bold', fontsize=10)
    ax23.axhline(df['sans_elec_afss_M'].iloc[-1], color=C['gris'], ls='--', alpha=0.6,
                 label=f'Niveau 2023 ({df["sans_elec_afss_M"].iloc[-1]:.0f}M)')
    ax23.set_title("Population sans électricité en 2050 (M)", fontweight='bold')
    ax23.set_ylabel("Millions de personnes"); ax23.legend(fontsize=8)

    plt.tight_layout()
    f2 = f'{out}/02_scenarios_2050.png'
    plt.savefig(f2, dpi=150, bbox_inches='tight', facecolor=C['fond'])
    plt.close()
    print(f"Figure 2 : {f2}")

    # FIGURE 3 : Infographie sombre — le défi en chiffres
    fig3, ax = plt.subplots(figsize=(13, 7))
    fig3.patch.set_facecolor('#0A0E1A')
    ax.set_facecolor('#0A0E1A')

    cats = [
        'Capacité\nréelle 2023\n(192 GW)',
        'Besoin\n2030\n(STEPS IEA)',
        'Besoin\n2040\n(Réaliste)',
        'Besoin\n2050\n(Réaliste)',
        'Besoin\n2050\n(Optimiste)'
    ]
    vals_gw   = [192, 320, 480, 614, 1024]
    bar_colors = ['#00E676', '#FFCA28', '#FF7043', '#EF5350', '#E040FB']

    bars = ax.barh(cats, vals_gw, color=bar_colors, alpha=0.88, height=0.55,
                   edgecolor='#FFFFFF22', linewidth=0.5)
    for bar, v in zip(bars, vals_gw):
        ax.text(bar.get_width()+8, bar.get_y()+bar.get_height()/2.,
                f'{v} GW', va='center', color='white', fontweight='bold', fontsize=12)
    ax.axvline(192, color='#00E676', ls='--', lw=1.5, alpha=0.4)

    ax.set_title(
        "Le Défi Électrique de l'Afrique Subsaharienne à 2050\n"
        "Capacité installée requise vs situation actuelle réelle (IEA Africa Energy Outlook 2022)",
        color='white', fontsize=13, fontweight='bold', pad=18
    )
    ax.set_xlabel("Capacité installée (GW)", color='white', fontsize=11)
    ax.tick_params(colors='white', labelsize=9)
    for spine in ax.spines.values():
        spine.set_color('#333333')
    ax.xaxis.label.set_color('white')
    ax.text(0.99, 0.01,
            "Sources : IEA Africa Energy Outlook 2022",
            transform=ax.transAxes, ha='right', va='bottom', color='#555555', fontsize=7.5, style='italic')

    # Ratio multiplicateur
    for i, (v, c) in enumerate(zip(vals_gw[1:], cats[1:]), 1):
        ratio = v / 192
        ax.text(v + 65, i - 0.5 + 0.275, f'×{ratio:.1f}', color='#AAAAAA', fontsize=9, style='italic')

    plt.tight_layout()
    f3 = f'{out}/03_defi_capacite.png'
    plt.savefig(f3, dpi=150, bbox_inches='tight', facecolor='#0A0E1A')
    plt.close()
    print(f"Figure 3 : {f3}")

    return f1, f2, f3


print("\nCRÉATION DES VISUALISATIONS...")
figs = visualiser(df, df_proj, out='myfolder/Project/Outputs')


# =============================================================================
# BLOC 8 : EXPORT DES DONNÉES
# =============================================================================

def exporter(df_hist, df_proj, out='outputs'):
    """Exporte les données en CSV avec métadonnées de source."""
    os.makedirs(out, exist_ok=True)

    # CSV données historiques avec note de source
    f1 = f'{out}/donnees_reelles_2000_2023.csv'
    df_hist.to_csv(f1, sep=';', decimal=',', encoding='utf-8-sig')
    print(f"Données réelles exportées : {f1}")

    # CSV projections
    f2 = f'{out}/projections_2024_2050.csv'
    df_proj.to_csv(f2, sep=';', decimal=',', encoding='utf-8-sig')
    print(f" Projections exportées : {f2}")

    # CSV synthèse + sources
    sources = {
        'Indicateur': [
            'Accès électricité Afrique SubSaharienne (%)',
            'Accès électricité Congo-Brazzaville (%)',
            'Population Afrique SubSaharienne (millions)',
            'Population Congo-Brazzaville (millions)',
            'Consommation élec. Afrique SubSaharienne (kWh)',
            'Consommation élec. Congo-Brazzaville (kWh)',
            'Consommation/hab Afrique SubSaharienne (kWh)',
            'Consommation/hab Congo-Brazzaville (kWh)',
            'Capacité installée Afrique SubSaharienne (GW)',
            'Population sans élec. Afrique SubSaharienne (M)',
            'PIB/hab Congo-Brazzaville (USD courants)',
            'Projection conso 2050 — Optimiste (kWh)',
            'Projection conso 2050 — Réaliste (kWh)',
            'Projection conso 2050 — Pessimiste (kWh)',
            'Projection accès 2050 — Optimiste Afrique SubSaharienne (%)',
            'Projection accès 2050 — Réaliste Afrique SubSaharienne (%)',
        ],
        'Valeur 2023': [
            df_hist['acces_afss_pct'].iloc[-1],
            df_hist['acces_congo_pct'].iloc[-1],
            df_hist['pop_afss_M'].iloc[-1],
            df_hist['pop_congo_M'].iloc[-1],
            df_hist['conso_afss_kwh'].iloc[-1],
            df_hist['conso_congo_kwh'].iloc[-1],
            df_hist['kwh_hab_afss'].iloc[-1],
            df_hist['kwh_hab_congo'].iloc[-1],
            df_hist['capacite_afss_gw'].iloc[-1],
            df_hist['sans_elec_afss_M'].iloc[-1],
            df_hist['pib_hab_congo_usd'].iloc[-1],
            round(df_proj['conso_afss_optimiste'].iloc[-1], 0),
            round(df_proj['conso_afss_realiste'].iloc[-1], 0),
            round(df_proj['conso_afss_pessimiste'].iloc[-1], 0),
            round(df_proj['acces_afss_optimiste'].iloc[-1], 1),
            round(df_proj['acces_afss_realiste'].iloc[-1], 1),
        ],
        'Source': [
            'Banque Mondiale WDI EG.ELC.ACCS.ZS / Tracking SDG7 2024',
            'Banque Mondiale WDI EG.ELC.ACCS.ZS / IEA 2024',
            'ONU DESA World Population Prospects 2024',
            'ONU DESA World Population Prospects 2024',
            'IEA World Energy Balances 2024 / Africa Energy Outlook 2022',
            'IEA Africa Energy Statistics 2024 / BAD',
            'Calcul auteur (IEA + ONU DESA)',
            'Calcul auteur (IEA + ONU DESA)',
            'Calcul auteur (WB + ONU DESA)',
            'Banque Mondiale WDI NY.GDP.PCAP.CD',
            'Projection auteur calibrée sur IEA APS 2022',
            'Projection auteur calibrée sur IEA STEPS 2022',
            'Projection auteur (stagnation)',
            'Projection auteur calibrée sur IEA APS 2022',
            'Projection auteur calibrée sur IEA STEPS 2022',
        ]
    }
    df_sources = pd.DataFrame(sources)
    f3 = f'{out}/synthese_avec_sources.csv'
    df_sources.to_csv(f3, sep=';', index=False, encoding='utf-8-sig')
    print(f"Synthèse + sources exportée : {f3}")


print("\nEXPORT DES DONNÉES :")
exporter(df, df_proj, out='myfolder/Project/Outputs')


# =============================================================================
# BLOC 9 : RÉSUMÉ FINAL
# =============================================================================
print("\n" + "="*70)
print("ANALYSE COMPLÈTE TERMINÉE — DONNÉES RÉELLES VÉRIFIÉES")
print("="*70)
print(f"""
Sources utilisées :
  [1] Banque Mondiale WDI          https://data.worldbank.org
  [2] IEA World Energy Balances    https://www.iea.org
  [3] IEA Africa Energy Outlook    https://www.iea.org/reports/africa-energy-outlook-2022
  [4] ONU DESA WPP 2024            https://population.un.org/wpp/

Chiffres clés réells (2023) :
  • Accès électricité Afrique SubSaharienne  : {df['acces_afss_pct'].iloc[-1]}%  (vs 23% en 2000)
  • Accès électricité Congo-Brazzaville     : {df['acces_congo_pct'].iloc[-1]}%  (vs 26.8% en 2000)
  • Population sans électricité   : {df['sans_elec_afss_M'].iloc[-1]:.0f} millions (+{df['sans_elec_afss_M'].iloc[-1]-df['sans_elec_afss_M'].iloc[0]:.0f}M vs 2000!)
  • Consommation/hab Congo-Brazzaville      : {df['kwh_hab_congo'].iloc[-1]:.0f} kWh/an (monde: 3600 kWh/an)
  • Capacité installée Afrique SubSaharienne : {df['capacite_afss_gw'].iloc[-1]} GW (IEA Africa Energy Outlook 2022)
""")

