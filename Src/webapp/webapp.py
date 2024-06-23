import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
from st_clickable_images import clickable_images
from env.env import *

class App():
    def __init__(self) -> None:
        self.lat_bar()


    def lat_bar(self):
        home_page = st.Page("webapp/home.py", title="Home", icon=":material/home:")
        eda_page = st.Page("webapp/eda.py", title="EDA", icon=":material/add_circle:")
        limp_page = st.Page("webapp/clean.py", title="Limpieza", icon=":material/delete:")

        pg = st.navigation([home_page,eda_page, limp_page])
        pg.run()





    