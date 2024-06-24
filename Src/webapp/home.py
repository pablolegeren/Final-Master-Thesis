import streamlit as st
from env.env import *
from st_clickable_images import clickable_images
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import requests
import json

def upload_file(cdn_path,bytes,file_name=None):
        
        if(cdn_path[-1]=='/'):
            cdn_path=cdn_path[:-1]

        request_url=st.session_state.base_url+cdn_path

        response=requests.request("PUT",request_url,data=bytes,headers=st.session_state.headers)

        return(response.json())

def get_file(cdn_path,download_path=None):
    if(cdn_path[-1]=='/'):
        cdn_path=cdn_path[:-1]

    filename=cdn_path.split('/')[-1]

    request_url=st.session_state.base_url+cdn_path
    response = requests.request("GET", request_url, headers=st.session_state.headers)
    
    if(response.status_code==404):
        raise ValueError('No such file exists')

    if(response.status_code!=200):
        raise Exception('Some error, please check all settings once and retry')

    if(download_path==None):
        download_path=filename

    return response.content.decode('utf-8')

def inicializacion():
    for elem in PARAMETROS_INICIALES.keys():
        if elem not in st.session_state:
            st.session_state[elem]=PARAMETROS_INICIALES[elem]
    st.session_state.headers={
        'AccessKey': st.session_state.api_key
    }

    if(st.session_state.storage_zone_region=='de' or st.session_state.storage_zone_region==''):
        st.session_state.base_url='https://storage.bunnycdn.com/'+st.session_state.storage_zone+'/'

    else:
        st.session_state.base_url='https://'+st.session_state.storage_zone_region+'.storage.bunnycdn.com/'+st.session_state.storage_zone+'/'

def inicio():
    st.markdown("<h1 style='text-align: center;'>RECOMENDADOR AIRBNB</h1>", unsafe_allow_html=True)
    st.markdown('---')
    st.markdown("<h1 style='text-align: center;'>¿Cual Prefieres?</h1>", unsafe_allow_html=True)
    #st.write('## **¿Cual Prefieres?**')
    df=pd.read_csv('Dataset_Apart/Cleaned/DatasetAirbnb_Cleaned_v1.csv')
    reducida=df.sample(2)
    col1,col2 = st.columns(2)
    with col1:
        with st.container(height=500):
            clicked = clickable_images(
                [reducida['url_img'].values[0]],
                titles=[f"Image #{str(i)}" for i in range(5)],
                div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                img_style={"margin": "5px", "height": "200px"})
            st.write(f'### **{reducida['Titulo'].values[0]}**')
            st.write(round(np.mean(reducida[['Limpieza', 'Veracidad', 'Llegada', 'Comunicacion', 'Ubicacion', 'Calidad']].values[0]),1) if round(np.mean(reducida[['Limpieza', 'Veracidad', 'Llegada', 'Comunicacion', 'Ubicacion', 'Calidad']].values[0]),1)!=np.nan else 'Nuevo!','⭐️')
            st.write(reducida['Localizacion'].values[0],'📍')
            st.link_button("Ver más", reducida['URL'].values[0])
            if clicked:
                st.session_state.ids.append(reducida['ID'].values[0])
                st.session_state.iteraciones+=1
            
    with col2:
        with st.container(height=500):
            clicked_2 = clickable_images(
                [reducida['url_img'].values[1]],
                titles=[f"Image #{str(i)}" for i in range(5)],
                div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
                img_style={"margin": "5px", "height": "200px"})
            st.write(f'### **{reducida['Titulo'].values[1]}**')
            st.write(round(np.mean(reducida[['Limpieza', 'Veracidad', 'Llegada', 'Comunicacion', 'Ubicacion', 'Calidad']].values[1]),1) if round(np.mean(reducida[['Limpieza', 'Veracidad', 'Llegada', 'Comunicacion', 'Ubicacion', 'Calidad']].values[1]),1)!=np.nan else 'Nuevo!','⭐️')
            st.write(reducida['Localizacion'].values[1],'📍')
            st.link_button("Ver más", reducida['URL'].values[1])
            if clicked_2:
                st.session_state.ids.append(reducida['ID'].values[1])
                st.session_state.iteraciones+=1
