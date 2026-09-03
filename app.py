import io
import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURARE PAGINĂ & STILURI VIZUALE
# ==========================================
st.set_page_config(
    page_title="Portal Aliniere Comenzi",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .screen-frame {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        border: 9px solid rgba(14, 165, 233, 0.45);
        box-shadow: inset 0 0 20px rgba(14, 165, 233, 0.2), 0 0 15px rgba(14, 165, 233, 0.3);
        pointer-events: none;
        z-index: 99998;
        box-sizing: border-box;
    }

    .stApp {
        background: linear-gradient(125deg, #f0f9ff 0%, #e0f2fe 50%, #f1f5f9 100%);
        color: #0f172a;
        overflow-x: hidden;
    }

    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-right: 1px solid #cbd5e1;
    }

    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #0369a1;
        margin-bottom: 0.2rem;
        animation: fadeInDown 1s ease-out;
    }

    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.8rem;
        animation: fadeInDown 1.2s ease-out;
    }

    @keyframes fadeInDown {
        0% { opacity: 0; transform: translateY(-20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    .corner-emoji {
        position: fixed;
        font-size: 2.2rem;
        z-index: 99999;
        pointer-events: none;
        user-select: none;
        filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
    }

    .top-left { top: 22px; left: 25px; animation: swingEmoji 3s ease-in-out infinite alternate; }
    .top-right { top: 22px; right: 25px; animation: bounceEmoji 2.5s ease-in-out infinite alternate; }
    .bottom-left { bottom: 22px; left: 25px; animation: floatEmoji 3.5s ease-in-out infinite alternate; }
    .bottom-right { bottom: 22px; right: 25px; animation: pulseEmoji 2s ease-in-out infinite alternate; }

    @keyframes swingEmoji {
        0% { transform: rotate(-15deg) translateY(0); }
        100% { transform: rotate(15deg) translateY(-8px); }
    }

    @keyframes bounceEmoji {
        0% { transform: translateY(0) scale(1); }
        100% { transform: translateY(-12px) scale(1.1); }
    }

    @keyframes floatEmoji {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(6px, -10px) rotate(10deg); }
    }

    @keyframes pulseEmoji {
        0% { transform: scale(1); }
        100% { transform: scale(1.2); }
    }

    .floating-shape-1 {
        position: fixed;
        width: 250px;
        height: 250px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.25) 0%, rgba(255,255,255,0) 70%);
        top: 10%;
        left: 5%;
        border-radius: 50%;
        z-index: 0;
        animation: floatShape 12s ease-in-out infinite alternate;
        pointer-events: none;
    }

    .floating-shape-2 {
        position: fixed;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(129, 140, 248, 0.2) 0%, rgba(255,255,255,0) 70%);
        bottom: 10%;
        right: 5%;
        border-radius: 50%;
        z-index: 0;
        animation: floatShape2 16s ease-in-out infinite alternate;
        pointer-events: none;
    }

    @keyframes floatShape {
        0% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(40px, 30px) scale(1.1); }
        100% { transform: translate(-20px, 50px) scale(0.95); }
    }

    @keyframes floatShape2 {
        0% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(-50px, -40px) scale(1.15); }
        100% { transform: translate(30px, -20px) scale(0.9); }
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(8px);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0284c7, #2563eb);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 1.4rem;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    div.stButton > button:first-child:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 8px 22px rgba(37, 99, 235, 0.45);
    }

    .stDownloadButton button {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 1.4rem;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
        transition: all 0.3s ease;
    }

    .stDownloadButton button:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 8px 22px rgba(16, 185, 129, 0.45);
    }
    </style>

    <div class="screen-frame"></div>
    <div class="corner-emoji top-left">📦</div>
    <div class="corner-emoji top-right">🚀</div>
    <div class="corner-emoji bottom-left">📊</div>
    <div class="corner-emoji bottom-right">✨</div>
    <div class="floating-shape-1"></div>
    <div class="floating-shape-2"></div>
