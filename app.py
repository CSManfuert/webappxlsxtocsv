import streamlit as st
import pandas as pd
import io

# Configuración de la página
st.set_page_config(page_title="Excel a CSV para Fotógrafos", layout="centered")
st.title("📸 Convertir Excel a CSV para Fotógrafos")
st.markdown("""
Sube tu archivo Excel con las columnas **'Nombre y apellido'** (formato: `Apellido, Nombre`) y **'DNI'`.  
Opcionalmente, puede incluir **'Teléfono'**.  
Generaremos un CSV con el orden:  
`nombre, apellido, dni, email, telefono`  
➡️ Si hay un número de teléfono, se le agregará un **"1" al inicio** automáticamente.
""")

# Subida del archivo
uploaded_file = st.file_uploader("📂 Sube tu archivo Excel (.xlsx o .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file)

        st.success("✅ Archivo Excel cargado correctamente.")
        st.write("### Vista previa del archivo original:")
        st.dataframe(df.head())

        # === Validación de columnas requeridas ===
        if 'Nombre y apellido' not in df.columns:
            st.error("❌ No se encontró la columna 'Nombre y apellido'")
            st.stop()
        if 'DNI' not in df.columns:
            st.error("❌ No se encontró la columna 'DNI'")
            st.stop()

        # Renombrar
        df = df.rename(columns={'DNI': 'dni'})

        # === Separar "Apellido, Nombre" → apellido, nombre ===
        split = df['Nombre y apellido'].astype(str).str.strip().str.split(',', n=1, expand=True)
        df['apellido'] = split[0].fillna('').str.strip()
        df['nombre'] = split[1].fillna('').str.strip()

        # === Limpiar DNI ===
        df['dni'] = pd.to_numeric(df['dni'], errors='coerce').fillna(0).astype(int).astype(str)

        # === Manejo de EMAIL ===
        if 'Email' in df.columns:
            df['email'] = df['Email'].astype(str).str.strip().str.lower()
        elif 'email' in df.columns:
            df['email'] = df['email'].astype(str).str.strip().str.lower()
        else:
            df['email'] = ''

        # === Manejo de TELÉFONO (aquí va la automatización del "1") ===
        telefono_col = None
        for col in df.columns:
            if 'telefono' in col.lower() or 'teléfono' in col.lower() or 'celular' in col.lower() or 'phone' in col.lower():
                telefono_col = col
                break

        if telefono_col:
            # Limpiar y agregar "1" al inicio si no lo tiene
            df['telefono'] = (
                df[telefono_col]
                .astype(str)
                .str.replace(r'\\D', '', regex=True)  # Elimina todo no numérico
                .str.lstrip('0')  # Elimina ceros iniciales
                .apply(lambda x: f"1{x}" if x and x != 'nan' and not x.startswith('1') else x)
            )
        else:
            df['telefono'] = ''  # Si no existe, crear vacío

        # === Reordenar y limpiar ===
        output_df = df[['nombre', 'apellido', 'dni', 'email', 'telefono']].copy()
        output_df.dropna(subset=['nombre', 'apellido', 'dni'], how='all', inplace=True)

        # Mostrar vista previa
        st.write("### ✅ Vista previa del CSV generado:")
        st.dataframe(output_df.head(10))

        # Preparar CSV
        csv_buffer = io.StringIO()
        output_df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_data = csv_buffer.getvalue()

        # Botón de descarga
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv_data,
            file_name="datos_fotografo.csv",
            mime="text/csv"
        )

        st.info("📌 El CSV se generó con formato correcto.")
        st.info("📞 Si había números de teléfono, se les agregó un '1' al inicio automáticamente.")
        st.info("💡 Puedes completar `email` y `telefono` más tarde si es necesario.")

    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar el archivo: {e}")
        st.exception(e)
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")
