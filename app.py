import io
import numpy as np
import pandas as pd
import streamlit as st

# ==============================================================================
# CONFIGURARE PAGINĂ STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Reconciliere Comenzi (BO FR / BO RO / Transit)",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Reconciliere & Aliniere Comenzi")
st.markdown(
    "Aplicație automată pentru reconcilierea comenzilor pe bază de **Material Number** și **Plant/Ship** (gestionează dubla localizare)."
)


# ==============================================================================
# 1. FUNCȚII AUXILIARE DE DETECȚIE ȘI PROCESARE
# ==============================================================================
def detect_sheet_names(sheet_list):
    """Detectează automat foile după denumire."""
    name_fr, name_ro, name_tp = None, None, None
    for s in sheet_list:
        s_up = str(s).upper().strip()
        if (
            "PIVOT" in s_up
            or "T-P" in s_up
            or "TRANSIT" in s_up
            or "PROGRESS" in s_up
        ):
            name_tp = s
        elif s_up == "BO FR" or ("FR" in s_up and not name_fr):
            name_fr = s
        elif s_up == "BO RO" or ("RO" in s_up and not name_ro):
            name_ro = s
    return name_fr, name_ro, name_tp


def detect_columns(df):
    """Identifică coloana de cod piesă, depozit și cantitate."""
    cols = {str(c).strip(): c for c in df.columns}
    col_mat, col_plant, col_qty = None, None, None

    # Cod piesă (exclude explicit denumirile/descrierile)
    for name, orig in cols.items():
        low = name.lower()
        if not any(x in low for x in ["name", "desc", "text", "denumire"]):
            if low in [
                "material number",
                "material",
                "part number",
                "part no",
                "row labels",
            ]:
                col_mat = orig
                break
    if not col_mat:
        for name, orig in cols.items():
            low = name.lower()
            if not any(x in low for x in ["name", "desc", "text", "denumire"]):
                if any(x in low for x in ["material", "part", "cod"]):
                    col_mat = orig
                    break
    if not col_mat:
        col_mat = df.columns[0]

    # Plant / Ship
    for name, orig in cols.items():
        low = name.lower()
        if low in ["plant", "ship", "depozit"]:
            col_plant = orig
            break

    # Cantitate
    for name, orig in cols.items():
        low = name.lower()
        if any(
            x in low
            for x in ["open qty", "sum of", "delivered", "qty", "cantitate"]
        ):
            col_qty = orig
            break
    if not col_qty and len(df.columns) > 1:
        col_qty = df.columns[1]

    return col_mat, col_plant, col_qty


def reconcile_orders(
    df_fr_raw, df_ro_raw, df_tp_raw, selected_plant: str = "ALL"
):
    """Calculează reconcilierea comenzilor pe cheia compusă Material | Plant."""
    # BO FR
    c_mat, c_plant, c_qty = detect_columns(df_fr_raw)
    df_fr = df_fr_raw[[c_mat, c_qty]].copy()
    df_fr.columns = ["Material", "BO FR"]
    df_fr["Material"] = df_fr["Material"].astype(str).str.strip()
    df_fr["BO FR"] = pd.to_numeric(df_fr["BO FR"], errors="coerce").fillna(0)

    if c_plant and c_plant in df_fr_raw.columns:
        df_fr["Plant"] = (
            df_fr_raw[c_plant].astype(str).str.strip().str.upper()
        )
    else:
        df_fr["Plant"] = "N/A"

    # BO RO
    c_mat, c_plant, c_qty = detect_columns(df_ro_raw)
    df_ro = df_ro_raw[[c_mat, c_qty]].copy()
    df_ro.columns = ["Material", "BO RO"]
    df_ro["Material"] = df_ro["Material"].astype(str).str.strip()
    df_ro["BO RO"] = pd.to_numeric(df_ro["BO RO"], errors="coerce").fillna(0)

    if c_plant and c_plant in df_ro_raw.columns:
        df_ro["Plant"] = (
            df_ro_raw[c_plant].astype(str).str.strip().str.upper()
        )
    else:
        df_ro["Plant"] = "N/A"

    # PIVOT T-P
    c_mat, _, c_qty = detect_columns(df_tp_raw)
    df_tp = df_tp_raw[[c_mat, c_qty]].copy()
    df_tp.columns = ["Material", "Transit & Progress"]
    df_tp["Material"] = df_tp["Material"].astype(str).str.strip()
    df_tp["Transit & Progress"] = pd.to_numeric(
        df_tp["Transit & Progress"], errors="coerce"
    ).fillna(0)
    df_tp = df_tp[
        ~df_tp["Material"].str.lower().isin(["total result", "grand total", ""])
    ]
    df_tp_agg = df_tp.groupby("Material", as_index=False)[
        "Transit & Progress"
    ].sum()

    # Filtrare după depozit
    selected_plant = selected_plant.strip().upper()
    if selected_plant and selected_plant != "ALL":
        df_fr = df_fr[df_fr["Plant"] == selected_plant]
        df_ro = df_ro[df_ro["Plant"] == selected_plant]

    # Agregare pe cheia compusă (Material + Plant)
    df_fr_agg = df_fr.groupby(["Material", "Plant"], as_index=False)[
        "BO FR"
    ].sum()
    df_ro_agg = df_ro.groupby(["Material", "Plant"], as_index=False)[
        "BO RO"
    ].sum()

    # Îmbinare date
    merged = pd.merge(
        df_fr_agg, df_ro_agg, on=["Material", "Plant"], how="outer"
    )
    merged["BO FR"] = merged["BO FR"].fillna(0)
    merged["BO RO"] = merged["BO RO"].fillna(0)

    # Adăugare Tranzit (pe cod piesă)
    merged = pd.merge(merged, df_tp_agg, on="Material", how="left")
    merged["Transit & Progress"] = merged["Transit & Progress"].fillna(0)

    # Calcul DIFF și stabilire ACTION
    merged["DIFF"] = (
        merged["BO RO"] + merged["Transit & Progress"] - merged["BO FR"]
    )
    merged["COMM - OK/NOK"] = np.where(merged["DIFF"] == 0, "OK", "NOK")

    def format_action(diff):
        val = round(diff)
        if val == 0:
            return "OK"
        elif val < 0:
            return f"DELETE {abs(val)}"
        else:
            return f"ADD {val}"

    merged["ACTION"] = merged["DIFF"].apply(format_action)

    merged = merged.rename(
        columns={"Plant": "Plant / Ship", "Material": "Material Number"}
    )
    cols_order = [
        "Plant / Ship",
        "Material Number",
        "BO FR",
        "BO RO",
        "Transit & Progress",
        "DIFF",
        "COMM - OK/NOK",
        "ACTION",
    ]
    return merged[cols_order].sort_values(
        by=["Material Number", "Plant / Ship"]
    )


