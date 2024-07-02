
#   IMPORTACION DE PAQUETES
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import json
import re
from progress.bar import ChargingBar

class GenerateDataSet():
    """
    Clase para la generación de los datasets de Comentarios y de Apartamentos en funcion del tipo de apartamento.
    """
    def __init__(self,tipos):
        """_summary_

        Args:
            tipos (_type_): _description_
        """
        self.url_airbnb='https://www.airbnb.es'
        self.tipos=tipos
        self.pat_limp=r'^(Limpieza)[0-9],[0-9]$'
        self.pat_ver=r'^(Veracidad)[0-9],[0-9]$'
        self.pat_lleg=r'^(Llegada)[0-9],[0-9]$'
        self.pat_com=r'^(Comunicación)[0-9],[0-9]$'
        self.pat_ub=r'^(Ubicación)[0-9],[0-9]$'
        self.pat_cal=r'^(Calidad)[0-9],[0-9]$'
        self.pattern_eval=r'^[0-9]+\s(evaluaciones)$'
        self.pattern_price=r'[0-9]+\s(€)\s$'
        self.claves = ["ID", "Titulo", "Descripcion Simple", "Informacion", "Evaluaciones", "Tipo", "Precio", "URL", 
                    "Limpieza", "Veracidad", "Llegada", "Comunicacion", "Ubicacion", "Calidad", 
                    "Servicios", "Localizacion"]
        self.claves_eval=['name','imagen','user_id','valoracion','comentario','apart_id','ubicacion']

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
    
    def get_url(self,tipos,max_apart=None):
        """
        Función encargada de obtener las urls de los apartamentos en función del tipo de apartamento.

        Args:
            tipos (list): Lista con los tipos de apartamentos a extraer (p.ej: A pie de playa).

        Returns:
            result (dict): 
                - keys -> Tipos de apartamentos.
                - values -> Lista con las urls.
        """

        driver=self.iniciar_wd()
        driver.get(self.url_airbnb)
        time.sleep(15)  #Espera mientras clicamos por primera vez el boton de mostrar mas
        total_urls=0

        result={}
        for o in tipos:
            # Buscar el elemento que contiene el texto
            driver.find_element(By.XPATH,f"//*[contains(text(), '{o}')]").click()
            time.sleep(2)

            scroll_height = driver.execute_script("return document.body.scrollHeight;")
            actions = ActionChains(driver)

            # Hacer scroll hasta el final de la página
            driver.execute_script(f"window.scrollTo(0, {scroll_height});")
            actions.send_keys(Keys.PAGE_UP).perform()
            time.sleep(3)

            for i in range(6):
                actions.send_keys(Keys.PAGE_UP).perform()
                time.sleep(.5)
            time.sleep(5)
            
            for b in driver.find_elements(By.XPATH,f"//button"):
                try:
                    if b.text.find('Mostrar más')!=-1:
                        b.click()
                        print('HA ENCONTRADO EL BOTON!!')
                except:
                    print('NO TIENE ATRIBUTO TEXT')
            time.sleep(3)

            for i in range(120):
                actions.send_keys(Keys.PAGE_DOWN).perform()
                time.sleep(.1)
            time.sleep(2)
            
            soup=BeautifulSoup(driver.page_source, 'html.parser')
            res=[]
            for u in soup.find_all('a'):
                en=u.get('href')
                
                if en.find('/rooms')!=-1:
                    res.append(f'https://www.airbnb.es{en}')
                    total_urls+=1
            result[o]=list(set(res))[:max_apart]
        
        driver.close()
        return result
    
    def apart_urls(self,max_apart=None):
        """
        Función encargada de la generación del archivo con las urls de los apartamentos.
        """
        res=self.get_url(self.tipos,max_apart=max_apart)
        return res


    def get_info_apart(self,url,driver):
        """
        Funcion encarga de extraer la informacion de un apartamento a partir de su url

        Args:
            url (string): Url del apartamento

        Returns:
            _type_: _description_
        """
        driver.get(url)
        time.sleep(3)

        tit=desc_s=info=evaluaciones=precio=limp=vera=lleg=com=ub=cal=serv=local=''
        
        html=driver.page_source
        soup=BeautifulSoup(html, 'html.parser')
        try:
            tit=soup.find('h1').text
        except:
            pass
        try:
            desc_s=soup.find('h2').text
        except:
            pass
        
        try:
            info=soup.find('ol').text
        except:
            pass

        try:

            #Bucle de extraccion de Precio y Nº de evaluaciones
            #----------------
            ev=soup.find_all('span')
            evalu=price=0
            for e in ev:
                if len(re.findall(self.pattern_eval,e.text))>0 and evalu==0:
                    evaluaciones=e.text
                    evalu+=1
                    
                if len(re.findall(self.pattern_price,e.text))>0 and price==0:
                    precio=e.text
                    price+=1

                if price==1 and evalu==1:
                    break
            
            #Bucle de extraccion de valoraciones en Limpieza, Veracidad, LLegada, Comunicacion, Ubicacion y Calidad
            #-----------
            divs=soup.find_all('div')
            for d in divs:
                if len(re.findall(self.pat_limp,d.text))>0:
                    limp=d.text
                elif len(re.findall(self.pat_ver,d.text))>0:
                    vera=d.text
                elif len(re.findall(self.pat_lleg,d.text))>0:
                    lleg=d.text
                elif len(re.findall(self.pat_com,d.text))>0:
                    com=d.text
                elif len(re.findall(self.pat_ub,d.text))>0:
                    ub=d.text
                elif len(re.findall(self.pat_cal,d.text))>0:
                    cal=d.text
                else:
                    pass
        except:
            pass
        
        #Bucle de extraccion de características (p.ej Wifi) y informacion de la ubicacion
        #---------------
        sps=soup.find_all('section')
        se=lo=0
        for s in sps:
            if s.text.find('¿Qué hay en este alojamiento?')!=-1 and se==0:
                serv=s.text[len('¿Qué hay en este alojamiento?'):]
                se+=1
            
            if s.text.find('¿Dónde me voy a quedar?')!=-1 and lo==0:
                local=s.text[len('¿Dónde me voy a quedar?'):]
                lo+=1

            if se==1 and lo==1:
                break
            
        return tit,desc_s,info,evaluaciones,precio,limp,vera,lleg,com,ub,cal,serv,local
    
    def apart_info(self,version,data):
        """_summary_
        """
        try:
            
            driver=self.iniciar_wd(headless=True)
            
            self.datos = {clave:[] for clave in self.claves}
            total=0
            for k in data.keys():
                total+=len(data[k])

            bar2 = ChargingBar('\nObteniendo Info:', max=total)

            #Bucle de extraccion de informacion a partir de cada url
            for k in data.keys():
                for url in data[k]:
                    bar2.next()
                    a,b,c,d,f,g,h,i,j,l,m,n,o=self.get_info_apart(url,driver)
                    nuevo_id = hash(url)
                    nuevos_datos = [nuevo_id, a, b, c, d, k, f, url, g, h, i, j, l, m, n, o]

                    for clave, dato in zip(self.claves, nuevos_datos):
                        self.datos[clave].append(dato)
            
            #Guardamos la informacion en un csv
            result=pd.DataFrame(self.datos,columns=self.claves)
            bar2.finish()     
            driver.close()
            print('FINALIZADO!!')
            return result
        except:
            print('No se ha encontrado el archivo urls.json')
    
    def get_val_apart(self,driver,url,data):
        """_summary_

        Args:
            driver (_type_): _description_
            url (_type_): _description_
            data (_type_): _description_

        Returns:
            _type_: _description_
        """

        driver.get(url)
        time.sleep(1)
        actions = ActionChains(driver)
        for i in range(10):
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(.5)
            try:
                boton = driver.find_element(By.XPATH,"//button[contains(text(), 'Mostrar las') and contains(text(), 'evaluaciones')]")
                break
            except:
                pass
        time.sleep(1)
        try:
            boton = driver.find_element(By.XPATH,"//button[contains(text(), 'Mostrar las') and contains(text(), 'evaluaciones')]")
            # Hacer clic en el botón
            boton.click()

            last_element = driver.find_element(By.XPATH,'//div[@data-testid="pdp-reviews-modal-scrollable-panel"]')
            last_element.click()
            for i in range(150):
                actions.send_keys(Keys.PAGE_DOWN).perform()
                time.sleep(.05)

            soup=BeautifulSoup(driver.page_source,'html.parser')
            revs=soup.find_all('div', {'data-review-id': True})
            apart_id=url
            for r in revs:
                try:
                    ubi_div=r.find('div', id=lambda value: value and 'review' in value)
                    ubi=ubi_div.find('div').text
                    try:
                        name=r.find_all('h2')[0].text
                    except:
                        name=''
                    photo=r.find_all('img')[0].get('src')
                    id_user=hash(photo)
                    val=r.find_all('span')[0].text

                    if len(r.find_all('span')[3].text)>25:
                        coment=r.find_all('span')[3].text
                    elif len(r.find_all('span')[4].text)>25:
                        coment=r.find_all('span')[4].text
                    elif len(r.find_all('span')[5].text)>25:
                        coment=r.find_all('span')[5].text
                    else:
                        coment=''

                    data['name'].append(name)
                    data['imagen'].append(photo)
                    data['user_id'].append(id_user)
                    data['valoracion'].append(val)
                    data['comentario'].append(coment)
                    data['apart_id'].append(url)
                    data['ubicacion'].append(ubi)
                    print('ID_apart: ',data['apar_id'])
                except:
                    pass
            data.to_csv(f'../../Dataset_Review/Raw/CommentDataset_v{version}.csv',index=False)
        except:
            pass
        
        return data
    
    def apart_val(self,data):
        """_summary_
        """

        driver=self.iniciar_wd()

        total=0
        for k in data.keys():
            total+=len(data[k])

        bar3 = ChargingBar('\nObteniendo Info de Comentarios:', max=total)
        
        datos={clave:[] for clave in self.claves_eval}

        for k in data.keys():
            for url in data[k]:
                bar3.next()
                datos=self.get_val_apart(driver,url,datos)
                print(datos)
                print('Dataframe: ',pd.DataFrame(datos,columns=self.claves_eval))
                data_inter=pd.DataFrame(datos,columns=self.claves_eval).to_csv('/Users/mariolamas/Desktop/Social-Network-Analysis/Dataset_Review/Raw/CommentDataset_v2.csv')
        bar3.finish() 
        data=pd.DataFrame(datos,columns=self.claves_eval)
        driver.close()
        return data

if __name__=='__main__':

    tipos=['A pie de playa', 'En el campo','Cabañas']
    dataset=GenerateDataSet(tipos)

    #Generamos el archivo de urls
    #------
    #res = dataset.apart_urls()    #Comenta esta linea si ya tienes un archivo url.json en este directorio
    #with open('urls.json','w') as jsonfile:
        #json.dump(res,jsonfile)
    #jsonfile.close()
    #Generamos el dataset de informacion de apartamentos
    #------
    with open('urls.json','r') as jsonfile:
        data=json.load(jsonfile)
    version=3
    #result=dataset.apart_info(version=version,data=data)
    #result.to_csv(f'DatasetAirbnb_v{version}.csv',index=False)

    #Generamos el dataset de comentarios
    #-------
    data=dataset.apart_val(data)
    data.to_csv(f'../../Dataset_Review/Raw/CommentDataset_v{version}.csv',index=False)
