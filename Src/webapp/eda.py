import streamlit as st
import pandas as pd
import numpy as np
import io
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics import calinski_harabasz_score




def eda_clean_apart(data_apart):

    data_apart.head()

    st.subheader('Información general del dataset')
    st.markdown('''Comenzamos observando las columnas que tenemos y el tipo de datos que tienen asociados.''')
    with st.container(height=200):
        buffer = io.StringIO()
        data_apart.info(buf=buffer)
        st.text(buffer.getvalue())

    st.subheader('Valores faltantes')
    st.markdown('''Observamos la cantidad de valores faltantes que tiene cada columna del dataset. De esta forma, podremos decidir si es necesario imputar valores o eliminar columnas y con que metodología lo realizamos.''')
    st.data_editor(data_apart.isna().sum())

    st.subheader('Resumen estadístico')
    st.markdown('''Observamos algunos estadísticos básicos de las variables numéricas del dataset.''')
    st.write(data_apart.describe())

    st.subheader('Resumen estadístico de variables categóricas')
    st.markdown('''Observamos algunos estadísticos básicos de las variables categóricas del dataset.''')
    st.write(data_apart.describe(include='O'))

    st.subheader('Extracción de latitud y longitud de la variable Localización')
    st.markdown('''
    Convertimos la ubicacion en forma de texto a latitud y longitud para poder visualizarlo en un mapa empleando la libreria **geopy**.
    
    ```python
                
    def lat_log(l):
        geolocator = Nominatim(user_agent="España")
        try:
            location = geolocator.geocode(l)
            latitude = location.latitude
            longitude = location.longitude
            return latitude, longitude
        except:
            return 10000,10000
    data_apart['Latitud_Longitud']=data_apart['Localizacion'].apply(lambda x: lat_log(x))

    data_apart['Latitud']=data_apart['Latitud_Longitud'].apply(lambda x: x[0])
    data_apart['Longitud']=data_apart['Latitud_Longitud'].apply(lambda x: x[1])
    data_apart.drop('Latitud_Longitud',axis=1,inplace=True)
    ```
                ''')

    st.subheader('Correlación de variables numéricas')
    fig, ax = plt.subplots(figsize=(20,20))
    num_cols = data_apart.select_dtypes(include=['number']).columns
    sns.heatmap(data_apart[num_cols].corr(),annot=True, ax=ax)
    st.pyplot(fig)


    
    


def price_part(data_apart):
    # Datos con latitud/longitud y valores
    datos=data_apart[(data_apart['Latitud']!=10000)&(data_apart['Longitud']!=10000)][['Latitud','Longitud','Precio']]
    st.subheader('Mapa de densidad de precios')
    st.markdown('''A partir de la latitud y longitud de los apartamentos, se ha creado un mapa de densidad de precios, para estudiar las zonas más caras y más asequibles.''')
    fig = px.density_mapbox(datos, lat = 'Latitud', lon = 'Longitud', z = 'Precio',
                            radius = 7,
                            center = dict(lat = 40.45, lon = -3.6),
                            zoom = 4,
                            mapbox_style = 'open-street-map',
                            color_continuous_scale = 'rainbow',
                            opacity = 0.5)
    st.plotly_chart(fig)
    st.markdown('''
    Observamos que las zonas más caras son:
    - **Sierra Norte de Madrid**
    - **Alicante**
    - **San Sebastián**
    ''')

    st.subheader('Precio medio por tipo de apartamento')
    st.markdown('''El precio medio de los apartamentos de tipo "En el campo" es el más elevado.''')
    st.bar_chart(data_apart.groupby('Tipo').agg({'Precio':'mean'}).reset_index(),x='Tipo',y='Precio')

    st.subheader('Relación entre el precio y la calidad del apartamento')
    st.markdown('''El gráfico demuetra que según los datos no existe una relación directa entre la calidad percibida por los cliente y el precio lo cual es sorprendete ya que una de las hipótesis que se bajaraba era que a 
                mayor precio mayor calidad.''')
    st.scatter_chart(data_apart,x='Precio',y='Calidad')

    st.subheader('Relación entre el precio y la capacidad del apartamento')
    st.markdown('''El gráfico demuetra que según los datos existe claramente una relacion creciente ente la capacidad de huéspedes y el precio.
                Esta conclusion valida una de las hipótesis principales que a mayor tamaño mayor precio.''')
    datos_cap=data_apart.groupby('Capacidad').agg({'Precio':'mean'}).reset_index()
    st.line_chart(datos_cap,x='Capacidad',y='Precio')

