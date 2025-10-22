import streamlit as st # type: ignore
from pages.home_page import df_lista_estudiantes, url
import requests
import pandas as pd

def select_model(model):
    st.session_state.selected_model = model

st.cache_data(ttl="1m", show_spinner=True) # Cada 5 minutos se actualizan los datos
def load_data():
    headers = {
        "Authorization": "Bearer TokenIAU"
    }

    response_data = requests.get(url, headers=headers, timeout=120)

    df_db = pd.DataFrame(response_data.json())

    df_db['fechafinalint'] = pd.to_datetime(df_db['fechafinalint'])
    df_db['fechainicialint'] = pd.to_datetime(df_db['fechainicialint'])
    
    return df_db

df_database = load_data()

model_list = df_database['modelo'].unique()
model_list.sort()

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = model_list[0]

for model in model_list:
    st.sidebar.button(model, on_click=select_model, args=[model])


selected_model = st.session_state.selected_model

# filtrado del dataframe
filtered_df = df_database[df_database['modelo'] == selected_model]
emails_monitores_IAU = df_lista_estudiantes[df_lista_estudiantes['Clase'] == 'IAU']['Email'].tolist()

# Titulo principal
st.header(f'Insights del Modelo: {" ".join(selected_model.split("_"))}')

if not filtered_df.empty:

    # subtitulo
    st.subheader('Metricas Clave')
    
    # Numero de usuarios unicos y total de interacciones
    nombre_clase = selected_model.split("_")[0]
    num_users = filtered_df['email'].nunique()
    total_interactions = filtered_df['numerointeracciones'].sum()
    try:
        estudiantes_clase = df_lista_estudiantes[df_lista_estudiantes['Clase'] == nombre_clase]['Email'].tolist()
        cantidad_estudiantes_clase = [email for email in estudiantes_clase if email not in emails_monitores_IAU]

    except:
        cantidad_estudiantes_clase = []
    
    total_esperados = len(cantidad_estudiantes_clase)
    
    # Display de las metricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Numero Total de Usuarios Unicos", num_users)
    col2.metric("Numero Total de Interacciones", total_interactions)
    col3.metric("Numero Total de Estudiantes en Clase", total_esperados)

    # Top 5 usuarios (solo estudiantes, excluyendo monitores)
    st.subheader('Top 5 Estudiantes por Interacciones')
    
    # Filtrar el DataFrame para excluir monitores
    filtered_df_estudiantes = filtered_df[~filtered_df['email'].isin(emails_monitores_IAU)]
    
    if not filtered_df_estudiantes.empty:
        top_users = filtered_df_estudiantes.groupby('email')['numerointeracciones'].sum().nlargest(5).reset_index()
        st.dataframe(top_users)
    else:
        st.info("No hay interacciones de estudiantes registradas para este modelo.")

    # INteracciones por dia
    st.subheader('Numero de Interacciones por Dia')
    
    interactions_by_date = filtered_df.groupby(filtered_df['fechainicialint'].dt.date)['numerointeracciones'].sum()
    
    # Diagrama de interacciones
    st.bar_chart(interactions_by_date)
    
else:
    st.warning('No hay información disponible para este modelo.')