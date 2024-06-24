import streamlit as st
import pandas as pd
from Data_clean.apart_clean import transform
import pandas as pd

def clean_pipeline(data):
    datos=pd.read_csv(data,index_col=0)
    datos=transform(datos)
    st.subheader('Datos limpios ya procesados:')
    data=st.dataframe(datos,column_config={'ID':None})
    st.download_button('Descargar datos',datos.to_csv(index=False),'data.csv')
    

st.markdown("<h1 style='text-align: center;'>Generador de dataset Airbnb</h1>", unsafe_allow_html=True)
st.markdown('---')
uploaded_file = st.file_uploader("Sube tu dataset generado")
if uploaded_file is not None:
    # Process the uploaded file
    data = clean_pipeline(uploaded_file)
