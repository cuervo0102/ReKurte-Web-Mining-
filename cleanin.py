# cleaner.py
import json
import pandas as pd
import re

with open("offers_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# ── 1. Doublons & lignes sans titre
df.drop_duplicates(subset=["url"], inplace=True)
df.dropna(subset=["titre"], inplace=True)

# ── 2. Nettoyer tous les strings (espaces, tabs, newlines)
str_cols = df.select_dtypes(include=["object", "str"]).columns
for col in str_cols:
    df[col] = df[col].apply(lambda x: re.sub(r'\s+', ' ', str(x)).strip() if pd.notna(x) else x)

# ── 3. Extraire secteur et fonction proprement
df["secteur"] = df["fonction_secteur"].str.extract(r'[Ss]ecteur\s*[:/–-]?\s*(.+)$')
df["fonction"] = df["fonction_secteur"].str.extract(r'^(.+?)\s*[-–]\s*[Ss]ecteur')
df["secteur"] = df["secteur"].str.strip()
df["fonction"] = df["fonction"].str.strip()

# ── 4. Extraire experience/niveau/contrat depuis description ou titre
#    (car les featureInfo li ne sont pas bien parsés)
def extract_from_description(desc, patterns):
    if pd.isna(desc):
        return None
    for pattern in patterns:
        match = re.search(pattern, str(desc), re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

# Expérience
exp_patterns = [
    r'[Ee]xp[eé]rience\s*(?:requise)?\s*[:/]\s*([^\n|]+)',
    r'(\d+\s*[àa]\s*\d+\s*ans?)',
    r'(Junior|Confirmé|Senior|Débutant)[^,\n]*'
]
df["experience_ext"] = df["description"].apply(
    lambda x: extract_from_description(x, exp_patterns)
)

# Niveau étude
niveau_patterns = [
    r"[Nn]iveau\s*d'[eé]tude\s*[:/]\s*([^\n|]+)",
    r'(Bac\s*[+\d]+[^\n,]*)',
    r'(Master|Licence|Ingénieur|Doctorat)[^\n,]*'
]
df["niveau_ext"] = df["description"].apply(
    lambda x: extract_from_description(x, niveau_patterns)
)

# Contrat
contrat_patterns = [
    r'[Tt]ype\s*de\s*contrat\s*[:/]\s*([^\n|]+)',
    r'\b(CDI|CDD|Stage|Freelance|Intérim)\b'
]
df["contrat_ext"] = df["description"].apply(
    lambda x: extract_from_description(x, contrat_patterns)
)

# ── 5. Ville depuis titre si manquante
villes = ['casablanca','rabat','marrakech','tanger','agadir',
          'fes','meknes','oujda','kenitra','tetouan','laayoune',
          'settat','mohammedia','beni mellal']

def extract_ville(row):
    if pd.notna(row.get("ville")):
        return str(row["ville"]).capitalize()
    for source in [str(row.get("titre","")), str(row.get("url",""))]:
        for v in villes:
            if v in source.lower():
                return v.capitalize()
    return "Autre"

df["ville"] = df.apply(extract_ville, axis=1)

# ── 6. Entreprise depuis titre si manquante
def extract_entreprise(row):
    if pd.notna(row.get("entreprise")) and str(row["entreprise"]) != "nan":
        return row["entreprise"]
    url = str(row.get("url", ""))
    match = re.search(r'-recrutement-(.+?)-\d+\.html', url)
    if match:
        return match.group(1).replace("-", " ").title()
    return None

df["entreprise"] = df.apply(extract_entreprise, axis=1)

# ── 7. Rapport final
print("=== AFTER CLEANING ===")
print(f"Total offres     : {len(df)}")
print(f"\nNulls restants :\n{df.isnull().sum()}")
print(f"\nTop villes :\n{df['ville'].value_counts().head(10)}")
print(f"\nTop secteurs :\n{df['secteur'].value_counts().head(10)}")
print(f"\nTop contrats :\n{df['contrat_ext'].value_counts().head(5)}")
print(f"\nTop expériences :\n{df['experience_ext'].value_counts().head(5)}")

df.to_csv("offers_clean.csv", index=False, encoding="utf-8-sig")
print(f"\n[✓] offers_clean.csv sauvegardé — {len(df)} offres")