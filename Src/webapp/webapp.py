import streamlit as st
from env.env import *

class App():
    def __init__(self) -> None:
        self.lat_bar()


    def lat_bar(self):
        home_page = st.Page("webapp/home.py", title="Home", icon=":material/home:")
        eda_page = st.Page("webapp/eda.py", title="EDA", icon=":material/add_circle:")
        limp_page = st.Page("webapp/clean.py", title="Limpieza", icon=":material/delete:")
        data_gen_page= st.Page("webapp/data_gen.py", title="Generación de datos", icon=":material/emoji_people:")

        pg = st.navigation([home_page,eda_page, limp_page,data_gen_page])
        pg.run()





    