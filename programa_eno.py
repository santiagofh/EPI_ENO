import streamlit as st
import pandas as pd
from io import BytesIO

patologias_por_fase = {
    "Fase 1":[
            "Carbunco",
            "Cólera",
            "Difteria",
            "Fiebre del Nilo Occidental",
            "Fiebres hemorrágicas",
            "Peste",
            "Poliomielitis (Parálisis Flácidas Agudas)",
            "Rabia humana",
            "Rubéola",
            "Sarampión" ],
    "Fase 2":[
            "Botulismo infantil",
            "Botulismo adulto",
            "Difteria",
            "Malaria",
            "Triquinosis",
            "Leptospirosis",
            "Chagas agudo",
            "Arbovirus (dengue, zika, chikungunya, fiebre amarilla)",
            "Meningitis Bacteriana, Enf.Meningocócica y Enf.Invasora por Haemophilius Influenzae",
            "Síndrome Pulmonar por Hantavirus"
        ],
    "Fase 3":[
            "Brucelosis",
            "Cisticercosis",
            "Coqueluche (Tos Ferina)",
            "Enfermedad de Chagas crónico",
            "Enfermedad de Creutzfeldt-Jakob (ECJ)",
            "Fiebre Q",
            "Fiebre Tifoidea y Paratifoidea",
            "Gonorrea",
            "Hepatitis A",
            "Hepatitis B",
            "Hepatitis C",
            "Hepatitis E",
            "Hidatidosis (Equinococosis)",
            "Leishmaniasis",
            "Lepra",
            "Listeriosis",
            "Neumococo",
            "Parotiditis",
            "Psitacosis",
            "Sífilis",
            "Síndrome de Inmunodeficiencia Adquirida (VIH/SIDA)",
            "Tétanos",
            "Tétanos Neonatal",
            "Tuberculosis en todas sus formas y localizaciones"
        ]
}


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

    return comparison_df, pendientes_validacion_2, sospechas_2

def generate_excel(pivot_table_1, pivot_table_2, comparison_df, df_filtered1, df_filtered2):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Escribir cada DataFrame en una hoja de Excel
    pivot_table_1.to_excel(writer, sheet_name='Tabla Dinámica 1', index=False)
    pivot_table_2.to_excel(writer, sheet_name='Tabla Dinámica 2', index=False)
    comparison_df.to_excel(writer, sheet_name='Comparación', index=False)

    # Filtrar datos de pendientes de validación y sospechas
    pendientes_validacion_df_1 = df_filtered1[df_filtered1['estado_caso'] == 'Inconcluso']
    pendientes_validacion_df_2 = df_filtered2[df_filtered2['estado_caso'] == 'Inconcluso']
    sospechas_df_1 = df_filtered1[(df_filtered1['etapa_clinica'] == 'SOSPECHA') & (df_filtered1['estado_caso'].isin(['Inconcluso', 'Validada']))]
    sospechas_df_2 = df_filtered2[(df_filtered2['etapa_clinica'] == 'SOSPECHA') & (df_filtered2['estado_caso'].isin(['Inconcluso', 'Validada']))]

    # Escribir datos de pendientes de validación
    pendientes_validacion_df_1.to_excel(writer, sheet_name='Pendientes Validacion 1', index=False)
    pendientes_validacion_df_2.to_excel(writer, sheet_name='Pendientes Validacion 2', index=False)

    # Escribir datos de sospechas
    sospechas_df_1.to_excel(writer, sheet_name='Sospechas 1', index=False)
    sospechas_df_2.to_excel(writer, sheet_name='Sospechas 2', index=False)

    writer.close()
    output.seek(0)

    return output


# Streamlit app
st.title("Comparación de Tablas Dinámicas para ENO")

data = [(fase, patologia) for fase, patologias in patologias_por_fase.items() for patologia in patologias]
df_patologias = pd.DataFrame(data, columns=['Fase', 'Patología'])


# Subir los archivos Excel
uploaded_file_1 = st.file_uploader("Sube el primer archivo Excel", type="xlsx")
uploaded_file_2 = st.file_uploader("Sube el segundo archivo Excel", type="xlsx")

selec_fase=['Fase 1','Fase 2','Fase 3']

st.subheader("Patologías por Fase")
st.dataframe(df_patologias)
fase=st.multiselect("Seleccione la FASE de interés:",selec_fase,selec_fase[0])
diseases_of_interest=[]
for selected_fase in fase:
    patologias = patologias_por_fase[selected_fase]
    diseases_of_interest.extend(patologias)

if uploaded_file_1 and uploaded_file_2:
    # Extraer las fechas desde los nombres de los archivos
    date1 = uploaded_file_1.name.split('.')[0]
    date2 = uploaded_file_2.name.split('.')[0]

    # Cargar y filtrar los datos
    df_filtered1 = load_and_filter_data(uploaded_file_1, diseases_of_interest)
    df_filtered2 = load_and_filter_data(uploaded_file_2, diseases_of_interest)

    # Crear las tablas dinámicas
    pivot_table_1 = create_pivot_table(df_filtered1)
    pivot_table_2 = create_pivot_table(df_filtered2)

    # Calcular la tabla de comparación
    comparison_df, pendientes_validacion_2, sospechas_2 = calculate_comparison_table(pivot_table_1, pivot_table_2, date1, date2)

    # Mostrar las tablas dinámicas y la tabla de comparación
    st.subheader(f"Tabla Dinámica del archivo {date1}")
    st.dataframe(pivot_table_1)
    
    st.subheader(f"Tabla Dinámica del archivo {date2}")
    st.dataframe(pivot_table_2)
    
    st.subheader("Tabla de Comparación entre las dos Tablas Dinámicas")
    st.dataframe(comparison_df)

    # Generar y permitir la descarga del archivo Excel con los detalles completos
    output = generate_excel(pivot_table_1, pivot_table_2, comparison_df, df_filtered1, df_filtered2)
    st.download_button(
        label="Descargar Excel",
        data=output,
        file_name="comparacion_tablas_dinamicas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.write("Por favor, sube ambos archivos Excel para continuar.")

