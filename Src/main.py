from webapp.webapp import App
import streamlit as st
st.set_page_config(page_title='Recomendador de Airbnb', page_icon='🏠', layout='wide',
                   initial_sidebar_state='collapsed')
app=App()