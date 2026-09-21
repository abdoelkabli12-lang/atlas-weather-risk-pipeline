# Atlas Weather Risk Pipeline

> Pipeline de données météorologiques pour le Royaume du Maroc — extraction, transformation, chargement et visualisation des prévisions météo avec évaluation des risques.

---

## 📌 Vue d'ensemble

Ce projet implémente un pipeline de données complet pour collecter, nettoyer, enrichir et visualiser les prévisions météorologiques sur 7 jours pour toutes les villes du Maroc. Il est construit autour de 3 couches de données (bronze → silver → gold), orchestré par Airflow, stocké dans PostgreSQL et visualisé via un dashboard Streamlit.

**Variables météo extraites (Open-Meteo) :**
- `temp_max` / `temp_min` — températures maximales et minimales (°C)
- `precipitation` — précipitations totales (mm)
- `precip_probability` — probabilité de précipitation (%)
- `wind_max` — vent max (km/h)
- `wind_gusts` — rafales (km/h)
- `weather_code` — code météo WMO

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   EXTRACTION    │────▶│  TRANSFORMATION  │────▶│    LOAD + DB    │
│  (bronze layer) │     │  (silver/gold)   │     │  (PostgreSQL)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                       │                        │
        ▼                       ▼                        ▼
  cities.csv +           weather_clean.csv        ┌─────────────────┐
  weather.json           weather_categories.csv   │  DASHBOARD      │
                                            weather_risk.csv  │  Streamlit      │
                                                           └─────────────────┘
```

Chaque couche a un rôle précis :
- **Bronze** : données brutes, telles qu'extraits (JSON API, CSV téléchargé)
- **Silver** : données nettoyées, structurées, prêtes à l'analyse
- **Gold** : données enrichies avec catégories et scores de risque

---

## 📂 Structure du projet

```
atlas-weather-risk-pipeline/
├── extraction/
│   ├── __init__.py
│   ├── cities.py          # Téléchargement villes Maroc
│   ├── weather.py         # API Open-Meteo
│   └── weather_mock.py    # Données fictives pour tests
│
├── transformation/
│   ├── __init__.py
│   ├── cleaning.py        # CleanData — aplanhissement JSON
│   ├── features.py        # Category + Risk — catégorisation & scoring
│   └── quality.py         # (réservé pour contrôle qualité)
│
├── load/
│   ├── __init__.py
│   ├── postgres.py        # Connexion DB PostgreSQL
│   └── load_weather.py    # Chargement des 3 tables
│
├── dashboard/
│   ├── streamlit_app.py   # Dashboard Streamlit
│   └── components/
│       └── __init__.py
│
├── airflow/
│   └── dags/
│       └── atlas_weather_pipeline.py   # DAG Airflow
│
├── config/
│   └── config.py          # Configuration (réservé)
│
├── inspect_db.py          # Outil d'inspection DB
└── README.md
```

---

## 🔧 Extraction — Couche Bronze

### 1. `extraction/cities.py` — `class Cities`

**Fonction :** `get_cities()`

Télécharge la liste des villes du Maroc depuis SimpleMaps et la sauvegarde en CSV.

**Source :** `https://simplemaps.com/static/data/country-cities/ma/ma.csv`

**Sortie :** `data/bronze/cities/morocco_cities.csv`

**Gestion d'erreurs :**
- `Timeout` → "The data took too long to load"
- `RequestException` → "the request didn't go through"

---

### 2. `extraction/weather.py` — `def get_weather()`

Récupère les prévisions météo sur 7 jours pour toutes les villes du Maroc depuis l'API Open-Meteo.

**API :** `https://api.open-meteo.com/v1/forecast`

