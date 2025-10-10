# app.py

# config de page
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import altair as alt

st.set_page_config(page_title="Pharma analyse light", layout="wide")
st.title("Analyse des ventes pharmaceutiques")

# constantes
DEFAULT_PATH = Path("pharma_consolidated_full.csv")
DATE_COL = "datum"
KNOWN_PRODUCTS = ["M01AB", "M01AE", "N02BA", "N02BE", "N05B", "N05C", "R03", "R06"]
TOPK_STACK = 8
SAMPLE_THRESHOLD = 2_000_000
SAMPLE_FRAC = 0.25
FAST_MODE = True

# chargement fichier
with st.sidebar:
    st.header("Données")
    use_uploader = st.toggle("Importer un fichier")
    if use_uploader:
        uploaded = st.file_uploader("Déposer un CSV", type=["csv"])
        if uploaded is None:
            st.stop()
        head_source = uploaded
        path = None
    else:
        if not DEFAULT_PATH.exists():
            st.error(f"Fichier introuvable {DEFAULT_PATH.resolve()}")
            st.stop()
        head_source = DEFAULT_PATH
        path = DEFAULT_PATH

# detection colonnes disponibles
def read_head(src):
    if isinstance(src, Path):
        return pd.read_csv(src, nrows=5)
    else:
        src.seek(0)
        dfh = pd.read_csv(src, nrows=5)
        src.seek(0)
        return dfh

head_df = read_head(head_source)

if DATE_COL not in head_df.columns:
    st.error(f"colonne {DATE_COL} absente")
    st.stop()

present_products = [c for c in KNOWN_PRODUCTS if c in head_df.columns]
has_hour = "Hour" in head_df.columns

usecols = [DATE_COL] + present_products + (["Hour"] if has_hour else [])
dtype_map = {c: "float32" for c in present_products}

# lecture optimisée
@st.cache_data(show_spinner=True)
def load_optimized_csv(path, uploaded, usecols, dtype_map, date_col, fast_mode, sample_threshold, sample_frac):
    if uploaded is not None:
        df = pd.read_csv(uploaded, usecols=[c for c in usecols if c], dtype=dtype_map)
    else:
        df = pd.read_csv(path, usecols=[c for c in usecols if c], dtype=dtype_map)
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce", infer_datetime_format=True)
    df = df.dropna(subset=[date_col])
    if fast_mode and len(df) > sample_threshold:
        df = df.sample(frac=sample_frac, random_state=42).sort_values(date_col)
    return df

df = load_optimized_csv(
    path=path,
    uploaded=uploaded if use_uploader else None,
    usecols=usecols,
    dtype_map=dtype_map,
    date_col=DATE_COL,
    fast_mode=FAST_MODE,
    sample_threshold=SAMPLE_THRESHOLD,
    sample_frac=SAMPLE_FRAC,
)

# dates disponibles et snapping
available_dates = pd.to_datetime(df[DATE_COL].dt.date).sort_values().unique()
if len(available_dates) == 0:
    st.error("aucune date valide")
    st.stop()

min_date = pd.to_datetime(available_dates[0]).date()
max_date = pd.to_datetime(available_dates[-1]).date()

def snap_range_to_available(d1, d2, avail_np):
    if d1 > d2:
        return None, None
    d1d = np.datetime64(pd.to_datetime(d1).date())
    d2d = np.datetime64(pd.to_datetime(d2).date())
    i = avail_np.searchsorted(d1d, side="left")
    j = avail_np.searchsorted(d2d, side="right") - 1
    if i >= len(avail_np) or j < 0 or i > j:
        return None, None
    start_snap = pd.to_datetime(avail_np[i]).normalize()
    end_snap_excl = pd.to_datetime(avail_np[j]).normalize() + pd.Timedelta(days=1)
    return start_snap, end_snap_excl

# filtres ui
st.subheader("Filtres")
c1, c2, c3 = st.columns([2, 2, 2])

# filtre produits
with c1:
    all_products = present_products
    selected_products = st.multiselect("Produits", options=all_products, default=all_products)

if not selected_products:
    st.info("sélectionner au moins un produit")
    st.stop()

