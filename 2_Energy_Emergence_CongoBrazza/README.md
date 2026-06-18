# Émergence Énergétique : Quels critères ? Où en est le Congo ? 
## Analyse comparative · 16 pays · Scoring · PCA · Clustering · Forecast 
--- 
## La question centrale 
Quels sont les critères qui font qu'un pays est « émergent énergétique » ? 
Le Congo-Brazzaville les remplit-il — et si non, quand peut-il y arriver ? 
Ce projet répond avec des **données réelles**, récupérées automatiquement depuis l'API officielle de la Banque Mondiale, pour 15 pays de référence et le Congo-Brazzaville. 
--- ## Ce que fait le code — étape par étape 

### 1. Récupération automatique des données (API Banque Mondiale) 
Le script appelle **directement** l'API ouverte de la Banque Mondiale pour 16 pays : 
``` https://api.worldbank.org/v2/country/{code}/indicator/{indicateur}?format=json ``` 
| Indicateur WDI | Variable | Année | 
|---|---|---| 
| `EG.ELC.ACCS.ZS` | Accès à l'électricité (%) | 2023 | 
| `EG.USE.ELEC.KH.PC` | Consommation électrique par habitant (kWh) | 2023 | 
| `EG.ELC.RNEW.ZS` | Part des énergies renouvelables (%) | 2021 | 
| `EG.ELC.LOSS.ZS` | Pertes réseau (%) | 2023 | 
| `NY.GDP.PCAP.CD` | PIB par habitant (USD courants) | 2023 | 
| `SP.POP.TOTL` | Population totale | 2023 | 
Pour le forecast Congo, les mêmes indicateurs sont récupérés sur **2009–2023**. 

### 2. Les 16 pays analysés 
**15 pays de référence** sélectionnés pour leurs progrès énergétiques mesurables : 
| Région | Pays | 
|---|---| 
| Afrique | Égypte · Éthiopie · Ghana · Kenya · Maroc · Rwanda · Afrique du Sud 
| 
| Moyen-Orient | Émirats Arabes Unis | 
| Amérique | Chili · Brésil | 
| Asie | Bangladesh · Inde · Kazakhstan · Turquie · Vietnam | 
**+ Congo-Brazzaville** — pays analysé. 

### 3. Scoring multicritères (5 critères pondérés) 
| Critère | Seuil d'émergence | Poids | Source | 
|---|---|---|---| 
| Accès électricité | ≥ 90 % | 30 % | IEA SDG7 2024 | 
| Consommation/hab | ≥ 1 000 kWh/an | 25 % | Energy for Growth Hub | 
| Part renouvelables | ≥ 60 % | 20 % | IEA Africa Outlook 2022 | 
| Pertes réseau | ≤ 15 % | 15 % | Banque Mondiale | 
| PIB/habitant | ≥ 2 500 USD | 10 % | Energy for Growth Hub | 
**Seuils de statut :** 
- Score ≥ 0.50 → **Émergent** 
- Score ≥ 0.25 → **En transition** 
- Score < 0.25 → **Pré-émergent** 
Méthode : normalisation **Min-Max** sur chaque indicateur, puis moyenne pondérée. Les pertes réseau sont **inversées** (moins de pertes = meilleur score). 

### 4. Analyse en Composantes Principales (PCA) + Clustering K-Means 
- **PCA** : réduction des 5 dimensions → 2 axes visuels 
- **K-Means** (3 clusters) : groupement automatique des pays par profil similaire 

### 5. Forecast par régression linéaire 
Régression linéaire sur l'historique Congo 2009–2023 pour estimer l'année d'atteinte de chaque seuil selon la **tendance actuelle** (sans réforme additionnelle). 
--- 
## Les 5 visualisations produites 
| Fichier | Contenu | 
|---|---| 
| `01_classement_radar.png` | Classement des 16 pays par score + Radar chart Congo vs médiane émergents | 
| `02_heatmap_criteres.png` | Matrice 16 pays × 5 critères — scores normalisés colorés | 
| `03_pca_clusters.png` | Cartographie PCA — 3 groupes de pays avec annotations | 
| `04_forecast_trajectoires.png` | Trajectoires forecast Congo (dark mode) — 3 indicateurs | 
| `05_gap_feuille_de_route.png` | Gap analysis Congo vs seuils + feuille de route |
 --- 
