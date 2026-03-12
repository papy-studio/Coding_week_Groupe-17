import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from ucimlrepo import fetch_ucirepo

# Charger la data
dataset = fetch_ucirepo(id=544)
df = pd.concat([dataset.data.features, dataset.data.targets], axis=1)

# Encoder yes/no
binary_cols = ['family_history_with_overweight', 'FAVC', 'SMOKE', 'SCC']
for col in binary_cols:
    df[col] = df[col].map({'yes': 1, 'no': 0})

# Encoder catégorielles
le = LabelEncoder()
for col in ['Gender', 'CAEC', 'CALC', 'MTRANS']:
    df[col] = le.fit_transform(df[col])

# Encoder la cible
le_target = LabelEncoder()
df['NObeyesdad'] = le_target.fit_transform(df['NObeyesdad'])

# Optimiser mémoire
def optimize_memory(df):
    before = df.memory_usage(deep=True).sum() / 1024
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].astype('float32')
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = df[col].astype('int32')
    after = df.memory_usage(deep=True).sum() / 1024
    print(f"Mémoire avant : {before:.1f} KB")
    print(f"Mémoire après : {after:.1f} KB")
    print(f"Réduction     : {((before-after)/before*100):.1f}%")
    return df

df = optimize_memory(df)

# Séparer X et y
X = df.drop(columns=['NObeyesdad'])
y = df['NObeyesdad']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Sauvegarder les CSV
X_train.to_csv('data/X_train.csv', index=False)
X_test.to_csv('data/X_test.csv', index=False)
y_train.to_csv('data/y_train.csv', index=False)
y_test.to_csv('data/y_test.csv', index=False)

print("✅ Fichiers CSV sauvegardés dans data/")
print(f"X_train : {X_train.shape}")
print(f"X_test  : {X_test.shape}")

from sklearn.preprocessing import StandardScaler

# Normaliser la data
# StandardScaler met toutes les features à la même échelle
# moyenne=0 et écart-type=1 pour chaque feature
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# Remplacer dans le modèle
model.fit(X_train_scaled, y_train)
y_pred = model.predict(X_test_scaled)