def recomendar_populares(condicion=None):
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

    rating_columns = ['Limpieza', 'Veracidad', 'Llegada', 'Comunicacion', 'Ubicacion', 'Calidad']
    # Calcular el promedio de las calificaciones para cada apartamento
    df['Promedio_Ratings'] = df[rating_columns].mean(axis=1)

    # Definir la puntuación de popularidad como una combinación de evaluaciones y promedio de ratings
    # Ajusta los pesos según la importancia que quieras dar a cada factor
    peso_evaluaciones = 0.6
    peso_ratings = 0.4

    df['Puntuacion_Popularidad'] = peso_evaluaciones * df['Evaluaciones'] + peso_ratings * df['Promedio_Ratings']

    def recomendador_por_popularidad(df):
        return df.sort_values(by='Puntuacion_Popularidad', ascending=False)

    # Obtener los 3 apartamentos más populares según la nueva métrica
    recomendaciones_populares = recomendador_por_popularidad(df)
    if condicion is not None:
        return recomendaciones_populares[recomendaciones_populares['Tipo']==condicion]
    return recomendaciones_populares

def recomendar_para_ti(data_apart,n):

    # Seleccionar características para calcular la similitud
    features = ['ID','Titulo','Descripcion Simple','URL','url_img','Localizacion']
    features_to_scale =[elem for elem in data_apart.columns if elem not in features]

    # Escalar características
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(data_apart[features_to_scale])

    # Calcular la similitud del coseno
    similarity_matrix = cosine_similarity(scaled_features)

    # Función para recomendar apartamentos similares
    def recomendador_por_similitud(df, apartment_id, top_n=30):
        # Encontrar el índice del apartamento
        idx = df.index[df['ID'] == apartment_id][0]
        
        # Obtener la similitud de los apartamentos
        similarity_scores = list(enumerate(similarity_matrix[idx]))
        
        # Ordenar los apartamentos por similitud
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        # Obtener los índices de los apartamentos más similares
        similar_apartments_indices = [i[0] for i in similarity_scores[1:top_n+1]]
        scores=[i[1] for i in similarity_scores[1:top_n+1]]
        
        return df.iloc[similar_apartments_indices],scores
    recomendaciones=pd.DataFrame(columns=list(data_apart.columns).extend(['Similitud']))
    for ap in st.session_state.ids:
        recomendaciones_similares, puntuaciones = recomendador_por_similitud(data_apart, ap, top_n=n)
        recomendaciones_similares['Similitud']=puntuaciones
        recomendaciones=pd.concat([recomendaciones,recomendaciones_similares])
    return recomendaciones