def clustering(data_apart):
    columnas_innecesarias_cluster=['ID','Titulo','Descripcion Simple','URL','url_img','Localizacion']
    data_cluster=data_apart.drop(columnas_innecesarias_cluster,axis=1)
    Coste = []
    krange = np.arange(2, 11) #krange = 2,3,4,5,6,7,8,9,10
    # bucle para el cálculo de la función de coste (SSE) desde k= 2 hasta k= 10
    for num in krange:
        kmeans = KMeans(n_clusters=num, n_init='auto', random_state=10, max_iter=100).fit(data_cluster)
        print(
            "Para k =",
            num,
            ', el coste (SSE)=',
            kmeans.inertia_,
        )
        Coste.append(kmeans.inertia_)
    st.subheader('Método del codo')
    st.markdown(''' El método del codo es una técnica utilizada para determinar el número óptimo de clusters en un conjunto de datos de forma visual y preliminar.
''')
    st.line_chart(data=pd.DataFrame(zip(krange,Coste),columns=['krange','Coste']),x='krange',y='Coste')
    st.markdown('''En este caso observamos que el numero de clusters optimos esta en el rango 2 a 5. Para obtener numéricamente el número óptimo,
                empleamos el método de la silueta y calinski harabasz.''')
    
    st.subheader('Silueta y Calinski Harabasz')
    for k in [3,4,5,6,7,8]:
        kmeans = KMeans(n_clusters=k, n_init= 'auto', random_state=10, max_iter=3000)
        Y_pred=kmeans.fit_predict(data_cluster) # Vector de asignación de etiquetas predichas para cada elemento
        data_cluster['id_cluster']=kmeans.labels_
        silhouette_avg = silhouette_score(data_cluster.drop('id_cluster',axis=1),data_cluster['id_cluster'])
        cal=calinski_harabasz_score(data_cluster.drop('id_cluster',axis=1),data_cluster['id_cluster'])

        st.write('Para un Nº de clusters: ',k)
        st.write('- S: ',silhouette_avg)
        st.write('- CH: ',cal)
        st.write('-'*50)
        st.markdown('''Observamos que según silueta el numero de clusters optimos es 3 y según calinski harabasz es 8.
                    Por lo tanto, realizamos un estudio para ambos valores.''')
    col_clust1,col_clust2=st.columns(2)
    with col_clust1:
        st.header('Clustering con 3 clusters')
        k_val=3
        kmeans = KMeans(n_clusters=k_val, n_init= 'auto', random_state=10, max_iter=3000)
        Y_pred=kmeans.fit_predict(data_cluster) # Vector de asignación de etiquetas predichas para cada elemento
        data_cluster['id_cluster']=kmeans.labels_
        #Boxplot con el comportamiento de los clusters para cada variable (Facilitar la caracterización)
        for col in data_cluster.columns:
            fig, ax = plt.subplots(figsize=(10,5))
            sns.boxplot(data_cluster,x=col,hue='id_cluster',ax=ax)
            st.pyplot(fig)
        st.bar_chart(data_cluster['id_cluster'].value_counts().reset_index(),x='id_cluster',y='count')
        st.markdown('''Conclusiones:  
- Uno de los cluster es considerablemente más grande que los otros dos.
- Existe un apartamento con caracteristicas muy diferentes al resto.''')
        
    with col_clust2:
        st.header('Clustering con 8 clusters')
        k_val=8
        kmeans = KMeans(n_clusters=k_val, n_init= 'auto', random_state=10, max_iter=3000)
        Y_pred=kmeans.fit_predict(data_cluster) # Vector de asignación de etiquetas predichas para cada elemento
        data_cluster['id_cluster']=kmeans.labels_
        #Boxplot con el comportamiento de los clusters para cada variable (Facilitar la caracterización)
        for col in data_cluster.columns:
            fig, ax = plt.subplots(figsize=(10,5))
            sns.boxplot(data_cluster,x=col,hue='id_cluster',ax=ax)
            st.pyplot(fig)
        st.bar_chart(data_cluster['id_cluster'].value_counts().reset_index(),x='id_cluster',y='count')
        st.markdown('''Conclusiones:
- FALTA CARACTERIZAR BIEN LOS CLUSTERS!!!                   
- Existe un problema con el desbalanceo de tamaño de los clusters.
- Uno de los grupos de corresponde a apartamentos con un precio medio mas elevado que el resto y cuya capacidad de huéspedes es considerablemente superior al resto, este
grupo de apartamentos además cuentan con todas las comodidades posibles (Wifi,Mascotas,Piscina...).
- El resto de grupos tienen caracteristicas muy similares entre ellos.''')
    

    

data_apart=pd.read_csv('Dataset_Apart/Cleaned/DatasetAirbnb_Cleaned_v1.csv')
st.markdown("<h1 style='text-align: center;'>Eda del dataset Apartamentos</h1>", unsafe_allow_html=True)
st.markdown('---')

col1,col2,col3=st.columns(3)
with col1:
    st.button('Información general del dataset',key='gen')
with col2:
    st.button('Análisis de precios',key='price')
with col3:
    st.button('Clustering',key='cluster')

if st.session_state.gen:
    eda_clean_apart(data_apart)

if st.session_state.price:
    price_part(data_apart)

if st.session_state.cluster:
    clustering(data_apart)