# ==============================================================================
# 2. INTERFAȚĂ UTILIZATOR & ÎNCĂRCARE FIȘIER
# ==============================================================================
uploaded_file = st.file_uploader(
    "Încarcă fișierul Excel cu date brute (.xlsx)", type=["xlsx", "xls", "xlsm"]
)

if uploaded_file:
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        all_sheets = excel_file.sheet_names

        st.subheader("⚙️ Configurare Foi și Depozit")
        col1, col2, col3 = st.columns(3)

        auto_fr, auto_ro, auto_tp = detect_sheet_names(all_sheets)

        with col1:
            idx_fr = all_sheets.index(auto_fr) if auto_fr in all_sheets else 0
            sheet_fr = st.selectbox(
                "Foaie Franța (BO FR)", all_sheets, index=idx_fr
            )

        with col2:
            idx_ro = (
                all_sheets.index(auto_ro)
                if auto_ro in all_sheets
                else min(1, len(all_sheets) - 1)
            )
            sheet_ro = st.selectbox(
                "Foaie România (BO RO)", all_sheets, index=idx_ro
            )

        with col3:
            idx_tp = (
                all_sheets.index(auto_tp)
                if auto_tp in all_sheets
                else min(2, len(all_sheets) - 1)
            )
            sheet_tp = st.selectbox(
                "Foaie Transit (PIVOT T-P)", all_sheets, index=idx_tp
            )

        # Citire preliminară pentru determinarea depozitelor existente
        df_ro_preview = pd.read_excel(excel_file, sheet_name=sheet_ro, nrows=500)
        _, c_p, _ = detect_columns(df_ro_preview)

        available_plants = ["ALL"]
        if c_p and c_p in df_ro_preview.columns:
            plants_found = sorted(
                [
                    str(x).strip().upper()
                    for x in df_ro_preview[c_p].dropna().unique()
                    if str(x).strip()
                ]
            )
            available_plants.extend(plants_found)

        plant_choice = st.selectbox(
            "Selectează Depozit / Plant (sau ALL pentru toate)",
            available_plants,
            index=0,
        )

        if st.button("🚀 Generează Aliniere", type="primary"):
            with st.spinner("Se procesează fișierul..."):
                df_fr_raw = pd.read_excel(excel_file, sheet_name=sheet_fr)
                df_ro_raw = pd.read_excel(excel_file, sheet_name=sheet_ro)
                df_tp_raw = pd.read_excel(excel_file, sheet_name=sheet_tp)

                df_result = reconcile_orders(
                    df_fr_raw, df_ro_raw, df_tp_raw, selected_plant=plant_choice
                )

                st.session_state["result_df"] = df_result

    except Exception as e:
        st.error(f"Eroare la citirea fișierului: {e}")

# ==============================================================================
# 3. AFIȘARE REZULTATE ȘI EXPORT EXCEL
# ==============================================================================
if "result_df" in st.session_state:
    df_res = st.session_state["result_df"]

    st.divider()
    st.subheader(f"📊 Rezultate Reconciliere ({len(df_res)} rânduri)")

    # Metrici rapide
    m1, m2, m3 = st.columns(3)
    total_ok = (df_res["COMM - OK/NOK"] == "OK").sum()
    total_nok = (df_res["COMM - OK/NOK"] == "NOK").sum()
    m1.metric("Total Referințe / Locații", len(df_res))
    m2.metric("Aliniate (OK)", total_ok)
    m3.metric("Discrepanțe (NOK)", total_nok)

    st.dataframe(df_res, use_container_width=True)

    # Generare fișier Excel pentru descărcare
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_res.to_excel(writer, sheet_name="Rezultate_Aliniere", index=False)
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Descarcă Raportul Excel",
        data=excel_data,
        file_name="Rezultate_Aliniere.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
