#analyzer.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
import re
import os

matplotlib.use("Agg")
os.makedirs("outputs", exist_ok=True)

df = pd.read_csv("offers_clean.csv", encoding="utf-8-sig")

#Normaliser
df["contrat_clean"] = df["contrat_ext"].str.upper().str.strip()
df["contrat_clean"] = df["contrat_clean"].replace({
    "CDI - TELETRAVAIL : NON": "CDI",
    "CDI - TELETRAVAIL : OUI": "CDI",
    "CDD - TELETRAVAIL : NON": "CDD",
    "STAGE": "Stage",
})
df["contrat_clean"] = df["contrat_clean"].where(
    df["contrat_clean"].isin(["CDI","CDD","Stage","Freelance","Interim"]), None
)

#Nettoyage texte description
STOPWORDS_FR = set([
    "de","du","la","le","les","des","et","en","un","une","pour",
    "dans","sur","avec","par","au","aux","est","sont","nous","vous",
    "ils","elle","que","qui","se","sa","son","ses","leur","leurs",
    "ce","ou","mais","donc","car","ni","ne","pas","plus","très",
    "être","avoir","faire","tout","bien","cette","ces","ils","nous"
])

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-zàâäeèêëîïôùûüçœæ\s]', ' ', text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS_FR and len(t) > 3]
    return " ".join(tokens)

df["text_clean"] = df["description"].apply(clean_text)

#TF-IDF
print("TF-IDF en cours...")
vectorizer = TfidfVectorizer(max_features=300, min_df=3, max_df=0.85)
X = vectorizer.fit_transform(df["text_clean"])
features = vectorizer.get_feature_names_out()

#Top 20 mots globaux
scores = X.mean(axis=0).A1
top_words = sorted(zip(features, scores), key=lambda x: -x[1])[:20]
print("\nTop 20 mots TF-IDF :")
for word, score in top_words:
    print(f"  {word:30s} {score:.4f}")

#Clustering KMeans
print("\nClustering KMeans...")
kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(X)

#Mots cles par cluster
print("\nMots cles par cluster :")
order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
for i in range(6):
    top = [features[j] for j in order_centroids[i, :8]]
    print(f"  Cluster {i} : {', '.join(top)}")

#Visualisations
print("\nGeneration des visualisations...")

#Wordcloud global
all_text = " ".join(df["text_clean"].dropna())
wc = WordCloud(width=1200, height=600, background_color="white",
               colormap="viridis", max_words=150).generate(all_text)
plt.figure(figsize=(14, 7))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.title("Competences les plus demandees — Rekrute.ma", fontsize=16)
plt.tight_layout()
plt.savefig("outputs/wordcloud_global.png", dpi=150)
plt.close()
print("wordcloud_global.png")

#Top 10 secteurs
plt.figure(figsize=(12, 6))
df["secteur"].value_counts().head(10).sort_values().plot(
    kind="barh", color="steelblue"
)
plt.title("Top 10 Secteurs qui recrutent")
plt.xlabel("Nombre d'offres")
plt.tight_layout()
plt.savefig("outputs/top_secteurs.png", dpi=150)
plt.close()
print("top_secteurs.png")

#Top 10 villes
plt.figure(figsize=(10, 5))
df[df["ville"] != "Autre"]["ville"].value_counts().head(10).sort_values().plot(
    kind="barh", color="coral"
)
plt.title("Top 10 Villes qui recrutent")
plt.xlabel("Nombre d'offres")
plt.tight_layout()
plt.savefig("outputs/top_villes.png", dpi=150)
plt.close()
print("top_villes.png")

#Distribution experience
plt.figure(figsize=(10, 5))
df["experience_ext"].value_counts().head(8).sort_values().plot(
    kind="barh", color="mediumseagreen"
)
plt.title("Experience requise")
plt.xlabel("Nombre d'offres")
plt.tight_layout()
plt.savefig("outputs/experience.png", dpi=150)
plt.close()
print("experience.png")

#Repartition clusters
plt.figure(figsize=(8, 5))
df["cluster"].value_counts().sort_index().plot(
    kind="bar", color="mediumpurple", rot=0
)
plt.title("Repartition des offres par cluster")
plt.xlabel("Cluster")
plt.ylabel("Nombre d'offres")
plt.tight_layout()
plt.savefig("outputs/clusters.png", dpi=150)
plt.close()
print("clusters.png")

#Sauvegarder dataset final
df.to_csv("offers_analyzed.csv", index=False, encoding="utf-8-sig")
print(f" Analyse terminee — offers_analyzed.csv sauvegarde")
print(f"Visualisations dans /outputs/")