import streamlit as st
import pandas as pd

st.title("Comparador de Archivos Excel")

# Cargar los archivos Excel

def page1():
    uploaded_file_1 = st.file_uploader("Arrastra el primer archivo Excel aquí", type="xlsx")
    uploaded_file_2 = st.file_uploader("Arrastra el segundo archivo Excel aquí", type="xlsx")

    if uploaded_file_1 is not None and uploaded_file_2 is not None:
        # Leer los archivos Excel
        df1 = pd.read_excel(uploaded_file_1)
        df2 = pd.read_excel(uploaded_file_2)

        # Mostrar columnas de cada archivo
        st.subheader("Columnas del Primer Archivo:")
        st.write(df1.columns.tolist())

        st.subheader("Columnas del Segundo Archivo:")
        st.write(df2.columns.tolist())

        # Comparar columnas
        st.subheader("Comparación de Columnas:")
        columnas_comunes = set(df1.columns).intersection(set(df2.columns))
        columnas_unicas_1 = set(df1.columns) - columnas_comunes
        columnas_unicas_2 = set(df2.columns) - columnas_comunes

        st.write(f"Columnas comunes: {columnas_comunes}")
        st.write(f"Columnas únicas en el primer archivo: {columnas_unicas_1}")
        st.write(f"Columnas únicas en el segundo archivo: {columnas_unicas_2}")

        # Mostrar dimensiones de cada archivo
        st.subheader("Dimensiones de los Archivos:")
        st.write(f"Primer archivo: {df1.shape[0]} filas y {df1.shape[1]} columnas")
        st.write(f"Segundo archivo: {df2.shape[0]} filas y {df2.shape[1]} columnas")

    else:
        st.write("Por favor, carga ambos archivos Excel para continuar.")

def page2():
    import streamlit as st
    import pandas as pd

    def create_pivot_table(df):
        # Filtrar los datos
        df_filtered = df[(df['vigente_no_eliminado'] == True) & (df['fecha_notificacion']>='2022-01-01')]

        # Crear la tabla dinámica
        pivot_table = pd.pivot_table(df_filtered,
                                    values='id_enfermedad_eno', 
                                    index=['enfermedad_notificada', 'etapa_clinica'],
                                    columns=['estado_caso'],
                                    aggfunc='count')

        return pivot_table

    st.title("Crear Tabla Dinámica desde Excel")

    # Subir el archivo Excel
    uploaded_file = st.file_uploader("Arrastra un archivo Excel aquí", type="xlsx")

    if uploaded_file is not None:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file)

        # Crear y mostrar la tabla dinámica
        st.subheader("Tabla Dinámica")
        pivot_table = create_pivot_table(df)
        st.dataframe(pivot_table)

    else:
        st.write("Por favor, sube un archivo Excel para crear la tabla dinámica.")
def page3():
    import streamlit as st
    import pandas as pd

    def load_and_filter_data(file, diseases_of_interest):
        df = pd.read_excel(file)
        df_filtered = df[
            (df['vigente_no_eliminado'] == True) & 
            (df['fecha_notificacion'] >= '2023-01-01') & 
            (df['enfermedad_notificada'].isin(diseases_of_interest))
        ]
        return df_filtered

    def create_pivot_table(df_filtered):
        pivot_table = pd.pivot_table(df_filtered,
                                    values='id_enfermedad_eno', 
                                    index=['enfermedad_notificada', 'etapa_clinica'],
                                    columns=['estado_caso'],
                                    aggfunc='count',
                                    margins=True, margins_name='Total')
        return pivot_table.reset_index()

    def calculate_comparison_table(pivot_table_1, pivot_table_2, date1, date2):
        # Buscar la fila 'Total' en las columnas después de reset_index
        total_row_1 = pivot_table_1[pivot_table_1['enfermedad_notificada'] == 'Total']
        total_row_2 = pivot_table_2[pivot_table_2['enfermedad_notificada'] == 'Total']

        # Filtrar las filas donde etapa_clinica es 'SOSPECHA'
        sospecha_row_1 = pivot_table_1[(pivot_table_1['etapa_clinica'] == 'SOSPECHA') & (pivot_table_1['enfermedad_notificada'] != 'Total')]
        sospecha_row_2 = pivot_table_2[(pivot_table_2['etapa_clinica'] == 'SOSPECHA') & (pivot_table_2['enfermedad_notificada'] != 'Total')]

        # Sumar las columnas de interés en las filas filtradas, excluyendo 'No validada'
        pendientes_validacion_1 = total_row_1['Inconcluso'].values[0] if 'Inconcluso' in total_row_1 else 0
        pendientes_validacion_2 = total_row_2['Inconcluso'].values[0] if 'Inconcluso' in total_row_2 else 0

        # Calcular "Sospechas*" excluyendo "No validada"
        sospechas_1 = sospecha_row_1['Inconcluso'].sum() + sospecha_row_1['Validada'].sum()
        sospechas_2 = sospecha_row_2['Inconcluso'].sum() + sospecha_row_2['Validada'].sum()

        comparison_data = {
            "Fecha": [date1, date2],
            "Pendientes Validación": [pendientes_validacion_1, pendientes_validacion_2],
            "Sospechas*": [sospechas_1, sospechas_2],
        }

        comparison_df = pd.DataFrame(comparison_data)

        return comparison_df

    # Streamlit app
    st.title("Comparación de Tablas Dinámicas para ENO")

    # Subir los archivos Excel
    uploaded_file_1 = st.file_uploader("Sube el primer archivo Excel", type="xlsx")
    uploaded_file_2 = st.file_uploader("Sube el segundo archivo Excel", type="xlsx")

    if uploaded_file_1 and uploaded_file_2:
        # Extraer las fechas desde los nombres de los archivos
        date1 = uploaded_file_1.name.split('.')[0]
        date2 = uploaded_file_2.name.split('.')[0]

        diseases_of_interest = [
            'Carbunco', 'Cólera', 'Difteria', 
            'Fiebre del Nilo Occidental', 'Fiebres hemorrágicas',
            'Peste', 'Poliomielitis (Parálisis Flácidas Agudas)',
            'Rabia humana', 'Rubéola', 'Sarampión'
        ]

        # Cargar y filtrar los datos
        df_filtered1 = load_and_filter_data(uploaded_file_1, diseases_of_interest)
        df_filtered2 = load_and_filter_data(uploaded_file_2, diseases_of_interest)

        # Crear las tablas dinámicas
        pivot_table_1 = create_pivot_table(df_filtered1)
        pivot_table_2 = create_pivot_table(df_filtered2)

        # Calcular la tabla de comparación
        comparison_df = calculate_comparison_table(pivot_table_1, pivot_table_2, date1, date2)

        # Mostrar las tablas dinámicas y la tabla de comparación
        st.subheader(f"Tabla Dinámica del archivo {date1}")
        st.dataframe(pivot_table_1)
        
        st.subheader(f"Tabla Dinámica del archivo {date2}")
        st.dataframe(pivot_table_2)
        
        st.subheader("Tabla de Comparación entre las dos Tablas Dinámicas")
        st.dataframe(comparison_df)
    else:
        st.write("Por favor, sube ambos archivos Excel para continuar.")


pg = st.navigation([
    st.Page(page1, title="Prueba de lectura de archivos excel", icon="🤖"),
    st.Page(page2, title="Tabla dinamica archivos excel", icon="🧮"),
    st.Page(page3, title="Comparacion 2 archivos excel", icon="🧮")
])
pg.run()

