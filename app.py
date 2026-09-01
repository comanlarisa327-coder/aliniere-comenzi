import io
import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURARE PAGINĂ & STILURI CU ANIMAȚII
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
    /* Culoare de fundal deschisă (Pastel Cald & Gradient) */
    .stApp {
        background: linear-gradient(125deg, #f0f9ff 0%, #e0f2fe 50%, #f1f5f9 100%);
        color: #0f172a;
        overflow-x: hidden;
    }

    /* Meniu Lateral */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-right: 1px solid #cbd5e1;
    }

    /* Animație pentru Titlu (Fade In & Slide Down) */
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
        0% {
            opacity: 0;
            transform: translateY(-20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Animație continuă cu sfere plutitoare în background */
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

    /* Carduri Metrici cu efect de Hover */
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

    /* Buton Principal cu Animație Pulse & Glow */
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

    /* Buton Descărcare Excel */
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

    <!-- Elemente animate de fundal -->
    <div class="floating-shape-1"></div>
    <div class="floating-shape-2"></div>
""",
    unsafe_allow_html=True,
)


def gaseste_coloana(df, posibilitati, default=None):
    """Găsește numele corect al coloanei chiar dacă diferă spațiile sau majusculele."""
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


def proceseaza_alinierea(uploaded_file, depozit_selectat):
    excel = pd.ExcelFile(uploaded_file)
    nume_foi = excel.sheet_names

    sheet_fr = next((s for s in nume_foi if "fr" in s.lower()), None)
    sheet_ro = next((s for s in nume_foi if "ro" in s.lower()), None)
    sheet_tp = next(
        (
            s
            for s in nume_foi
            if "t+p" in s.lower()
            or "transit" in s.lower()
            or "progress" in s.lower()
        ),
        None,
    )

    if not sheet_fr or not sheet_ro or not sheet_tp:
        raise ValueError(
            f"Nu s-au găsit toate foile necesare în fișier. Foi existente: {nume_foi}"
        )

    franta = pd.read_excel(uploaded_file, sheet_name=sheet_fr)
    romania = pd.read_excel(uploaded_file, sheet_name=sheet_ro)
    transit = pd.read_excel(uploaded_file, sheet_name=sheet_tp)

    franta.columns = franta.columns.astype(str).str.strip()
    romania.columns = romania.columns.astype(str).str.strip()
    transit.columns = transit.columns.astype(str).str.strip()

    col_plant_fr = gaseste_coloana(franta, ["Plant", "Depozit"])
    col_plant_ro = gaseste_coloana(romania, ["Plant", "Depozit"])
    col_plant_tp = gaseste_coloana(transit, ["Plant", "Depozit"])

    col_mat_fr = gaseste_coloana(
        franta,
        ["Material Number", "Material", "Row Labels", "Cod Material"],
        default=franta.columns[0],
    )
    col_mat_ro = gaseste_coloana(
        romania,
        ["Material Number", "Material", "Row Labels", "Cod Material"],
        default=romania.columns[0],
    )
    col_mat_tp = gaseste_coloana(
        transit,
        ["Material Number", "Material", "Row Labels", "Cod Material"],
        default=transit.columns[0],
    )

    col_qty_fr = gaseste_coloana(
        franta,
        ["Qty to be Delivered", "Open Qty", "Sum of Qty", "Qty", "Cantitate"],
        default=franta.columns[1],
    )
    col_qty_ro = gaseste_coloana(
        romania,
        ["Open Qty", "Qty to be Delivered", "Sum of Qty", "Qty", "Cantitate"],
        default=romania.columns[1],
    )
    col_qty_tp = gaseste_coloana(
        transit,
        ["Qty to be Delivered", "Open Qty", "Sum of Qty", "Qty", "Cantitate"],
        default=transit.columns[1] if len(transit.columns) > 1 else transit.columns[0],
    )

    if col_plant_fr:
        franta = franta[
            franta[col_plant_fr].astype(str).str.strip().str.upper()
            == depozit_selectat
        ].copy()
    if col_plant_ro:
        romania = romania[
            romania[col_plant_ro].astype(str).str.strip().str.upper()
            == depozit_selectat
        ].copy()
    if col_plant_tp:
        transit = transit[
            transit[col_plant_tp].astype(str).str.strip().str.upper()
            == depozit_selectat
        ].copy()

    franta[col_qty_fr] = pd.to_numeric(
        franta[col_qty_fr], errors="coerce"
    ).fillna(0)
    romania[col_qty_ro] = pd.to_numeric(
        romania[col_qty_ro], errors="coerce"
    ).fillna(0)
    transit[col_qty_tp] = pd.to_numeric(
        transit[col_qty_tp], errors="coerce"
    ).fillna(0)

    # 1. Pivoturi
    pivot_fr = pd.pivot_table(
        franta, index=col_mat_fr, values=col_qty_fr, aggfunc="sum"
    ).reset_index()
    pivot_fr.columns = ["Row Labels", "BO FR"]
    pivot_fr["Row Labels"] = pivot_fr["Row Labels"].astype(str).str.strip()

    pivot_ro = pd.pivot_table(
        romania, index=col_mat_ro, values=col_qty_ro, aggfunc="sum"
    ).reset_index()
    pivot_ro.columns = ["Row Labels", "BO RO"]
    pivot_ro["Row Labels"] = pivot_ro["Row Labels"].astype(str).str.strip()

    pivot_tp = pd.pivot_table(
        transit, index=col_mat_tp, values=col_qty_tp, aggfunc="sum"
    ).reset_index()
    pivot_tp.columns = ["Row Labels", "Transit & Progress"]
    pivot_tp["Row Labels"] = pivot_tp["Row Labels"].astype(str).str.strip()

    # 2. VLOOKUP Merge
    row_labels = (
        pd.concat(
            [
                pivot_fr[["Row Labels"]],
                pivot_ro[["Row Labels"]],
                pivot_tp[["Row Labels"]],
            ]
        )
        .drop_duplicates()
        .reset_index(drop=True)
    )

    rezultat = (
        row_labels.merge(pivot_fr, on="Row Labels", how="left")
        .merge(pivot_ro, on="Row Labels", how="left")
        .merge(pivot_tp, on="Row Labels", how="left")
    ).fillna(0)

    # 3. Calcule: DIFF, Status, Action
    rezultat["DIFF"] = (
        rezultat["BO RO"]
        + rezultat["Transit & Progress"]
        - rezultat["BO FR"]
    )
    rezultat["COMM - OK/NOK"] = rezultat["DIFF"].apply(
        lambda d: "OK" if d == 0 else "NOK"
    )

    def stabileste_actiune(diff):
        val = int(round(diff))
        if diff < 0:
            return f"DELETE {abs(val)}"
        elif val > 0:
            return f"ADD {val}"
        return "OK"

    rezultat["ACTION"] = rezultat["DIFF"].apply(stabileste_actiune)
    rezultat = rezultat.sort_values(by="DIFF", ascending=True)

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
    1. **Încarcă fișierul** Excel cu date brute.
    2. **Alege depozitul** din meniu.
    3. Apasă butonul **Generează Raportul**.
    4. Descarcă fișierul calculat.
    
    ---
    **Reguli de reconciliere:**  
    `DIFF = (BO RO + T&P) - BO FR`
    - `DIFF < 0` ➔ **DELETE**
    - `DIFF > 0` ➔ **ADD**
    - `DIFF = 0` ➔ **OK**
    """
    )

# ==========================================
# ZONA PRINCIPALĂ
# ==========================================
st.markdown(
    '<div class="main-title">📦 Aliniere Comenzi & Reconciliere Stoc</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Sistem automat pentru calculul comenzilor BO Franța, BO România și Tranzit</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Încarcă fișierul Excel (.xlsx):", type=["xlsx"]
    )

with col2:
    plant = st.selectbox(
        "Selectează Depozitul (Plant):", ["FR01", "FR02", "FR03", "FR06"]
    )

st.write("")

if uploaded_file:
    if st.button("🚀 Generează Raportul", use_container_width=True):
        with st.spinner("Se prelucrează datele și formulele..."):
            try:
                excel_data, df_rezultat = proceseaza_alinierea(
                    uploaded_file, plant
                )

                # Animație dublă de succes pe ecran
                st.balloons()

                st.success(
                    f"✨ Raportul pentru depozitul **{plant}** a fost generat cu succes!"
                )

                # Carduri statistice animate
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

                # Tabel rezultate
                st.subheader("📋 Previzualizare Rezultate")
                st.dataframe(df_rezultat, use_container_width=True, height=400)

                # Buton descărcare
                st.download_button(
                    label="📥 Descarcă Raportul Excel Final",
                    data=excel_data,
                    file_name=f"Rezultat_Aliniere_{plant}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"❌ A apărut o eroare la procesare: {e}")
