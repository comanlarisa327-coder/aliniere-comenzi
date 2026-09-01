import io
import pandas as pd
import streamlit as st


def gaseste_coloana(df, posibilitati, default=None):
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

    # Pivot Tables
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

    # Merge / VLOOKUP
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

    # Calcule
    rezultat["DIFF"] = (
        rezultat["BO RO"]
        + rezultat["Transit & Progress"]
        - rezultat["BO FR"]
    )
    rezultat["COMM - OK/NOK"] = rezultat["DIFF"].apply(
        lambda d: "OK" if d == 0 else "NOK"
    )

    # Logica inversată: < 0 este DELETE, > 0 este ADD
    def stabileste_actiune(diff):
        val = int(round(diff))
        if diff < 0:
            return f"DELETE {abs(val)}"
        elif val > 0:
            return f"ADD {val}"
        return "OK"

    rezultat["ACTION"] = rezultat["DIFF"].apply(stabileste_actiune)
    rezultat = rezultat.sort_values(by="DIFF", ascending=True)

    # Salvare în memorie
    output_buffer = io.BytesIO()
    with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
        pivot_fr.to_excel(writer, sheet_name="Pivot_BO_FR", index=False)
        pivot_ro.to_excel(writer, sheet_name="Pivot_BO_RO", index=False)
        pivot_tp.to_excel(writer, sheet_name="Pivot_TP", index=False)
        rezultat.to_excel(writer, sheet_name="Rezultate", index=False)

    return output_buffer.getvalue(), rezultat


# ==========================================
# INTERFAȚĂ WEB (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Aliniere Comenzi", layout="wide")
st.title("📊 Aplicație Aliniere Comenzi FR / RO / Transit")

uploaded_file = st.file_uploader(
    "1. Încarcă fișierul Excel cu date brute (.xlsx)", type=["xlsx"]
)

plant = st.selectbox(
    "2. Alege depozitul (Plant):", ["FR01", "FR02", "FR03", "FR06"]
)

if uploaded_file and st.button("🚀 Generează Raportul"):
    with st.spinner("Se procesează datele..."):
        try:
            excel_data, df_rezultat = proceseaza_alinierea(uploaded_file, plant)
            st.success("Raportul a fost generat cu succes!")

            st.subheader("Previzualizare Rezultate:")
            st.dataframe(df_rezultat, use_container_width=True)

            st.download_button(
                label="📥 Descarcă Raportul Excel",
                data=excel_data,
                file_name=f"Rezultat_Aliniere_{plant}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception as e:
            st.error(f"Eroare la procesare: {e}")
