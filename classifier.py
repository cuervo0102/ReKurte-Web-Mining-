import pandas as pd
import pickle
import scipy.sparse as sp
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs("outputs", exist_ok=True)


df = pd.read_csv("offers_analyzed.csv", encoding="utf-8-sig")

print("Chargement TF-IDF...")
with open("tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

X_full = sp.load_npz("tfidf_matrix.npz")


top_secteurs = df["secteur"].value_counts()
top_secteurs = top_secteurs[top_secteurs >= 30].index
mask = df["secteur"].isin(top_secteurs)

X = X_full[mask.values]
y = df[mask]["secteur"].reset_index(drop=True)

print(f"Dataset : {len(y)} offres, {len(top_secteurs)} secteurs")
print(f"Secteurs : {list(top_secteurs)}")


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Logistic Regression...")
lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)
print(classification_report(y_test, y_pred_lr))

print("\nNaive Bayes...")
nb = MultinomialNB()
nb.fit(X_train, y_train)
y_pred_nb = nb.predict(X_test)
print(classification_report(y_test, y_pred_nb))

acc_lr = accuracy_score(y_test, y_pred_lr)
acc_nb = accuracy_score(y_test, y_pred_nb)


print(f"Logistic Regression accuracy : {acc_lr:.2%}")
print(f"Naive Bayes accuracy         : {acc_nb:.2%}")
print(f"Meilleur modele              : {'Logistic Regression' if acc_lr > acc_nb else 'Naive Bayes'}")

best_pred = y_pred_lr if acc_lr > acc_nb else y_pred_nb
cm = confusion_matrix(y_test, best_pred, labels=top_secteurs)

plt.figure(figsize=(14, 10))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=top_secteurs,
            yticklabels=top_secteurs)
plt.title("Confusion Matrix — Classification par Secteur")
plt.ylabel("Reel")
plt.xlabel("Predit")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("outputs/confusion_matrix.png", dpi=150)
plt.close()
print("outputs/confusion_matrix.png sauvegarde")

models = ["Logistic Regression", "Naive Bayes"]
scores = [acc_lr, acc_nb]

plt.figure(figsize=(7, 4))
bars = plt.bar(models, scores, color=["steelblue", "coral"])
plt.ylim(0, 1)
plt.title("Comparaison des modeles de classification")
plt.ylabel("Accuracy")
for bar, score in zip(bars, scores):
    plt.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 0.01,
             f"{score:.2%}", ha="center", fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/model_comparison.png", dpi=150)
plt.close()
print("outputs/model_comparison.png sauvegarde")