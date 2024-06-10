import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np

class App():
    def __init__(self) -> None:
        self.pag_central()

    def lat_bar(self):
        pass

    def pag_central(self):
        st.write('# **Bienvenido al recomendador de Airbnb**')
        st.markdown('---')
        ruta_img='/Users/mariolamas/Downloads/prueba_Casa.png'

        items=[{'image':ruta_img, 'text':elem[2],'Rating':elem[-2],'ubi':elem[14]} for elem in self.recomendar_populares(4).itertuples()]
        st.write('#### **Los más populares**')
        # Mostrar las imágenes con texto
        self.display_images_with_text(items)

        st.write('#### **Para ti**')
    
    def display_images_with_text(self,items):
        st.markdown("<style>.container { display: flex; flex-wrap: nowrap; } .container img { margin-right: 10px; } .container div { display: flex; flex-direction: column; justify-content: center; }</style>", unsafe_allow_html=True)
        container = st.container()
        with container:
            col1, col2,col3,col4 = st.columns(4)
            with col1:
                st.image(items[0]['image'], use_column_width=True)
                st.write(items[0]['text'])
                st.write(round(items[0]['Rating'],1),'⭐️')
                st.write(items[0]['ubi'],'📍')
                
            with col2:
                st.image(items[1]['image'], use_column_width=True)
                st.write(items[1]['text'])
                st.write(round(items[1]['Rating'],1),'⭐️')
                st.write(items[1]['ubi'],'📍')

            with col3:
                st.image(items[2]['image'], use_column_width=True)
                st.write(items[2]['text'])
                st.write(round(items[2]['Rating'],1),'⭐️')
                st.write(items[2]['ubi'],'📍')

            with col4:
                st.image(items[3]['image'], use_column_width=True)
                st.write(items[3]['text'])
                st.write(round(items[3]['Rating'],1),'⭐️')
                st.write(items[3]['ubi'],'📍')

            st.write("---")
    
    def recomendar_populares(self,n):
        """
        Funcion encargada de retornar los n apartamentos mas populares en funcion de cantidad de evaluaciones y ratings.

        Args:
            n (int): Numero de apartamenos mas populares

        Returns:
            pd.DataFrame: DataFrame con la informacion de los apartamentos más populares
        """
        df=pd.read_csv('Dataset_Apart/Cleaned/DatasetAirbnb_Cleaned_v1.csv')
        # Definir las columnas de calificaciones
        rating_columns = ['Limpieza', 'Veracidad', 'Llegada', 'Comunicacion', 'Ubicacion', 'Calidad']

        # Llenar valores faltantes en las columnas de calificaciones con la media
        df[rating_columns] = df[rating_columns].fillna(df[rating_columns].mean())

        # Calcular el promedio de las calificaciones para cada apartamento
        df['Promedio_Ratings'] = df[rating_columns].mean(axis=1)

        # Definir la puntuación de popularidad como una combinación de evaluaciones y promedio de ratings
        # Ajusta los pesos según la importancia que quieras dar a cada factor
        peso_evaluaciones = 0.6
        peso_ratings = 0.4

        df['Puntuacion_Popularidad'] = peso_evaluaciones * df['Evaluaciones'] + peso_ratings * df['Promedio_Ratings']

        def recomendador_por_popularidad(df, top_n=5):
            return df.sort_values(by='Puntuacion_Popularidad', ascending=False).head(top_n)

        # Obtener los 3 apartamentos más populares según la nueva métrica
        recomendaciones_populares = recomendador_por_popularidad(df, top_n=n)
        return recomendaciones_populares





    