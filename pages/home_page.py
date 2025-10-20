import streamlit as st # type: ignore
import pandas as pd
import json
import requests
import plotly.graph_objects as go

# Set the title of the Streamlit app
st.title('Dashboard de Interacciones')

# Carga de Datos
url = "https://n8n.virtual.uniandes.edu.co/webhook/7cd7a485-f4f3-4838-96b7-9267e1b1e866"
df_lista_estudiantes = pd.read_csv("estudiantes_IAU.csv", sep=";")
 
@st.cache_data(ttl="1m", show_spinner=True) # Cada 5 minutos se actualizan los datos
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


total_interacciones = df_database['numerointeracciones'].sum()
num_usuarios = df_database['email'].nunique()
col1, col2 = st.columns(2)
col1.metric("Numero de Usuarios Unicos", num_usuarios)
col2.metric("Numero Total de Interacciones", total_interacciones)

st.header('Resumen de Uso', divider=True)

list_clases = df_database['modelo'].unique()
list_clases.sort()
list_emails_usados = df_database['email'].unique()

metricas_por_clase = []

for clase in list_clases:
    codigo_clase = clase.split("_")[0]
    filtered_df = df_database[df_database['modelo'] == clase]

    # Calculo metricas
    num_users = filtered_df['email'].nunique()
    total_interacciones_modelo = filtered_df['numerointeracciones'].sum()
    try:
        if clase != 'MINE4101_CreacionNotebooks':
            total_esperados = len(df_lista_estudiantes[df_lista_estudiantes['Clase'] == codigo_clase]['Email'].tolist())
        else:
            total_esperados = 1
    except:
        total_esperados = 0
    
    metricas_por_clase.append({
        'clase': f"{" ".join(clase.split('_'))}",
        'estudiantes_que_usaron': num_users,
        'estudiantes_esperados': total_esperados,
        'cantidad_interacciones': total_interacciones_modelo
    }) 
    
for metrica in metricas_por_clase:
    st.subheader(f"**{metrica['clase']}**")
    
    # Calcular porcentaje de uso
    if metrica['estudiantes_esperados'] > 0:
        porcentaje_uso = (metrica['estudiantes_que_usaron'] / metrica['estudiantes_esperados']) * 100
    else:
        porcentaje_uso = 0
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Gráfico gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = porcentaje_uso,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "% de Estudiantes que Usaron"},
            delta = {'reference': 100},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ]
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True, key=f"gauge_{metrica['clase']}")
    
    with col2:
        # Métricas en la segunda columna
        st.metric("Estudiantes que usaron", metrica['estudiantes_que_usaron'])
        st.metric("Total de estudiantes esperados", metrica['estudiantes_esperados'])
        st.metric("Total de interacciones", metrica['cantidad_interacciones'])
    
    st.write("---")