import pandas as pd
from pathlib import Path

# Dossier où se trouvent les fichiers CSV bruts
BASE = Path(".")

# Fichiers d'entrée
SRC = {
    "Hourly": BASE / "Pharma_Ventes_Hourly.csv",
    "Daily": BASE / "Pharma_Ventes_Daily.csv",
    "Weekly": BASE / "Pharma_Ventes_Weekly.csv",
    "Monthly": BASE / "Pharma_Ventes_Monthly.csv",
}

# Fichiers de sortie
OUT = {
    "Hourly": BASE / "clean_hourly_full.csv",
    "Daily": BASE / "clean_daily_full.csv",
    "Weekly": BASE / "clean_weekly_full.csv",
    "Monthly": BASE / "clean_monthly_full.csv",
    "All": BASE / "pharma_consolidated_full.csv",
}

# Étape 1 : détecter toutes les colonnes existantes dans les fichiers
all_columns = set()
for p in SRC.values():
    df_tmp = pd.read_csv(p, sep=None, engine="python", nrows=5)
    all_columns.update(df_tmp.columns)
# On force la présence de datum et granularite
all_columns.update(["datum", "granularite"])
all_columns = list(all_columns)

# === Réorganisation manuelle des colonnes (ordre prioritaire) ===
preferred_order = [
    "granularite",
    "datum",
    "Year",
    "Month",
    "Weekday Name",
    "Hour",
    "M01AB",
    "M01AE",
    "N02BA",
    "N02BE",
    "N05B",
    "N05C",
    "R03",
    "R06",
]
# Colonnes restantes détectées automatiquement mais non listées ci-dessus
remaining = [c for c in all_columns if c not in preferred_order]
# Nouvel ordre final
all_columns = preferred_order + remaining

# Fonctions utilitaires
def read_csv_auto(p: Path) -> pd.DataFrame:
    return pd.read_csv(p, sep=None, engine="python")

def to_datetime_robust(series: pd.Series, monthly: bool = False) -> pd.Series:
    """Conversion robuste de 'datum' en datetime."""
    if monthly:
        s = pd.to_datetime(series, errors="coerce")
        if s.isna().any():
            s = pd.to_datetime(series, errors="coerce", dayfirst=True)
        return s
    else:
        s = pd.to_datetime(series, errors="coerce", dayfirst=True)
        if s.isna().any():
            s2 = pd.to_datetime(series, errors="coerce")
            s = s.fillna(s2)
        return s

def clean_with_all_columns(df: pd.DataFrame, level: str, all_cols: list) -> pd.DataFrame:
    """Nettoyage qui conserve toutes les colonnes globales dans l'ordre souhaité."""
    df = df.copy()
    monthly = (level == "Monthly")
    if 'datum' in df.columns:
        df['datum'] = to_datetime_robust(df['datum'], monthly=monthly)
    else:
        df['datum'] = pd.NaT
    df['granularite'] = level
    # Crée les colonnes manquantes
    for col in all_cols:
        if col not in df.columns:
            df[col] = pd.NA
    # Réordonne selon all_cols
    df = df[all_cols]
    return df

# Étape 2 : nettoyage des fichiers
dfs_clean = {}
report = []

for level, path in SRC.items():
    raw = read_csv_auto(path)
    clean = clean_with_all_columns(raw, level, all_columns)
    dfs_clean[level] = clean
    clean.to_csv(OUT[level], index=False)
    report.append({
        "Fichier": path.name,
        "Granularite": level,
        "Lignes": clean.shape[0],
        "Colonnes": clean.shape[1],
        "Dates min": str(clean['datum'].min()),
        "Dates max": str(clean['datum'].max())
    })

# Étape 3 : consolidation dans un fichier unique
df_all = pd.concat(list(dfs_clean.values()), ignore_index=True)
df_all.to_csv(OUT["All"], index=False)

# Étape 4 : rapport
print("\n=== Rapport de nettoyage ===")
for r in report:
    print(f"{r['Fichier']:<30} | {r['Granularite']:<8} | Lignes: {r['Lignes']:<6} | Colonnes: {r['Colonnes']:<3} | Dates: {r['Dates min']} → {r['Dates max']}")

print("\n=== Fichiers générés ===")
for k, p in OUT.items():
    print(f"- {k}: {p}")