**Paramètres :**
| Paramètre | Valeur |
|---|---|
| `latitude` | Toutes les latitudes des villes marocaines (comma-separated) |
| `longitude` | Toutes les longitudes (comma-separated) |
| `daily` | `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `precipitation_probability_max`, `wind_speed_10m_max`, `wind_gusts_10m_max`, `weather_code` |
| `timezone` | `Africa/Casablanca` |

**Sortie :** `data/bronze/weather/weather.json`

Chaque entrée du JSON contient : `city`, `latitude`, `longitude`, `timezone`, et `daily` (avec 7 jours de données pour les 7 variables).

**Gestion d'erreurs :**
- `Timeout` → "The data took too long to load"
- `RequestException` → "Request failed: {e}"

---

### 3. `extraction/weather_mock.py` — Données de test

Génère des données météo synthétiques pour les tests, sans appel API.

**Ce qu'il fait :**
- Lit `data/bronze/cities/morocco_cities.csv`
- Pour chaque ville, génère 7 jours de données aléatoires
- Température de base aléatoire entre 24°C et 36°C
- Variabilité réaliste : temp_max ±4°C, temp_min = temp_max − 7 à 15°C
- Précipitations : 0–20 mm, probabilité : 0–100%
- Vent : 10–40 km/h, rafales : vent × 1.3–1.8
- weather_code généré selon la probabilité de précipitation (codes clairs <20%, modérés 20–60%, pluvieux >60%)

**Sortie :** `data/bronze/weather/weather_mock.json`

**Usage :** Remplacer `weather.json` par `weather_mock.json` pour tester le pipeline sans dépendre de l'API.

---

## 🔄 Transformation — Couches Silver et Gold

### 4. `transformation/cleaning.py` — `class CleanData`

#### `__init__()`
Charge le JSON bronze (`data/bronze/weather/weather.json`) et le transforme en DataFrame.

#### `cleaning_data()`
Aplanit la structure imbriquée du JSON Open-Meteo en un DataFrame plat.

**Processus :**
1. Pour chaque ligne du DataFrame (une ville), extrait la partie `daily`
2. Ajoute `city`, `latitude`, `longitude` à chaque ligne daily
3. Concatène toutes les lignes daily en un seul DataFrame
4. Sélectionne et réordonne les colonnes
5. Rename les colonnes :
   - `time` → `date`
   - `temperature_2m_max` → `temp_max`
   - `temperature_2m_min` → `temp_min`
   - `precipitation_sum` → `precipitation`
   - `precipitation_probability_max` → `precip_probability`
   - `wind_speed_10m_max` → `wind_max`
   - `wind_gusts_10m_max` → `wind_gusts`
6. Convertit `date` en datetime
7. Sauvegarde en CSV : `data/silver/weather_clean.csv`

**Sortie (silver) :** `data/silver/weather_clean.csv`

| Colonne | Type | Description |
|---|---|---|
| city | str | Nom de la ville |
| latitude | float | Latitude |
| longitude | float | Longitude |
| date | datetime | Date de la prévision |
| temp_max | float | Temp max °C |
| temp_min | float | Temp min °C |
| precipitation | float | Précipitations mm |
| precip_probability | float | Probabilité précip % |
| wind_max | float | Vent max km/h |
| wind_gusts | float | Rafales km/h |
| weather_code | int | Code WMO |

---

### 5. `transformation/features.py` — `class Category` et `class Risk`

#### Classe `Category` — Catégorisation des variables

Transforme les valeurs numériques en catégories textuelles.

##### `temp_category()`
Catégorise `temp_max` en 5 niveaux :

| Temp max (°C) | Catégorie |
|---|---|
| < 20 | cold |
| 20-30 | Mild |
| 30-40 | Normal |
| 40-50 | Hot |
| ≥ 50 | Extreme |

Bins : `[10, 20, 30, 40, 50, 55]` | Labels : `["cold", "Mild", "Normal", "Hot", "Extreme"]`

##### `prec_category()`
Catégorise `precipitation` :

| Précip (mm) | Catégorie |
|---|---|
| 0 | zero |
| 0-0.1 | Low |
| 0.1-0.5 | Moderate |
| 0.5-1 | Heavy |
| >1 | Very Heavy |

Bins : `[-∞, 0, 0.1, 0.5, 1, ∞]` | Labels : `["zero", "Low", "Moderate", "Heavy", "Very Heavy"]`

##### `prec_probability_category()`
Catégorise `precip_probability` :

| Probabilité (%) | Catégorie |
|---|---|
| 0-20 | Very Low |
| 20-40 | Low |
| 40-60 | Moderate |
| 60-80 | High |
| 80-100 | Very High |

Bins : `[0, 20, 40, 60, 80, 100]` | Labels : `["Very Low", "Low", "Moderate", "High", "Very High"]`

##### `wind_category()`
Catégorise `wind_max` :

| Vent max (km/h) | Catégorie |
|---|---|
| < 5 | weak |
| 5-10 | normal |
| 10-20 | stong |
| 20-30 | very strong |
| >30 | extreme |

Bins : `[5, 10, 20, 30, 40, ∞]` | Labels : `["weak", "normal", "stong", "very strong", "extreme"]`

##### `gust_category()`
Catégorise `wind_gusts` :

| Rafales (km/h) | Catégorie |
|---|---|
| < 30 | weak |
| 30-50 | normal |
| 50-70 | strong |
| 70-90 | very strong |
| >90 | extreme |

Bins : `[0, 30, 50, 70, 90, ∞]` | Labels : `["weak", "normal", "strong", "very strong", "extreme"]`

##### `weather_code_category()`
Mapping des codes WMO vers des catégories de risque :

| Code(s) WMO | Catégorie |
|---|---|
| 0 | Clear |
| 1, 2 | Low |
| 3, 45, 48, 51, 53 | Moderate |
| 55, 56, 57, 61, 63, 71, 73, 80, 81 | High |
| 65, 66, 67, 75, 77, 82, 85, 86 | Very High |
| 95, 96, 99 | Extreme |

Utilise un dictionnaire de mapping direct via `df["weather_code"].map(risk_values)`.

##### `save_category()`
Orchestre toutes les catégorisations et sauvegarde en : `data/gold/weather_categories.csv`

Contient toutes les colonnes silver + les 6 colonnes de catégorie :
`temp_category`, `prec_category`, `prec_probability_category`, `wind_category`, `gust_category`, `weather_category`

---

#### Classe `Risk` — Calcul des scores de risque

##### `temp_risk()`
| Catégorie | Score |
|---|---|
| cold | 20 |
| Mild | 0 |
| Normal | 0 |
| Hot | 50 |
| Extreme | 100 |

##### `prec_risk()`
| Catégorie | Score |
|---|---|
| zero | 0 |
| Low | 25 |
| Moderate | 60 |
| Heavy | 80 |
| Very Heavy | 100 |

##### `prec_probability_risk()`
| Catégorie | Score |
|---|---|
| Very Low | 0 |
| Low | 25 |
| Moderate | 50 |
| High | 75 |
| Very High | 100 |

##### `wind_risk()`
| Catégorie | Score |
|---|---|
| weak | 0 |
| normal | 25 |
| stong | 50 |
| very strong | 75 |
| extreme | 100 |

##### `gust_risk()`
| Catégorie | Score |
|---|---|
| weak | 0 |
| normal | 25 |
| strong | 50 |
| very strong | 75 |
| extreme | 100 |

##### `weather_code_risk()`
| Catégorie | Score |
|---|---|
| Clear | 0 |
| Low | 25 |
| Moderate | 40 |
| High | 75 |
| Very High | 90 |
| Extreme | 100 |

##### `risk_score()`
Calcule le score de risque global comme combinaison pondérée :

```
risk_score = (
    temp_risk           * 0.20 +
    prec_risk           * 0.15 +
    prec_probability_risk * 0.15 +
    wind_risk           * 0.20 +
    gust_risk           * 0.20 +
    weather_code_risk   * 0.10
)
```

**Pondérations :**
| Variable | Poids | Justification |
|---|---|---|
| temp_risk | 20% | Impact modéré sur les activités |
| prec_risk | 15% | Impact sur les transports |
| prec_probability_risk | 15% | Incertitude météo |
| wind_risk | 20% | Impact sur constructions/agriculture |
| gust_risk | 20% | Rafales dangereuses |
| weather_code_risk | 10% | Indicateur global complémentaire |

Le score varie de 0 (pas de risque) à 100 (risque maximal).

##### `risk_level()`
Catégorise le score global en 4 niveaux :

| Score | Niveau |
|---|---|
| 0-24 | Low |
| 25-49 | Moderate |
| 50-74 | High |
| 75-100 | Extreme |

Bins : `[-1, 24, 49, 74, 100]` | Labels : `["Low", "Moderate", "High", "Extreme"]`

##### `save_risk()`
Orchestre tous les calculs et sauvegarde en : `data/gold/weather_risk.csv`

Ajoute une colonne `weather_id` (index séquentiel 1, 2, 3...) comme clé primaire.

---

## 🗄️ Chargement — PostgreSQL

### 6. `load/postgres.py` — Connexion DB

Crée le moteur SQLAlchemy pour PostgreSQL en lisant les credentials depuis les variables d'environnement (`.env`).

**Variables d'environnement :**
| Variable | Default | Description |
|---|---|---|
| `DB_USER` | `atlas_weather` | Nom d'utilisateur |
| `DB_PASSWORD` | (vide) | Mot de passe |
| `DB_HOST` | `localhost` | Hôte |
| `DB_PORT` | `5433` | Port |
| `DB_NAME` | `weather_db` | Nom de la base |

URL de connexion : `postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}`

---

### 7. `load/load_weather.py` — `def load_to_postgres()`

Charge les 3 jeux de données dans PostgreSQL :

#### Étape 1 — Nettoyage
```sql
TRUNCATE weather_forecasts, cities RESTART IDENTITY CASCADE;
DROP TABLE IF EXISTS weather_risk CASCADE;
```

#### Étape 2 — Villes
Charge `data/bronze/cities/morocco_cities.csv` dans la table `cities` via `to_sql(if_exists='append')`.

#### Étape 3 — Prévisions météo
1. Récupère `city_id` et `city` depuis la table `cities`
2. Crée un DataFrame avec `city_id` + `city`
3. Merge avec `data/silver/weather_clean.csv` sur `city`
4. Drop `city`, `latitude`, `longitude` (redondantes avec la FK)
5. Renomme `date` → `forecast_date`
6. Charge dans `weather_forecasts`

**Schéma `weather_forecasts` :**
| Colonne | Type |
|---|---|
| `weather_id` | SERIAL PRIMARY KEY |
| `city_id` | INTEGER REFERENCES cities(city_id) |
| `forecast_date` | DATE |
| `temp_max` | FLOAT |
| `temp_min` | FLOAT |
| `precipitation` | FLOAT |
| `precip_probability` | FLOAT |
| `wind_max` | FLOAT |
| `wind_gusts` | FLOAT |
| `weather_code` | INTEGER |

#### Étape 4 — Risques
1. Récupère `weather_id` depuis `weather_forecasts`
2. Merge avec `data/gold/weather_risk.csv` sur `weather_id`
3. Renomme : `temp_category` → `temperature_category`, `prec_category` → `precipitation_category`
4. Charge dans `weather_risk`

**Schéma `weather_risk` :**
| Colonne | Type |
|---|---|
| `weather_id` | INTEGER PRIMARY KEY REFERENCES weather_forecasts(weather_id) |
| `temperature_category` | VARCHAR |
| `precipitation_category` | VARCHAR |
| `wind_category` | VARCHAR |
| `risk_score` | FLOAT |
| `risk_level` | VARCHAR |

---

## 🔄 Orchestration — Airflow DAG

### `airflow/dags/atlas_weather_pipeline.py`

**DAG :** `atlas_weather_pipeline`

| Paramètre | Valeur |
|---|---|
| Schedule | `@daily` |
| Start date | 2026-09-20 |
| Catchup | False |
| Retries | 2 |
| Retry delay | 2 minutes |

**6 tâches en chaîne séquentielle :**

```
extract_cities → extract_weather → clean → categorize → calculate_risk → load_postgres
```

| # | Task ID | PythonCallable | Rôle |
|---|---|---|---|
| 1 | `extract_cities` | `Cities().get_cities` | Télécharge les villes du Maroc |
| 2 | `extract_weather` | `get_weather` | Récupère les données météo Open-Meteo |
| 3 | `clean` | `CleanData().cleaning_data` | Aplanit le JSON → CSV silver |
| 4 | `categorize` | `Category().save_category` | Catégorise toutes les variables (silver → gold) |
| 5 | `calculate_risk` | `Risk().save_risk` | Calcule les scores de risque (gold) |
| 6 | `load_postgres` | `load_to_postgres` | Charge les 3 tables en PostgreSQL |

Chaque tâche est un `PythonOperator`. Les dépendances garantissent que chaque étape consomme la sortie de la précédente.

---

## 📊 Dashboard Streamlit

### `dashboard/streamlit_app.py`

Dashboard interactif pour explorer les données météo et les risques.

**Configuration :**
- Page title : "Atlas Weather Risk"
- Icône : 🌦️
- Layout : wide, sidebar expansée
- Thème sombre : fond `#050810`, texte `#f8fafc`

