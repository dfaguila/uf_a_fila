import streamlit as st
import pandas as pd

# -----------------------------
# Función de transformación UF
# -----------------------------
def transformar_uf(df, anio):
    # Asegurar nombre columna día
    df = df.rename(columns={df.columns[0]: "Dia"})
    
    # Pasar de ancho a largo
    df_melt = df.melt(id_vars=["Dia"], var_name="Mes", value_name="UF")
    
    # Eliminar vacíos
    df_melt = df_melt.dropna()
    
    # Mapeo meses abreviados
    meses = {
        "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Ago": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12
    }
    
    df_melt["Mes_num"] = df_melt["Mes"].map(meses)
    
    # Crear fecha
    df_melt["Fecha"] = pd.to_datetime(
        dict(year=anio, month=df_melt["Mes_num"], day=df_melt["Dia"]),
        errors="coerce"
    )
    
    # Limpiar fechas inválidas
    df_melt = df_melt.dropna(subset=["Fecha"])
    
    # Limpiar formato UF (ej: 38.419,17 → 38419.17)
    df_melt["UF"] = (
        df_melt["UF"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    
    # Resultado final
    df_final = df_melt[["Fecha", "UF"]].copy()
    df_final["Fecha"] = df_final["Fecha"].dt.strftime("%d-%m-%Y")
    
    return df_final


# -----------------------------
# Interfaz Streamlit
# -----------------------------
st.set_page_config(page_title="Conversor UF SII", layout="wide")

st.title("📊 Conversor UF (Formato SII → Serie diaria)")
st.write("Convierte matrices de UF del SII (meses en columnas, días en filas) a formato tabla.")

archivo = st.file_uploader("Sube archivo (CSV o Excel)", type=["csv", "xlsx"])

anio = st.number_input("Año de la matriz", min_value=2000, max_value=2100, value=2025)

if archivo:
    try:
        if archivo.name.endswith(".csv"):
            df = pd.read_csv(archivo, sep=";", encoding="utf-8")
        else:
            df = pd.read_excel(archivo)

        # LIMPIEZA CLAVE
        df.columns = df.columns.str.strip()

        st.subheader("🔍 Vista original")
        st.dataframe(df.head(10), use_container_width=True)

        df_final = transformar_uf(df, anio)

        st.subheader("✅ Resultado transformado")
        st.dataframe(df_final, use_container_width=True)

        csv = df_final.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Descargar CSV",
            csv,
            f"UF_{anio}_transformada.csv",
            "text/csv"
        )

        st.success(f"Conversión completada: {len(df_final)} registros generados")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