# filtre période
with c2:
    date_selection = st.date_input(
        "Période",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD",
    )
    if isinstance(date_selection, tuple) and len(date_selection) == 2:
        d1, d2 = date_selection
        if d1 is None or d2 is None:
            st.info("sélectionner deux dates début et fin")
            st.stop()
        start_dt, end_dt = snap_range_to_available(d1, d2, available_dates)
        if start_dt is None or end_dt is None:
            st.info("la plage choisie ne contient aucune date disponible")
            st.stop()
    else:
        st.info("sélectionner deux dates début et fin")
        st.stop()

# filtre granularité
with c3:
    granularity = st.radio("Granularité", ["Heure", "Jour", "Semaine", "Mois"], horizontal=True)
    rule_map = {"Heure": "H", "Jour": "D", "Semaine": "W-MON", "Mois": "MS"}
    rule = rule_map[granularity]

# application filtres
base_cols = [DATE_COL] + selected_products + (["Hour"] if "Hour" in df.columns else [])
mask_cur = (df[DATE_COL] >= start_dt) & (df[DATE_COL] < end_dt)
df_cur = df.loc[mask_cur, base_cols].copy()

# agrégation
@st.cache_data(show_spinner=False)
def resample_sum_wide(df_wide, date_col, rule):
    if df_wide.empty:
        return df_wide
    return (
        df_wide.set_index(date_col)
               .sort_index()
               .resample(rule)
               .sum(min_count=1)
               .reset_index()
    )

cur_resampled = resample_sum_wide(df_cur[[DATE_COL] + selected_products], DATE_COL, rule)

# kpi
def kpis_from_resampled(resampled):
    if resampled.empty:
        return 0.0, np.nan, "—", 0
    prod_cols = [c for c in resampled.columns if c != DATE_COL]
    total = resampled[prod_cols].sum().sum()
    daily = resample_sum_wide(df_cur[[DATE_COL] + selected_products], DATE_COL, "D")
    daily_total = daily[prod_cols].sum(axis=1) if not daily.empty else pd.Series(dtype="float32")
    daily_avg = float(daily_total.mean()) if not daily_total.empty else np.nan
    totals_by_prod = resampled[prod_cols].sum(axis=0).sort_values(ascending=False)
    top_prod = totals_by_prod.index[0] if len(totals_by_prod) else "—"
    n_points = len(resampled)
    return float(total), daily_avg, top_prod, n_points

st.markdown("---")
st.header("Indicateurs clés")
cur_total, cur_daily_avg, cur_top, n_points = kpis_from_resampled(cur_resampled)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Quantité totale (g)", f"{cur_total:,.0f}".replace(",", " "))
with k2:
    st.metric("Moyenne journalière (g)", "—" if pd.isna(cur_daily_avg) else f"{cur_daily_avg:,.2f}".replace(",", " "))
with k3:
    st.metric("Top produit", cur_top)
with k4:
    st.metric("Points temporels", f"{n_points}")

# line chart
st.markdown("---")
st.header("Évolution des ventes")

def to_long_total(rdf):
    if rdf.empty:
        return pd.DataFrame(columns=[DATE_COL, "value"])
    prod_cols = [c for c in rdf.columns if c != DATE_COL]
    return pd.DataFrame({DATE_COL: rdf[DATE_COL], "value": rdf[prod_cols].sum(axis=1)})

def fmt_time(s, granularity):
    if granularity == "Heure":
        return s.dt.strftime("%Y-%m-%d %H:00")
    if granularity == "Jour":
        return s.dt.strftime("%Y-%m-%d")
    if granularity == "Semaine":
        iso = s.dt.isocalendar()
        return ("S" + iso["week"].astype(str) + " " + iso["year"].astype(str))
    return s.dt.strftime("%Y-%m")

line_df = to_long_total(cur_resampled)
line_df["label"] = fmt_time(line_df[DATE_COL], granularity)

line_chart = alt.Chart(line_df).mark_line().encode(
    x=alt.X("label:N", title="Temps", sort=None),
    y=alt.Y("value:Q", title="Quantité (g)"),
    tooltip=["label", alt.Tooltip("value:Q", title="Quantité (g)")]
).properties(height=320)
st.altair_chart(line_chart, use_container_width=True)

# stacked area
st.markdown("---")
st.header("Contribution des produits")