def pag_central(data_apart):
    st.markdown("<h1 style='text-align: center;'>RECOMENDADOR AIRBNB</h1>", unsafe_allow_html=True)

    st.markdown('---')
    ruta_img='/Users/mariolamas/Downloads/prueba_Casa.png'

    items=[{'image':elem[-5], 'text':elem[2],'Rating':elem[-2],'ubi':elem[14],'url_apart':elem[7]} for elem in recomendar_populares().itertuples()]
    st.write('#### **Los más populares**')
    # Mostrar las imágenes con texto
    display_images_with_text(items)

    st.write('#### **Para ti**')
    recomendaciones=recomendar_para_ti(data_apart,4)
    recom_ordered=recomendaciones.sort_values(by='Similitud',ascending=False)
    recom_ordered=recom_ordered.drop('Similitud',axis=1)
    rating_columns = ['Limpieza', 'Veracidad', 'Llegada', 'Comunicacion', 'Ubicacion', 'Calidad']
    # Calcular el promedio de las calificaciones para cada apartamento
    recom_ordered['Promedio_Ratings'] = recom_ordered[rating_columns].mean(axis=1)
    items_2=[{'image':elem[-4], 'text':elem[2],'Rating':elem[-1],'ubi':elem[14],'url_apart':elem[7]} for elem in recom_ordered.iloc[:4].itertuples()]
    display_images_with_text(items_2)

    st.write('#### **En la Playa**')
    recom_playa=recom_ordered[recom_ordered['Tipo']==2.0]
    if recom_playa.shape[0]<4:
        playa_popu=recomendar_populares(condicion=2.0)
        playa_popu.drop(['Puntuacion_Popularidad'],axis=1,inplace=True)
        recom_playa=pd.concat([recom_playa,playa_popu],axis=0)
    items_3=[{'image':elem[-4], 'text':elem[2],'Rating':elem[-1],'ubi':elem[14],'url_apart':elem[7]} for elem in recom_playa.iloc[:4].itertuples()]
    display_images_with_text(items_3)

    st.write('#### **En el Campo**')
    recom_campo=recom_ordered[recom_ordered['Tipo']==0.0]
    if recom_campo.shape[0]<4:
        campo_popu=recomendar_populares(condicion=0.0)
        campo_popu.drop(['Puntuacion_Popularidad'],axis=1,inplace=True)
        recom_campo=pd.concat([recom_campo,campo_popu],axis=0)
    items_4=[{'image':elem[-4], 'text':elem[2],'Rating':elem[-1],'ubi':elem[14],'url_apart':elem[7]} for elem in recom_campo.iloc[:4].itertuples()]
    display_images_with_text(items_4)

    st.write('#### **Cabañas**')
    recom_cabaña=recom_ordered[recom_ordered['Tipo']==1.0]
    if recom_cabaña.shape[0]<4:
        cab_popu=recomendar_populares(condicion=1.0)
        cab_popu.drop(['Puntuacion_Popularidad'],axis=1,inplace=True)
        recom_cabaña=pd.concat([recom_cabaña,cab_popu],axis=0)
    
    items_5=[{'image':elem[-4], 'text':elem[2],'Rating':elem[-1],'ubi':elem[14],'url_apart':elem[7]} for elem in recom_cabaña.iloc[:4].itertuples()]
    display_images_with_text(items_5)


def display_images_with_text(items):
    st.markdown("<style>.container { display: flex; flex-wrap: nowrap; } .container img { margin-right: 10px; } .container div { display: flex; flex-direction: column; justify-content: center; }</style>", unsafe_allow_html=True)
    container = st.container()
    with container:
        col1, col2,col3,col4 = st.columns(4)
        with col1:
            with st.container(height=500):
                st.image(items[0]['image'], width=200,use_column_width=True)
                st.write(items[0]['text'])
                st.write(round(items[0]['Rating'],1),'⭐️')
                st.write(items[0]['ubi'],'📍')
                st.link_button("Ver más", items[0]['url_apart'])
            
        with col2:
            with st.container(height=500):
                st.image(items[1]['image'], width=200,use_column_width=True)
                st.write(items[1]['text'])
                st.write(round(items[1]['Rating'],1),'⭐️')
                st.write(items[1]['ubi'],'📍')
                st.link_button("Ver más", items[1]['url_apart'])

        with col3:
            with st.container(height=500):
                st.image(items[2]['image'], width=200,use_column_width=True)
                st.write(items[2]['text'])
                st.write(round(items[2]['Rating'],1),'⭐️')
                st.write(items[2]['ubi'],'📍')
                st.link_button("Ver más", items[2]['url_apart'])

        with col4:
            with st.container(height=500):
                st.image(items[3]['image'], width=200,use_column_width=True)
                st.write(items[3]['text'])
                st.write(round(items[3]['Rating'],1),'⭐️')
                st.write(items[3]['ubi'],'📍')
                st.link_button("Ver más", items[3]['url_apart'])

        st.write("---")


inicializacion()

if st.session_state.iteraciones<=5:
    inicio()
else:
    data_usuarios=get_file('usuarios.json','user.json')
    print(data_usuarios)
    info_user=json.loads(data_usuarios)
    ids=','.join([f'{elem}' for elem in st.session_state.ids])
    print(ids)
    info_user[st.session_state.user_id]=ids
    info_user = {k: (int(v) if isinstance(v, np.int64) else v) for k, v in info_user.items()}
    json_str = json.dumps(info_user)
    # Convertir la cadena JSON a bytes
    bytes_obj = json_str.encode('utf-8')
    respuesta=upload_file('usuarios.json',bytes=bytes_obj)
    print(respuesta)
    pag_central(data_apart=pd.read_csv('Dataset_Apart/Cleaned/DatasetAirbnb_Cleaned_v1.csv'))
