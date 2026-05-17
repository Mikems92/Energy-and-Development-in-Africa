# Énergie Électrique en Afrique Subsaharienne \& Congo-Brazzaville

## Analyse des données réelles 2000–2023 | Projections 2050

### *Données : Banque Mondiale · IEA · ONU*



## 🔴 Le chiffre qui devrait vous révolter

**589 millions d’habitants vivaient en Afrique subsaharienne sans accès à l’électricité en 2023.**

Et voici le paradoxe qui rend ce chiffre encore plus douloureux :

L’accès à l’électricité est passé de 5.7% à 53.3% (soit +27.6 pts) en Afrique subsaharienne et de 29.4% à 51.3% (soit +21.9 pts) au Congo-Brazzaville. Et pourtant, en 2000, il y avait 506 millions de personnes sans électricité contre 589 millions en Afrique subsaharienne.

La démographie a effacé 23 ans de progrès. En termes absolus, l'Afrique subsaharienne recule.



\---

## Le cas Congo-Brazzaville : l'injustice en données

|Indicateur|Congo-B 2023|Monde 2023|Ratio|
|-|-|-|-|
|Consommation/habitant|**338 kWh/an**|3 600 kWh/an|**9,4% du monde**|
|Taux d'accès à l'électricité|**51,3%**|92%|—|
|Capacité hydraulique potentielle|**≥ 44 000 MW** (Grand Inga)|—|Inexploitée|
|PIB/habitant|2 482 USD|13 631 USD|18%|



Le fleuve Congo est le **2ᵉ fleuve du monde en débit**. Son potentiel hydroélectrique représente **6% du potentiel mondial**. Le projet Grand Inga, s'il était réalisé, pourrait alimenter un tiers de toute l'Afrique.

**En 2023, un Congolais consomme 338 kWh d'électricité par an. Un Français en consomme 6 415.**

Ce n'est pas un problème de ressources. C'est un problème de gouvernance, de financement et de priorités.



\---

## Ce que les données réelles révèlent

```
DONNÉES RÉELLES VÉRIFIÉES — SOURCES OFFICIELLES
─────────────────────────────────────────────────────────────────────
Indicateur                          2000        2023      Variation
─────────────────────────────────────────────────────────────────────
Accès électricité Afrique SS (%)    25,7%       53,3%     +27,6 pts
Accès électricité Congo-B (%)       29,4%       51,3%     +21,9 pts
Population Afrique SS (millions)     681,125     1 260,0     +85%
Sans électricité Afrique SS (M)      506         589       +83M
Consommation/hab Afrique SS (kWh)    454         376       -17%
Consommation/hab Congo-B (kWh)        96         338       +252%
Capacité installée Afrique SS (GW)    68         192       +182%
─────────────────────────────────────────────────────────────────────
Sources : Banque Mondiale WDI · IEA World Energy Balances 2024
          IRENA Statistics 2024 · ONU 


```

### Projections 2050 (3 scénarios calibrés IEA)

```
─────────────────────────────────────────────────────────────────
                              Pessimiste   Réaliste   Optimiste
─────────────────────────────────────────────────────────────────
Consommation Afrique SS (TWh)      953       1 235       2 339
Accès électricité Afr. SS (%)      55%         70%         100%
Accès électricité Congo (%)        58%         70%         100%
Capacité installée (GW)            272         353         668
Sans électricité (millions)      1 104         736         0
─────────────────────────────────────────────────────────────────
Scénarios alignés sur : IEA STEPS (réaliste) / IEA APS (optimiste)
IEA Africa Energy Outlook 2022
```



\---

## Contenu du projet

```
energie\\\\\\\_afrique\\\\\\\_2050/
│
├── analyse\\\\\\\_energie\\\\\\\_part\\\\\\\_1.py   ← Script principal (400+ lignes commentées)
│
├──├── 01\\\\\\\_dashboard\\\\\\\_donnees\\\\\\\_reelles.png  ← Dashboard 4 panneaux
│   ├── 02\\\\\\\_scenarios\\\\\\\_2050.png             ← Comparaison 3 scénarios
│   ├── 03\\\\\\\_defi\\\\\\\_capacite.png              ← Infographie dark mode
│   ├── donnees\\\\\\\_reelles\\\\\\\_2000\\\\\\\_2023.csv     ← Données réelles vérifiées
│   ├── projections\\\\\\\_2024\\\\\\\_2050.csv         ← Projections 2024–2050
│   └── synthese\\\\\\\_avec\\\\\\\_sources.csv         ← Tableau de bord + sources
│
├── README.md

```

\---

## Stack technique

```python
Python 3.11+ | Pandas 3.0+ | NumPy 2.4+ | Matplotlib 3.10+ | Seaborn 0.13+
```

```bash
pip install pandas numpy matplotlib seaborn
python analyse\\\\\\\_energie\\\\\\\_part\\\\\\\_1.py
```



\---

## Ce projet couvre

**Python fondamentaux** — fonctions, dictionnaires, boucles, conditions, f-strings
**Pandas** — DataFrame, `set\\\\\\\_index`, `isnull`, `describe`, `iloc`, `pct\\\\\\\_change`, `clip`, `to\\\\\\\_csv`
**NumPy** — arrays, opérations vectorisées
**Matplotlib/Seaborn** — `subplots`, `plot`, `bar`, `fill\\\\\\\_between`, `annotate`, `savefig`
**Mathématiques** — TCAC, croissance exponentielle, facteur de charge, interpolation
**Méthode Data Science** — Collecte → Nettoyage → EDA → Modélisation → Visualisation → Communication



\---

## Sources officielles

|#|Source|Indicateurs|URL|
|-|-|-|-|
|1|**Banque Mondiale WDI**|Accès électricité, PIB/hab|[data.worldbank.org](https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS)|
|2|**IEA World Energy Balances 2024**|Consommation, production|[iea.org](https://www.iea.org/data-and-statistics/data-product/world-energy-balances)|
|3|**IEA Africa Energy Outlook 2022**|Scénarios, projections|[iea.org/reports](https://www.iea.org/reports/africa-energy-outlook-2022)|
|4|**ONU DESA WPP 2024**|Population, démographie|[population.un.org](https://population.un.org/wpp/)|



\---

## Questions ouvertes (réagissez et commentez)

**🔴 Le projet Grand Inga est-il encore réaliste en 2026 ?** Capacité potentielle : 44 000 MW. Montant estimé : 80 milliards USD. Aucune date de livraison confirmée. Qu'est-ce qui bloque vraiment ?

**🟡 Solaire décentralisé vs grand réseau centralisé** — quelle est la meilleure stratégie pour électrifier les 589 millions ? le off-grid solaire est-elle la solution ? Votre avis ?

**🟢 Le paradoxe congolais** — un pays qui exporte du pétrole et du gaz mais qui consomme 338 kWh/hab/an. Comment sortir de cette trappe à ressources ?

\---



**Donnez une étoile si ce projet vous a été utile.**