**Filtres sidebar :**
1. **Cities** — multiselect de toutes les villes
2. **Forecast period** — date range picker
3. **Risk level** — multiselect `[Low, Moderate, High, Extreme]`

**Métriques (5 colonnes) :**

| Métrique | Description |
|---|---|
| Cities | Nombre de villes dans les filtres |
| Max temp | Température maximale (°C) |
| Max precip | Précipitations maximales (mm) |
| High-risk periods | Nombre de périodes High/Extreme |
| Peak risk | Score max + ville + date |

**Visualisations :**

1. **Risk by city** — Bar chart : risque moyen par ville (tri croissant)
2. **Risk distribution** — Bar chart : nombre de prévisions par niveau de risque
3. **Risk timeline** — Line chart : risque moyen et max par date

**Tableaux :**

1. **Critical forecast windows** — Top 10 des périodes les plus risquées
2. **City summary** — Résumé par ville (avg_risk, peak_risk, avg_temp, total_precip, max_wind)
3. **Forecast explorer** — Exploration complète de toutes les colonnes catégorisées + risque

**Carte géographique :**
- `st.map()` avec les villes colorées par risque moyen
- Couleurs : vert (<25) → turquoise (<50) → jaune (<75) → rouge clair (<90) → rouge (≥90)

---

