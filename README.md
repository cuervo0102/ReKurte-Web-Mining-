# Rekrute Web Mining — Analyse du Marché de l'Emploi au Maroc

## Description

Ce projet est une application complète de Web Mining ciblant Rekrute.ma, le principal portail d'offres d'emploi au Maroc. L'objectif est de collecter, nettoyer et analyser les offres d'emploi afin d'identifier les tendances du marché du travail marocain : secteurs qui recrutent, compétences les plus demandées, répartition géographique et profils recherchés.



---

## Structure du projet

```
ReKrute-Mining/
├── data/
│   ├── offer_urls.json         # URLs collectées par le crawler
│   ├── offers_raw.json         # Données brutes extraites par le scraper
│   ├── offers_clean.csv        # Données nettoyées
│   └── offers_analyzed.csv     # Données analysées avec clusters
├── models/
│   ├── tfidf_vectorizer.pkl    # Vectorizer TF-IDF sauvegardé
│   ├── tfidf_matrix.npz        # Matrice TF-IDF sauvegardée
│   ├── clf_results.pkl         # Résultats de classification
│   ├── skills.pkl              # Compétences extraites
│   └── assoc_rules.pkl         # Règles d'association
├── outputs/
│   ├── wordcloud_global.png
│   ├── top_secteurs.png
│   ├── top_villes.png
│   ├── top_skills.png
│   ├── experience.png
│   ├── clusters.png
│   ├── confusion_matrix.png
│   ├── model_comparison.png
│   └── association_rules.png
├── crawler.py
├── scraper.py
├── cleaner.py
├── analyzer.py
├── classifier.py
├── association.py
└── dashboard.py
```

---

## Pipeline

### Etape 1 — Crawling (crawler.py)

Parcourt les pages de liste de Rekrute.ma et collecte les URLs de toutes les offres d'emploi disponibles.

- Source : rekrute.com/offres.html
- Pagination via le parametre p
- Resultat : offer_urls.json (1795 URLs)

### Etape 2 — Scraping (scraper.py)

Pour chaque URL collectee, extrait les donnees structurees de l'offre d'emploi.

Champs extraits :
- Titre du poste
- Entreprise
- Ville
- Secteur d'activite et fonction
- Experience requise
- Niveau d'etude
- Type de contrat
- Teletravail
- Description complete

Resultat : offers_raw.json (1788 offres)

### Etape 3 — Nettoyage (cleaner.py)

- Suppression des doublons
- Normalisation des chaines de caracteres
- Extraction du secteur et de la fonction depuis le champ combine
- Extraction de l'experience, du niveau d'etude et du contrat depuis la description
- Reconstitution des villes manquantes depuis le titre ou l'URL

Resultat : offers_clean.csv

### Etape 4 — Analyse (analyzer.py)

- Nettoyage du texte des descriptions (stopwords, regex)
- Vectorisation TF-IDF (300 features, min_df=3, max_df=0.85)
- Clustering KMeans (6 clusters)
- Generation des visualisations : wordcloud, top secteurs, top villes, experience, clusters
- Sauvegarde du vectorizer et de la matrice TF-IDF pour reutilisation

Resultat : offers_analyzed.csv, tfidf_vectorizer.pkl, tfidf_matrix.npz

### Etape 5 — Classification (classifier.py)

Comparaison de deux modeles de classification supervises sur les secteurs d'activite.

- Modele 1 : Logistic Regression — Accuracy : 88.65%
- Modele 2 : Naive Bayes — Accuracy : 74.59%
- Meilleur modele : Logistic Regression

Resultat : clf_results.pkl, confusion_matrix.png, model_comparison.png

### Etape 6 — Regles d'association (association.py)

Extraction des competences techniques et soft skills depuis les descriptions, puis generation des regles d'association via l'algorithme Apriori.

- min_support : 0.04
- min_confidence : 0.4
- Librairie : mlxtend

Resultat : skills.pkl, assoc_rules.pkl, top_skills.png, association_rules.png



## Installation

```bash
# Creer un environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS

# Installer les dependances
pip install requests beautifulsoup4 pandas scikit-learn
pip install wordcloud matplotlib seaborn
pip install dash plotly mlxtend
pip install scipy
```

---

## Execution

Lancer les scripts dans cet ordre :

```bash
python crawler.py       # collecte les URLs
python scraper.py       # extrait les donnees
python cleaner.py       # nettoie le dataset
python analyzer.py      # TF-IDF + clustering + visualisations
python classifier.py    # classification supervisee
python association.py   # regles d'association
python dashboard.py     # lance le dashboard sur http://localhost:8050
```

Chaque script verifie si ses fichiers de sortie existent deja avant de recalculer.
Pour forcer le recalcul : `python script.py --force`

---

## Resultats principaux

| Metrique | Valeur |
|---|---|
| Offres collectees | 1788 |
| Pages crawlees | 180 |
| Taux de succes scraping | 99.6% |
| Secteurs identifies | 15 |
| Accuracy Logistic Regression | 88.65% |
| Accuracy Naive Bayes | 74.59% |
| Clusters KMeans | 6 |
| Regles d'association generees | 60+ |

### Principaux enseignements

- Casablanca concentre 43% des offres d'emploi, suivie de Rabat (17%)
- Banque/Finance est le secteur qui recrute le plus (143 offres)
- Le profil le plus demande : 1 a 3 ans d'experience, niveau Bac+4/5
- Les competences transversales les plus demandees : management, gestion, finance, comptabilite
- La Logistic Regression surpasse largement Naive Bayes pour la classification de texte multiclasse

---

## Technologies utilisees

| Categorie | Outils |
|---|---|
| Collecte | requests, BeautifulSoup4, Scrapy |
| Traitement | pandas, numpy, re |
| Machine Learning | scikit-learn (TF-IDF, KMeans, LogisticRegression, MultinomialNB) |
| Association Rules | mlxtend (Apriori) |
| Visualisation | matplotlib, seaborn, wordcloud, plotly |
| Dashboard | Dash, Plotly |
| Stockage | JSON, CSV, pickle, scipy.sparse |