""",
    unsafe_allow_html=True,
)


def gaseste_coloana_material(df):
    """Găsește coloana de Material Number (evită coloana de descriere/denumire)."""
    cols_map = {str(c).strip().lower(): c for c in df.columns}
    for col_lower, col_orig in cols_map.items():
        if not any(x in col_lower for x in ["name", "desc", "text", "denumire"]):
            if col_lower in ["material number", "material", "part number", "part no", "row labels", "cod material"]:
                return col_orig
    for col_lower, col_orig in cols_map.items():
        if not any(x in col_lower for x in ["name", "desc", "text", "denumire"]):
            if any(x in col_lower for x in ["material", "part", "cod"]):
                return col_orig
    return df.columns[0]


def gaseste_coloana(df, posibilitati, default=None):
    """Găsește coloana pe baza unei liste de cuvinte-cheie."""
    cols_map = {str(c).strip().lower(): c for c in df.columns}
    for pos in posibilitati:
        pos_clean = pos.strip().lower()
        if pos_clean in cols_map:
            return cols_map[pos_clean]
    for pos in posibilitati:
        pos_clean = pos.strip().lower()
        for c_lower, c_orig in cols_map.items():
            if pos_clean in c_lower:
                return c_orig
    return default


def preselecteaza_foile(excel_file, depozit_selectat):
    """Detectează și preselectează foile din fișier, potrivind pivotul de tranzit cu depozitul ales."""
    excel = pd.ExcelFile(excel_file)
    nume_foi = excel.sheet_names

    def_fr, def_ro, def_tp = None, None, None
    dep_clean = depozit_selectat.replace("ALL", "").strip().upper()

    for s in nume_foi:
        s_up = s.strip().upper()
        # Căutare foaie specifică de Tranzit (ex: PIVOT T SI P FR01)
        if any(k in s_up for k in ["PIVOT", "T SI P", "T-P", "TRANSIT", "PROGRESS"]):
            if dep_clean and dep_clean in s_up:
                def_tp = s
            elif not def_tp:
                def_tp = s
        elif s_up == "BO FR" or ("FR" in s_up and not def_fr and "PIVOT" not in s_up):
            def_fr = s
        elif s_up == "BO RO" or ("RO" in s_up and not def_ro and "PIVOT" not in s_up):
            def_ro = s

    idx_fr = nume_foi.index(def_fr) if def_fr in nume_foi else 0
    idx_ro = nume_foi.index(def_ro) if def_ro in nume_foi else min(1, len(nume_foi) - 1)
    idx_tp = nume_foi.index(def_tp) if def_tp in nume_foi else min(2, len(nume_foi) - 1)

    return nume_foi, idx_fr, idx_ro, idx_tp


def proceseaza_alinierea(uploaded_file, depozit_selectat, sheet_fr, sheet_ro, sheet_tp):
    franta = pd.read_excel(uploaded_file, sheet_name=sheet_fr)
    romania = pd.read_excel(uploaded_file, sheet_name=sheet_ro)
    transit = pd.read_excel(uploaded_file, sheet_name=sheet_tp)

    franta.columns = franta.columns.astype(str).str.strip()
    romania.columns = romania.columns.astype(str).str.strip()
    transit.columns = transit.columns.astype(str).str.strip()

    col_plant_fr = gaseste_coloana(franta, ["Plant", "Ship", "Depozit"])
    col_plant_ro = gaseste_coloana(romania, ["Ship", "Plant", "Depozit"])

    col_mat_fr = gaseste_coloana_material(franta)
    col_mat_ro = gaseste_coloana_material(romania)
    col_mat_tp = gaseste_coloana_material(transit)

    col_qty_fr = gaseste_coloana(
        franta,
        ["Qty to be Delivered", "Open Qty", "Sum of Qty", "Delivered", "Qty", "Cantitate"],
        default=franta.columns[1],
    )
    col_qty_ro = gaseste_coloana(
        romania,
        ["Open Qty", "Qty to be Delivered", "Sum of Qty", "Qty", "Cantitate"],
        default=romania.columns[1],
    )
    col_qty_tp = gaseste_coloana(
        transit,
        ["Sum of CAN", "CAN", "Qty to be Delivered", "Open Qty", "Sum of Qty", "Qty", "Cantitate"],
        default=transit.columns[1] if len(transit.columns) > 1 else transit.columns[0],
    )

    depozit_filtru = depozit_selectat.strip().upper()
    este_toate = "ALL" in depozit_filtru

    # Izolare strictă pe depozitul ales
    if col_plant_fr:
        franta["_PLANT_"] = franta[col_plant_fr].astype(str).str.strip().str.upper()
        if not este_toate:
            franta = franta[franta["_PLANT_"] == depozit_filtru].copy()
    else:
        franta["_PLANT_"] = depozit_filtru if not este_toate else "N/A"

    if col_plant_ro:
        romania["_PLANT_"] = romania[col_plant_ro].astype(str).str.strip().str.upper()
        if not este_toate:
            romania = romania[romania["_PLANT_"] == depozit_filtru].copy()
    else:
        romania["_PLANT_"] = depozit_filtru if not este_toate else "N/A"

    # Conversie cantități
    franta[col_qty_fr] = pd.to_numeric(franta[col_qty_fr], errors="coerce").fillna(0)
    romania[col_qty_ro] = pd.to_numeric(romania[col_qty_ro], errors="coerce").fillna(0)
    transit[col_qty_tp] = pd.to_numeric(transit[col_qty_tp], errors="coerce").fillna(0)

    transit = transit[
        ~transit[col_mat_tp].astype(str).str.lower().isin(["total result", "grand total", "nan", ""])
    ].copy()

    # Agregare date pe depozit
    pivot_fr = (
        franta.groupby([col_mat_fr, "_PLANT_"], as_index=False)[col_qty_fr]
        .sum()
        .rename(columns={col_mat_fr: "Row Labels", col_qty_fr: "BO FR"})
    )
    pivot_fr["Row Labels"] = pivot_fr["Row Labels"].astype(str).str.strip()

    pivot_ro = (
        romania.groupby([col_mat_ro, "_PLANT_"], as_index=False)[col_qty_ro]
        .sum()
        .rename(columns={col_mat_ro: "Row Labels", col_qty_ro: "BO RO"})
    )
    pivot_ro["Row Labels"] = pivot_ro["Row Labels"].astype(str).str.strip()

    pivot_tp = (
        transit.groupby(col_mat_tp, as_index=False)[col_qty_tp]
        .sum()
        .rename(columns={col_mat_tp: "Row Labels", col_qty_tp: "Transit & Progress"})
    )
    pivot_tp["Row Labels"] = pivot_tp["Row Labels"].astype(str).str.strip()

    # Îmbinare
    rezultat = pd.merge(pivot_fr, pivot_ro, on=["Row Labels", "_PLANT_"], how="outer").fillna(0)
    rezultat = pd.merge(rezultat, pivot_tp, on="Row Labels", how="left").fillna(0)
    rezultat = rezultat.rename(columns={"_PLANT_": "Plant / Ship"})

    # Formule: DIFF, Status, Action
    rezultat["DIFF"] = rezultat["BO RO"] + rezultat["Transit & Progress"] - rezultat["BO FR"]
    rezultat["COMM - OK/NOK"] = rezultat["DIFF"].apply(lambda d: "OK" if round(d) == 0 else "NOK")

    def stabileste_actiune(diff):
        val = int(round(diff))
        if val < 0:
            return f"DELETE {abs(val)}"
        elif val > 0:
            return f"ADD {val}"
        return "OK"

    rezultat["ACTION"] = rezultat["DIFF"].apply(stabileste_actiune)

    coloane_finale = [
        "Plant / Ship",
        "Row Labels",
        "BO FR",
        "BO RO",
        "Transit & Progress",
        "DIFF",
        "COMM - OK/NOK",
        "ACTION",
    ]
    rezultat = rezultat[coloane_finale].sort_values(by=["Row Labels", "Plant / Ship"], ascending=True)

    output_buffer = io.BytesIO()
    with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
        pivot_fr.to_excel(writer, sheet_name="Pivot_BO_FR", index=False)
        pivot_ro.to_excel(writer, sheet_name="Pivot_BO_RO", index=False)
        pivot_tp.to_excel(writer, sheet_name="Pivot_TP", index=False)
        rezultat.to_excel(writer, sheet_name="Rezultate", index=False)

    return output_buffer.getvalue(), rezultat


# ==========================================
# MENIU LATERAL
# ==========================================
with st.sidebar:
    st.header("📌 Ghid Utilizare")
    st.markdown(
        """
    1. **Alege depozitul** dorit.
    2. **Încarcă fișierul** Excel cu date brute.
    3. **Selectează foile** (Franța, România și foaia de pivot de tranzit dedicată depozitului ales).
    4. Apasă **Generează Raportul**.
    
    ---
    **Reguli de calcul:**  
    `DIFF = (BO RO + T&P) - BO FR`
    - `DIFF < 0` ➔ **DELETE**
    - `DIFF > 0` ➔ **ADD**
    - `DIFF = 0` ➔ **OK**
    """
    )

# ==========================================
# CORPUL APLICAȚIEI
# ==========================================
st.markdown(
    '<div class="main-title">📦 Aliniere Comenzi & Reconciliere Stoc</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Reconciliere automată pe depozite și gestionare dublă localizare</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Încarcă fișierul Excel (.xlsx):", type=["xlsx"]
    )

with col2:
    plant = st.selectbox(
        "Selectează Depozitul de reconciliat:", ["FR01", "FR02", "FR03", "FR06", "ALL (Toate Depozitele)"]
    )

if uploaded_file:
    try:
        lista_foi, idx_fr, idx_ro, idx_tp = preselecteaza_foile(uploaded_file, plant)

        st.subheader("📑 Confirmare Foi Corespunzătoare:")
        f_col1, f_col2, f_col3 = st.columns(3)

        with f_col1:
            sheet_fr = st.selectbox("Foaie Franța (BO FR):", lista_foi, index=idx_fr)
        with f_col2:
            sheet_ro = st.selectbox("Foaie România (BO RO):", lista_foi, index=idx_ro)
        with f_col3:
            label_tp = f"Foaie Tranzit ({plant}):" if "ALL" not in plant else "Foaie Tranzit:"
            sheet_tp = st.selectbox(label_tp, lista_foi, index=idx_tp)

        st.write("")
        if st.button("🚀 Generează Raportul", use_container_width=True):
            with st.spinner("Se prelucrează datele și formulele..."):
                val_depozit = "ALL" if "ALL" in plant else plant
                excel_data, df_rezultat = proceseaza_alinierea(
                    uploaded_file, val_depozit, sheet_fr, sheet_ro, sheet_tp
                )

                st.balloons()

                st.success(
                    f"✨ Raportul pentru depozitul **{plant}** a fost calculat corect!"
                )

                total_articole = len(df_rezultat)
                total_delete = (
                    df_rezultat["ACTION"].str.startswith("DELETE").sum()
                )
                total_add = df_rezultat["ACTION"].str.startswith("ADD").sum()
                total_ok = (df_rezultat["ACTION"] == "OK").sum()

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Articole", total_articole)
                m2.metric("Acțiuni ADD", total_add)
                m3.metric("Acțiuni DELETE", total_delete)
                m4.metric("Status OK", total_ok)

                st.subheader("📋 Previzualizare Rezultate")
                st.dataframe(df_rezultat, use_container_width=True, height=400)

                nume_descarcare = f"Rezultat_Aliniere_{val_depozit}.xlsx"
                st.download_button(
                    label="📥 Descarcă Raportul Excel Final",
                    data=excel_data,
                    file_name=nume_descarcare,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
    except Exception as e:
        st.error(f"❌ A apărut o eroare la procesare: {e}")
