import pandas as pd
import pickle
import re
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import matplotlib.pyplot as plt
import os

import pickle

os.makedirs("outputs", exist_ok=True)

df = pd.read_csv("offers_analyzed.csv", encoding="utf-8-sig")


SKILLS = [
    "python","java","javascript","php","sql","excel","power bi",
    "sap","salesforce","crm","erp","linux","docker","kubernetes",
    "git","agile","scrum","anglais","français","communication",
    "management","comptabilité","audit","marketing","finance",
    "analyse","reporting","gestion","qualité","logistique",
    "autocad","solidworks","matlab","r studio","machine learning",
    "deep learning","data","cloud","azure","aws"
]

def extract_skills(text):
    if pd.isna(text):
        return []
    text = str(text).lower()
    return [skill for skill in SKILLS if skill in text]

df["skills"] = df["description"].apply(extract_skills)

df_skills = df[df["skills"].apply(len) >= 2]
print(f"{len(df_skills)} offres avec 2+ competences detectees")

te = TransactionEncoder()
te_array = te.fit_transform(df_skills["skills"])
df_encoded = pd.DataFrame(te_array, columns=te.columns_)

print("Apriori en cours...")
frequent_itemsets = apriori(
    df_encoded,
    min_support=0.05,
    use_colnames=True
)
frequent_itemsets["length"] = frequent_itemsets["itemsets"].apply(len)
print(f"    → {len(frequent_itemsets)} itemsets frequents trouves")

rules = association_rules(
    frequent_itemsets,
    metric="confidence",
    min_threshold=0.5
)
rules = rules.sort_values("lift", ascending=False)

print(f"Top 10 regles d'association :")
print(rules[["antecedents","consequents","support","confidence","lift"]].head(10).to_string())

skill_counts = df_skills["skills"].explode().value_counts().head(15)

plt.figure(figsize=(12, 6))
skill_counts.sort_values().plot(kind="barh", color="steelblue")
plt.title("Top 15 Competences les plus demandees")
plt.xlabel("Nombre d'offres")
plt.tight_layout()
plt.savefig("outputs/top_skills.png", dpi=150)
plt.close()
print("\noutputs/top_skills.png sauvegarde")

plt.figure(figsize=(10, 6))
plt.scatter(rules["support"], rules["confidence"],
            c=rules["lift"], cmap="YlOrRd", alpha=0.7, s=80)
plt.colorbar(label="Lift")
plt.xlabel("Support")
plt.ylabel("Confidence")
plt.title("Regles d'association — Support vs Confidence")
plt.tight_layout()
plt.savefig("outputs/association_rules.png", dpi=150)
plt.close()
print("outputs/association_rules.png sauvegarde")


rules.to_csv("outputs/association_rules.csv", index=False, encoding="utf-8-sig")
print("outputs/association_rules.csv sauvegarde")






df["skills"].to_pickle("skills.pkl")
rules.to_pickle("assoc_rules.pkl")
frequent_itemsets.to_pickle("frequent_itemsets.pkl")

print("skills.pkl + assoc_rules.pkl sauvegardés")