## Structure du projet 
``` 
PROJECT/01.Energy/Sem_02/ 
│ 
├── 📄 analyse_emergence_energetique.py ← Script principal (1 020 lignes) 
│ 
├── 📊 01_classement_radar.png 
├── 📊 02_heatmap_criteres.png 
├── 📊 03_pca_clusters.png 
├── 📊 04_forecast_trajectoires.png 
├── 📊 05_gap_feuille_de_route.png 
│
 ├── 📄 scores_emergence_energetique.csv ← Classement + scores 16 pays 
├── 📄 forecast_congo_emergence.csv ← Années d'atteinte par seuil 
└── 📄 gap_analyse_congo.csv ← Gap Congo vs chaque critère 
``` 
--- 
## Notions couvertes 
| Notion | Bibliothèque | Application dans ce projet | 
|---|---|---| 
| **Appel API REST** | `requests` | Récupération automatique WB pour 16 pays | 
| **Normalisation Min-Max** | `sklearn.preprocessing` | Rendre 5 indicateurs comparables | 
| **Scoring pondéré** | `pandas` / `numpy` | Score composite d'émergence | 
| **PCA** | `sklearn.decomposition` | Visualiser 5 dimensions en 2D | 
| **K-Means clustering** | `sklearn.cluster` | Grouper les pays par profil similaire | 
| **Régression linéaire** | `sklearn.linear_model` | Forecast tendance Congo | 
| **Radar chart** | `matplotlib` (polar) | Comparaison multidimensionnelle | 
| **Heatmap annotée** | `seaborn` | Matrice de scores colorée | 
| **GridSpec** | `matplotlib.gridspec` | Mise en page multi-panneaux complexe | 
| **FancyBboxPatch** | `matplotlib.patches` | Boîtes arrondies dans les figures | 

--- 
## Sources officielles 
| # | Source | URL | 
|---|---|---| 
| 1 | **Banque Mondiale WDI** | [data.worldbank.org/indicator](https://data.worldbank.org/indicator) | 
| 2 | **IEA Africa Energy Outlook 2022** | [iea.org/reports/africa-energy-outlook-2022](https://www.iea.org/reports/africa-energy-outlook-2022) | 
| 3 | **IEA SDG7 Data & Projections 2024** | [iea.org/reports/sdg7-data-and-projections](https://www.iea.org/reports/sdg7-data-and-projections) | 
| 4 | **IRENA Statistics 2024** | [irena.org/Data/Downloads/IRENASTAT](https://www.irena.org/Data/Downloads/IRENASTAT) | 
| 5 | **Energy for Growth Hub** | [energyforgrowth.org](https://energyforgrowth.org) | 
| 6 | **ONU DESA WPP 2024** | [population.un.org/wpp](https://population.un.org/wpp/) | 
| 7 | **Ember Climate 2024** | [ember-climate.org/data](https://ember-climate.org/data/) | 
--- 
## Questions ouvertes — Issues GitHub
Q1 — Le score Congo-Brazzaville est calculé à partir de 5 critères pondérés. Si vous changiez les poids — par exemple en donnant plus d'importance aux ENR (35%) et moins au PIB (5%) — le classement changerait-il significativement ? Pourquoi ou pourquoi pas ? 
Q2 — Le forecast utilise une régression linéaire (tendance actuelle). Quels événements extérieurs (financement BAD, mise en service Grand Inga, réforme E2C) pourraient "casser" cette droite à la hausse ? 
Q3 — Parmi les 15 pays de référence, lequel, selon vous, représente le modèle le plus réaliste à suivre pour le Congo, compte tenu de ses spécificités géographiques, institutionnelles et économiques ? 
--- 
** Donnez une étoile si ce projet vous a été utile** 