## 📦 Données — Structure des répertoires

```
data/
├── bronze/
│   ├── cities/
│   │   └── morocco_cities.csv       # Villes du Maroc (simplemaps)
│   └── weather/
│       ├── weather.json             # Données réelles Open-Meteo
│       └── weather_mock.json        # Données de test
│
├── silver/
│   └── weather_clean.csv            # Données nettoyées et aplanries
│
└── gold/
    ├── weather_categories.csv       # Données catégorisées
    └── weather_risk.csv             # Données avec scores de risque
```

---

## 🚀 Comment lancer le projet

### Prérequis
- Python 3.9+
- Airflow (pour l'orchestration)
- PostgreSQL (pour le stockage)
- Dépendances : `pandas`, `numpy`, `requests`, `sqlalchemy`, `psycopg2`, `python-dotenv`, `streamlit`

### 1. Configuration
Créer un fichier `.env` à la racine du projet :
```
DB_USER=atlas_weather
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5433
DB_NAME=weather_db
```

### 2. Lancer le pipeline Airflow
```bash
airflow dags unpause atlas_weather_pipeline
airflow tasks run atlas_weather_pipeline extract_cities --execution-date 2026-09-21
```

### 3. Lancer le dashboard Streamlit
```bash
streamlit run dashboard/streamlit_app.py
```

### 4. Inspection de la base de données
```bash
python inspect_db.py
```

### 5. Tester avec les données mock
Remplacer `weather.json` par `weather_mock.json` dans `cleaning.py` pour tester sans l'API.

---

## 📈 Modèle de risque — Détails

Le score de risque global est une **moyenne pondérée** de 6 indicateurs individuels, chacun normalisé de 0 à 100 :

```
risk_score = 0.20 × temp_risk
           + 0.15 × prec_risk
           + 0.15 × prec_probability_risk
           + 0.20 × wind_risk
           + 0.20 × gust_risk
           + 0.10 × weather_code_risk
```

**Interprétation des niveaux :**
- **Low (0-24)** : Conditions normales, aucun risque particulier
- **Moderate (25-49)** : Risque léger, vigilance recommandée
- **High (50-74)** : Risque significatif, précautions nécessaires
- **Extreme (75-100)** : Conditions potentiellement dangereuses, alerte nécessaire

---

## 🔍 Outils utilitaires

### `inspect_db.py`
Script d'inspection de la base PostgreSQL :
- Affiche la base de données et le schéma courant
- Liste toutes les tables
- Vérifie si `weather_risk` existe et affiche ses colonnes
- Liste les clés étrangères de `weather_risk`
