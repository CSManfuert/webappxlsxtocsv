import streamlit as st
import pandas as pd
import io

# Configuración de la página
st.set_page_config(page_title="Excel a CSV para RAG", layout="centered")
st.title("📄 Convertir Excel a CSV")
st.markdown("""
Sube tu archivo Excel con las columnas **'Nombre y apellido'** (formato: `Apellido, Nombre`) y **'DNI'`.  
Generaremos un CSV con el orden:  
`nombre, apellido, dni, email, telefono`  
La columna **telefono** se crea vacía, lista para que agregues números después.  
Si luego se completa, puedes volver a usar esta app para agregar el **"1"** al inicio.
""")

# Subida del archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx o .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file)

        st.success("✅ Archivo Excel cargado correctamente.")
        st.write("### Vista previa del archivo original:")
        st.dataframe(df.head())

        # Verificar columnas necesarias
        if 'Nombre y apellido' not in df.columns:
            st.error("❌ No se encontró la columna 'Nombre y apellido'")
            st.stop()
        if 'DNI' not in df.columns:
            st.error("❌ No se encontró la columna 'DNI'")
            st.stop()

        # Seleccionar y renombrar
        df = df[['Nombre y apellido', 'DNI']].copy()
        df = df.rename(columns={'DNI': 'dni'})

        # Separar "Apellido, Nombre" → apellido, nombre
        split = df['Nombre y apellido'].astype(str).str.strip().str.split(',', n=1, expand=True)
        df['apellido'] = split[0].fillna('').str.strip()
        df['nombre'] = split[1].fillna('').str.strip()  # Puede ser vacío si no hay coma

        # Limpiar DNI
        df['dni'] = pd.to_numeric(df['dni'], errors='coerce').fillna(0).astype(int).astype(str)

        # Agregar columnas vacías
        df['email'] = ''
        # En lugar de: df['telefono'] = ''
        # Usa esto si la columna ya existe:
        if 'telefono' in df.columns:
            df['telefono'] = (
                df['telefono'].astype(str).str.replace(r'\D', '', regex=True)
                .apply(lambda x: f"1{x}" if x and x != 'nan' and not x.startswith('1') else x)
            )
        else:
            df['telefono'] = ''

        # Reordenar columnas
        output_df = df[['nombre', 'apellido', 'dni', 'email', 'telefono']].copy()

        # Eliminar filas vacías
        output_df.dropna(subset=['nombre', 'apellido', 'dni'], how='all', inplace=True)

        # Mostrar vista previa
        st.write("### Vista previa del CSV generado:")
        st.dataframe(output_df.head(10))

        # Preparar CSV
        csv_buffer = io.StringIO()
        output_df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_data = csv_buffer.getvalue()

        # Botón de descarga
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv_data,
            file_name="datos_procesados.csv",
            mime="text/csv"
        )

        st.info("✅ El CSV se generó con formato listo para usar.")
        st.info("💡 Puedes completar `email` y `telefono` manualmente o con otra herramienta.")
        st.info("🔄 Si luego agregas números de teléfono, vuelve a subir el CSV y este sistema les agregará el '1' automáticamente.")

    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")
