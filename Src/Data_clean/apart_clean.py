
#   IMPORTACION DE PAQUETES
import pandas as pd
import re
import numpy as np
import undetected_chromedriver as uc
from progress.bar import ChargingBar
from geopy.geocoders import Nominatim
from sklearn.impute import SimpleImputer


def ubi(x):
    """
    Funcion encargada de procesar la informacion de la localización.

    Args:
        x (Fila): Fila del dataframe con la información de la localizacion

    Returns:
        Fila: Informacion procesada de la localización
    """
    try:
        dic={}
        e=x.find('España') if x.find('España')!=-1 else 1e10
        p=x.find('Portugal') if x.find('Portugal')!=-1 else 1e10
        f=x.find('Francia') if x.find('Francia')!=-1 else 1e10

        dic[e]='España'
        dic[p]='Portugal'
        dic[f]='Francia'


        if e==p==f:
            return np.nan
        else:
            minimo=min(e,p,f)

            return x.split(dic[minimo])[0] + dic[minimo]
    except:
        return np.nan
    

def transform(data):
    """
    Funcion encargada del preprocesamiento de los datos en crudo.

    Args:
        data (DataFrame): Dataframe con los datos de los apartamentos en crudo.

    Returns:
        DataFrame: DataFrame con los datos procesados.
    """
    #Patterns de extraccion de informacion
    #-----
    patt=r'([0-9]+\xa0viajeros)'
    patt_hue=r'([0-9]+\xa0huéspedes)'
    patt_camas=r'([0-9]+\scama[s]?)'
    patt_ban=r'([0-9]+\sbaño[s]?)'
    patt_drom=r'([0-9]+\sdormitorio[s]?)'

    #Procesamiento del dataframe
    #-----
    data['Evaluaciones']=data['Evaluaciones'].str.replace(' evaluaciones','').str.replace('\xa0evaluaciones','').astype(float)
    data['Precio']=data['Precio'].str.replace('€','').astype(float)
    data['Limpieza']=data['Limpieza'].str.replace('Limpieza','').str.replace(',','.').astype(float)
    data['Veracidad']=data['Veracidad'].str.replace('Veracidad','').str.replace(',','.').astype(float)
    data['Llegada']=data['Llegada'].str.replace('Llegada','').str.replace(',','.').astype(float)
    data['Comunicacion']=data['Comunicacion'].str.replace('Comunicación','').str.replace(',','.').astype(float)
    data['Ubicacion']=data['Ubicacion'].str.replace('Ubicación','').str.replace(',','.').astype(float)
    data['Calidad']=data['Calidad'].str.replace('Calidad','').str.replace(',','.').astype(float)

    #Extraccion de informacion del apartamento
    #----------
    data['Capacidad']=data['Informacion'].apply(lambda x:re.findall(patt,x)[0] if len(re.findall(patt,x))>0 else re.findall(patt_hue,x)[0] if len(re.findall(patt_hue,x))>0 else np.nan)
    data['Capacidad']=data['Capacidad'].str.replace('\xa0viajeros','').str.replace('\xa0huéspedes','').astype(float)
    data['Camas']=data['Informacion'].apply(lambda x: re.findall(patt_camas,x)[0] if len(re.findall(patt_camas,x)) else np.nan)
    data['Camas']=data['Camas'].str.replace(' camas','').str.replace(' cama','').astype(float)
    data['Baños']=data['Informacion'].apply(lambda x: re.findall(patt_ban,x)[0] if len(re.findall(patt_ban,x)) else np.nan)
    data['Baños']=data['Baños'].str.replace(' baños','').str.replace(' baño','').str.replace('\xa0baños','').astype(float)
    data['Dormitorios']=data['Informacion'].apply(lambda x: re.findall(patt_drom,x)[0] if len(re.findall(patt_drom,x)) else np.nan)
    data['Dormitorios']=data['Dormitorios'].str.replace(' dormitorios','').str.replace(' dormitorio','').astype(float)
    data['Baño Compartido']=data['Informacion'].apply(lambda x: 1 if x.find('Baño compartido')!=-1 else 0)

    #Extraccion de datos de los servicios
    #------------
    data['Wifi']=data['Servicios'].str.contains('Wifi').astype(float)
    data['Mascotas']=data['Servicios'].str.contains('Admite mascotas').astype(float)
    data['Piscina']=data['Servicios'].str.contains('Piscina').astype(float)
    data['Parking']=data['Servicios'].str.contains('Aparcamiento gratuito').astype(float)

    #Corrección de la localización
    #-----------
    data['Localizacion']=data['Localizacion'].apply(lambda x: ubi(x))

    #Eliminacion de columnas sobrantes
    #-----------
    data.drop(['Informacion','Servicios'],axis=1,inplace=True)
    def lat_log(l):
        geolocator = Nominatim(user_agent="España")
        try:
            location = geolocator.geocode(l)
            latitude = location.latitude
            longitude = location.longitude
            return latitude, longitude
        except:
            return 10000,10000
    data['Latitud_Longitud']=data['Localizacion'].apply(lambda x: lat_log(x))
    data['Latitud']=data['Latitud_Longitud'].apply(lambda x: x[0])
    data['Longitud']=data['Latitud_Longitud'].apply(lambda x: x[1])
    data.drop('Latitud_Longitud',axis=1,inplace=True)
    imputer = SimpleImputer(strategy='mean')
    imputer_cat = SimpleImputer(strategy='most_frequent')
    cols_cat=['Wifi','Mascotas','Piscina','Parking']
    columnas_categoricas=data.select_dtypes(include='object').columns
    not_cat=[col for col in data.columns if col not in cols_cat and col not in list(set(columnas_categoricas).union(set(cols_cat)))]
    data[cols_cat]=imputer_cat.fit_transform(data[cols_cat])
    data[not_cat]=imputer.fit_transform(data[not_cat])
    
    return data

