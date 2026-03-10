import pandas as pd
import joblib
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix, precision_recall_curve
from imblearn.over_sampling import SMOTE

print("Loading data...")
df = pd.read_csv("sepsis_raw.csv")
df = df[['Patient_ID', 'HR', 'O2Sat', 'Temp', 'SepsisLabel']].copy()

print(f"Raw rows: {len(df)}")
print(f"Unique patients: {df['Patient_ID'].nunique()}")

print("Aggregating per patient...")
agg = df.groupby('Patient_ID').agg(
    HR_max    = ('HR',          'max'),
    HR_mean   = ('HR',          'mean'),
    SpO2_min  = ('O2Sat',       'min'),
    SpO2_mean = ('O2Sat',       'mean'),
    Temp_max  = ('Temp',        'max'),
    Temp_mean = ('Temp',        'mean'),
    sepsis    = ('SepsisLabel', 'max'),
).reset_index()

print(f"Patients: {len(agg)}")
print(f"Sepsis patients: {agg['sepsis'].sum()} ({agg['sepsis'].mean()*100:.1f}%)")

X = agg[['HR_max', 'HR_mean', 'SpO2_min', 'SpO2_mean', 'Temp_max', 'Temp_mean']]
y = agg['sepsis'].astype(int)

imputer = SimpleImputer(strategy='median')
X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=67, stratify=y
)

sm = SMOTE(random_state=42)
X_train, y_train = sm.fit_resample(X_train, y_train)
print(f"After SMOTE — Sepsis: {y_train.sum()}, Normal: {len(y_train)-y_train.sum()}")

print("Training...")
model = RandomForestClassifier(
    n_estimators=400,
    max_depth=20,        # prevents trees from memorising training data
    min_samples_leaf=5,  # each leaf needs at least 5 patients
    class_weight='balanced',  # tells the model to penalise missing sepsis cases more
    random_state=67,
    n_jobs=-1
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

auc = roc_auc_score(y_test, y_prob)
f1  = f1_score(y_test, y_pred)
cm  = confusion_matrix(y_test, y_pred)

print(f"\nAUC-ROC : {auc:.4f}")
print(f"F1 Score: {f1:.4f}")
print(f"\nConfusion Matrix (default threshold 0.5):")
print(f"               Predicted No  Predicted Yes")
print(f"Actual No          {cm[0][0]:6d}        {cm[0][1]:6d}")
print(f"Actual Sepsis      {cm[1][0]:6d}        {cm[1][1]:6d}")
print(f"Missed sepsis: {cm[1][0]}")

# Find the threshold where we catch at least 70% of real sepsis cases
# In healthcare, missing a sick patient is worse than a false alarm
print("\nFinding best threshold for healthcare...")
precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
best_t = thresholds[0]
for t, p, r in zip(thresholds, precision, recall):
    if r >= 0.70:
        best_t = t
        print(f"Use this threshold in app.py: {t:.4f}")
        print(f"At this threshold — Precision: {p:.3f}, Recall: {r:.3f}")
        print(f"Meaning: catches {r*100:.1f}% of real sepsis cases")
        break

# Show confusion matrix at best threshold
y_pred_best = (y_prob >= best_t).astype(int)
cm2 = confusion_matrix(y_test, y_pred_best)
print(f"\nConfusion Matrix at threshold {best_t:.4f}:")
print(f"               Predicted No  Predicted Yes")
print(f"Actual No          {cm2[0][0]:6d}        {cm2[0][1]:6d}")
print(f"Actual Sepsis      {cm2[1][0]:6d}        {cm2[1][1]:6d}")
print(f"Missed sepsis: {cm2[1][0]}  (was {cm[1][0]} at default threshold)")

print(f"\nFeature Importance:")
for feat, score in sorted(zip(X.columns, model.feature_importances_), key=lambda x: -x[1]):
    print(f"  {feat}: {score:.4f}")

joblib.dump(model, "sepsis_model.pkl")
joblib.dump(imputer, "imputer.pkl")

# Input: [HR_max, HR_mean, SpO2_min, SpO2_mean, Temp_max, Temp_mean]
# For single sensor reading: [hr, hr, spo2, spo2, temp, temp]
# Update HIGH RISK threshold in app.py with the value printed above
print("\nDone.")