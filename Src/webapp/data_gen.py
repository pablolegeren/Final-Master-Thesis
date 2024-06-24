from Obt_data.data import *
import streamlit as st




st.markdown("<h1 style='text-align: center;'>Generador de dataset Airbnb</h1>", unsafe_allow_html=True)
st.markdown('---')

col1,col2=st.columns([.7,.3])

with col1:
    st.session_state.maximo=st.number_input('Número de registros',min_value=0,value=0,key='n_reg')
    data_version=st.number_input('Versión del dataset',min_value=0,value=0,key='n_vers')
    tipos_elegidos=st.multiselect('Tipo de apartamento',options=['A pie de playa', 'Casas rurales','Cabañas'],key='tipos')
    coments=st.checkbox('Mostrar comentarios',key='coments')
    datagen_class=GenerateDataSet(tipos_elegidos)
    if st.button('Generar dataset',key='gen'):
        if st.session_state.maximo>0:
            urls=datagen_class.apart_urls(max_apart=st.session_state.maximo)
        else:
            urls=datagen_class.apart_urls()
        result=datagen_class.apart_info(data_version,urls)
        st.write('Info Apartamentos generados:')
        st.dataframe(result)
        if coments:
            data_coments=datagen_class.apart_val(urls)
            st.write('Comentarios:')
            st.dataframe(data_coments)


with col2:
    st.subheader('Requerimientos')
    st.markdown('- Google Chrome instalado en el sistema y como navegador por defecto.')
    st.markdown('- Ejecutar la aplicacion en local.')