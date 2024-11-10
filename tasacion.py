import pandas as pd
import streamlit as st
from datetime import datetime

# Load data from the Excel file
#@st.cache_data
def load_data():
    file_path = 'tasacion_coches2024.xlsx'  # Update the path to a local relative path
    xls = pd.ExcelFile(file_path)
    coches_df = pd.read_excel(xls, 'coches')
    tasacion_df = pd.read_excel(xls, 'tasacion')
    
    # Clean up column names for better access
    coches_df.columns = [str(col).strip() for col in coches_df.iloc[0]]
    coches_df = coches_df[1:]
    coches_df.reset_index(drop=True, inplace=True)
    # Ensure column names are accessible
    coches_df.columns = coches_df.columns.str.replace(' ', '_').str.replace('.', '').str.lower()
    tasacion_df.columns = tasacion_df.columns.str.replace(' ', '_').str.replace('.', '').str.lower()
        
    return coches_df, tasacion_df

coches_df, tasacion_df = load_data()

# Streamlit app
st.title('Aplicación de Tasación de Coches')

# Step 1: Select the car by brand
marca = st.selectbox('Seleccione la marca del coche:', sorted(coches_df['marca'].unique()))
filtered_df = coches_df[coches_df['marca'] == marca]

# Step 1.1: Input registration date and filter by commercial period
fecha_matriculacion = st.date_input('Ingrese la fecha de matriculación del coche:', value=datetime.now())

current_date = datetime.now()

year_matriculacion = fecha_matriculacion.year
filtered_df = filtered_df[(filtered_df['inicio'] <= year_matriculacion) & (filtered_df['fin'] >= year_matriculacion)]

# Step 1.2: Select fuel type and filter by it
combustibles_disponibles = ['Todos'] + filtered_df['combustible'].unique().tolist()
combustible = st.selectbox('Seleccione el tipo de combustible (o todos):', combustibles_disponibles)
if combustible != 'Todos':
    filtered_df = filtered_df[filtered_df['combustible'] == combustible]

# Step 1.3: Filter by model and display additional information
modelos_disponibles = [f"{m} - {c} Cv" for m, c in zip(filtered_df['modelo-tipo'], filtered_df['cv'])]
if modelos_disponibles:
    modelo = st.selectbox('Seleccione el modelo del coche:', modelos_disponibles)
    selected_model = modelo.split(' - ')[0]
    filtered_model_df = filtered_df[filtered_df['modelo-tipo'] == selected_model]

    # Display additional information about the selected car
    st.write('Información del coche seleccionado:')
    for index, row in filtered_model_df.iterrows():
        st.write(f"Periodo comercial: {row['inicio']} - {row['fin']}")
        st.write(f"Cilindrada (C.C.): {row['cc']}")
        st.write(f"Número de cilindros: {row['cilindros']}")
        st.write(f"Combustible: {row['combustible']}")
        st.write(f"Potencia (P kW): {row['pkw']}")
        st.write(f"Coeficiente fiscal (cvf): {row['cvf']}")
        st.write(f"Potencia (cv): {row['cv']}")

    # Step 3: Calculate car age and get valuation percentage
    car_age = (current_date.year - fecha_matriculacion.year) * 12 + (current_date.month - fecha_matriculacion.month)
    car_age_month = (current_date.month - fecha_matriculacion.month)
    car_age_year = (current_date.year - fecha_matriculacion.year)

    # Find the appropriate valuation percentage from tasacion
    def get_percentage_for_car_age(car_age, tasacion_df):
        porcentaje_tasacion = tasacion_df[(tasacion_df['desde'] <= car_age) & (tasacion_df['hasta'] >= car_age)]
        if not porcentaje_tasacion.empty:
            return porcentaje_tasacion['porcentajes'].values[0]
        else:
            return None

    porcentaje = get_percentage_for_car_age(car_age, tasacion_df)

    if not filtered_model_df.empty:
        valor_original = filtered_model_df['valor'].values[0]
        valor_original = float(valor_original)

        # Calculate the current valuation
        valor_actual = valor_original * (porcentaje / 100)
        valor_final = valor_actual + (valor_actual * 0.20)

        # Display the valuation result
        # st.write(f'Antigüedad del coche: {car_age} meses')
        st.write(f'Antigüedad del coche: {car_age_year} años {car_age_month} meses')
        st.write(f'Porcentaje de tasación aplicado: {porcentaje}%')
        st.write(f'Valor original del coche: {valor_original:.2f} euros')
        st.write(f'Valor actual del coche según su antigüedad: {valor_actual:.2f} euros')
        st.write(f'--- El valor final con el 20% de la ayuda: {valor_final:.2f} euros ---')
    else:
        st.write('No se encontraron coches que cumplan con los criterios seleccionados.')
else:
    st.write('No se encontraron modelos disponibles para los criterios seleccionados.')