class ManualImputer():
    """
    Clase encargada de la imputacion de valores nulos de forma manual por parte del usuario.
    """

    def __init__(self,dataframe):
        
        self.airbnb='https://www.airbnb.es'
        self.data=dataframe
    
    def iniciar_wd(self,headless=False):
        """
        Función encargada de arrancar el Webdriver de Google Chrome.

        Args:
            headless (bool, optional): True abre una pestaña visual del navegador

        Returns:
            driver: Objeto interactuable de selenium (Navegador)
        """
        options=uc.ChromeOptions()
        options.add_argument('--password-store=basic')
        options.add_experimental_option(
            'prefs',
            {'credentials_enable_service':False,
            'profile.password_manager_enabled':False}
        )
        if headless:
            options.add_argument('--headless')

        #Iniciamos el driver
        driver=uc.Chrome(options=options,headless=headless,log_level=3)
        driver.maximize_window()
        
        return driver
    
    def value_impute(self,col,driver,tipo):
        """
        Funcion encargada de iterar sobre los valores nulos solicitando el valor a introducir a el usuario

        Args:
            col (string): Nombre de la columna
            driver (WebDriver): Webdriver de googleChrome
            tipo (type): Tipo de dato correspondiente a la columna
        """
        try:
            indices_nulos = self.data[self.data[col].isnull()].index

            bar2 = ChargingBar('\nRellenando Huecos:', max=len(indices_nulos))
            for ind in indices_nulos:
                bar2.next()
                driver.get(self.data.at[ind,'URL'])

                value=tipo(input(f'\nIntroduce el valor para la columna {col}: '))
                
                self.data.at[ind,col]=value
            
            bar2.finish()
        
        except:
            print('La columna indicada no existe')
        pass

    def manual_imputer(self,columnas):
        """
        Funcion encargada de la iteracion sobre los pares columna: tipo de dato

        Args:
            columnas (dict): Diccionario con el nombre de las columnas como clave y el tipo de dato como valore

        Returns:
            pd.DataFrame: DataFrame con la imputacion de valores nulos 
        """
        driver=self.iniciar_wd()
        for col,tipo in columnas.items():
            self.value_impute(col,driver,tipo)
        
        return self.data
    


if __name__=='__main__':

    ruta_dataset='../../Dataset_Apart/Raw/DatasetAirbnb_v1.csv'

    version=1.2

    data=pd.read_csv(ruta_dataset)

    data=transform(data)

    #   Hacemos la imputacion manual en caso de ser necesaria
    #columnas={'Precio':float}
    #imputer=ManualImputer(data)
    #data=imputer.manual_imputer(columnas)


    data.to_csv(f'../../Dataset_Apart/Cleaned/DatasetAirbnb_Cleaned_v{version}.csv',index=False)

    separator_line = '-' * 50
    text = "Limpieza completa"
    text_centered = text.center(len(separator_line))
    print(f"\n{separator_line}\n{text_centered}\n{separator_line}\n")