if not cur_resampled.empty:
    prod_cols = [c for c in cur_resampled.columns if c != DATE_COL]
    totals_by_prod = cur_resampled[prod_cols].sum(axis=0).sort_values(ascending=False)
    topk = totals_by_prod.index[:TOPK_STACK].tolist()
    others = [c for c in prod_cols if c not in topk]

    area_df = cur_resampled[[DATE_COL] + topk].copy()
    if others:
        area_df["Autres"] = cur_resampled[others].sum(axis=1)

    area_long = area_df.melt(id_vars=[DATE_COL], var_name="product", value_name="value")
    area_long["label"] = fmt_time(area_long[DATE_COL], granularity)

    stack_mode = st.radio("Mode de stack", ["Part relative", "Valeur absolue"], horizontal=True)
    y_enc = alt.Y(
        "value:Q",
        title=("Part" if stack_mode == "Part relative" else "Quantité (g)"),
        stack=("normalize" if stack_mode == "Part relative" else True)
    )

    area_chart = alt.Chart(area_long).mark_area().encode(
        x=alt.X("label:N", title="Temps", sort=None),
        y=y_enc,
        color=alt.Color("product:N", title="Produit"),
        tooltip=["product", "label", alt.Tooltip("value:Q", title="Quantité (g)")]
    ).properties(height=320)
    st.altair_chart(area_chart, use_container_width=True)
else:
    st.info("pas de données pour cette période")

# bar chart
st.markdown("---")
st.header("Top et bottom produits")

if not cur_resampled.empty:
    prod_cols = [c for c in cur_resampled.columns if c != DATE_COL]
    totals = cur_resampled[prod_cols].sum(axis=0).reset_index()
    totals.columns = ["product", "Quantité (g)"]

    b1, b2 = st.columns([2, 1])
    with b1:
        mode_rank = st.radio("Classement", ["Top", "Bottom"], horizontal=True)
    with b2:
        n_rank = st.number_input("Nombre de produits affichés", 3, 50, 10, 1)

    totals = totals.sort_values("Quantité (g)", ascending=(mode_rank == "Bottom")).head(int(n_rank))

    bar_chart = alt.Chart(totals).mark_bar().encode(
        x=alt.X("Quantité (g):Q", title="Quantité (g)"),
        y=alt.Y("product:N", sort="-x", title="Produit"),
        tooltip=["product", "Quantité (g)"]
    ).properties(height=max(250, 22 * len(totals)))
    st.altair_chart(bar_chart, use_container_width=True)
else:
    st.info("pas de données à agréger pour le classement")

# heatmap
st.markdown("---")
st.header("Heatmap des pics")

if "Hour" not in df_cur.columns:
    st.info("heatmap indisponible colonne Hour absente")
else:
    cur_for_heat = df_cur.dropna(subset=["Hour"]).copy()
    cur_for_heat["Heure"] = pd.to_numeric(cur_for_heat["Hour"], errors="coerce")
    cur_for_heat = cur_for_heat[(cur_for_heat["Heure"] >= 0) & (cur_for_heat["Heure"] <= 23)]
    cur_for_heat["Heure"] = cur_for_heat["Heure"].astype(int)

    if cur_for_heat.empty:
        st.info("aucune donnée horaire valide")
    else:
        cur_for_heat["Jour"] = pd.to_datetime(cur_for_heat[DATE_COL]).dt.day_name(locale="fr_FR")
        cur_for_heat["total"] = cur_for_heat[selected_products].sum(axis=1)
        heat_agg = cur_for_heat.groupby(["Jour", "Heure"])["total"].sum().reset_index()
        heat_agg.rename(columns={"total": "Quantité (g)"}, inplace=True)

        ordre_jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        lower = heat_agg["Jour"].str.lower()
        if set(ordre_jours).issubset(set(lower.unique())):
            order_map = {j: i for i, j in enumerate(ordre_jours)}
            heat_agg["_order"] = lower.map(order_map)
            day_sort = heat_agg.sort_values("_order")["Jour"].drop_duplicates().tolist()
        else:
            day_sort = heat_agg["Jour"].dropna().unique().tolist()

        heatmap = alt.Chart(heat_agg).mark_rect().encode(
            x=alt.X("Heure:O", title="Heure"),
            y=alt.Y("Jour:N", sort=day_sort, title="Jour"),
            color=alt.Color("Quantité (g):Q", title="Quantité (g)"),
            tooltip=["Jour", "Heure", "Quantité (g)"]
        ).properties(height=260)
        st.altair_chart(heatmap, use_container_width=True)
