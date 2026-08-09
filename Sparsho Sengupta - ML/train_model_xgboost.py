import pandas as pd
import joblib
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    confusion_matrix,
    precision_recall_curve,
)
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

print("Loading data...")
df = pd.read_csv("sepsis_raw.csv")
df = df[["Patient_ID", "HR", "O2Sat", "Temp", "SepsisLabel"]].copy()

agg = (
    df.groupby("Patient_ID")
    .agg(
        HR_max=("HR", "max"),
        HR_mean=("HR", "mean"),
        SpO2_min=("O2Sat", "min"),
        SpO2_mean=("O2Sat", "mean"),
        Temp_max=("Temp", "max"),
        Temp_mean=("Temp", "mean"),
        sepsis=("SepsisLabel", "max"),
    )
    .reset_index()
)

X = agg[["HR_max", "HR_mean", "SpO2_min", "SpO2_mean", "Temp_max", "Temp_mean"]]
y = agg["sepsis"].astype(int)

imputer = SimpleImputer(strategy="median")
X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=67, stratify=y
)

sm = SMOTE(random_state=42)
X_train, y_train = sm.fit_resample(X_train, y_train)

print("Training XGBoost...")
model = XGBClassifier(
    n_estimators=400,
    max_depth=6,  # shallower than RF — XGBoost prefers this
    learning_rate=0.05,  # slow learning = better generalisation
    subsample=0.8,  # use 80% of data per tree
    colsample_bytree=0.8,  # use 80% of features per tree
    scale_pos_weight=12,  # handles class imbalance (ratio of normal:sepsis)
    random_state=67,
    n_jobs=-1,
    eval_metric="auc",
    use_label_encoder=False,
)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=50)

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

auc = roc_auc_score(y_test, y_prob)
f1 = f1_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print(f"\nXGBoost AUC-ROC : {auc:.4f}")
print(f"XGBoost F1 Score: {f1:.4f}")

precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
for t, p, r in zip(thresholds, precision, recall):
    if r >= 0.70:
        print(f"\nBest threshold: {t:.4f}")
        print(f"Precision: {p:.3f}  Recall: {r:.3f}")
        break

print("\nFeature Importances:")
for feat, score in sorted(
    zip(X.columns, model.feature_importances_), key=lambda x: -x[1]
):
    print(f"  {feat}: {score:.4f}")

joblib.dump(model, "sepsis_model_xgb.pkl")
joblib.dump(imputer, "imputer_xgb.pkl")
print("\nSaved: sepsis_model_xgb.pkl and imputer_xgb.pkl")
