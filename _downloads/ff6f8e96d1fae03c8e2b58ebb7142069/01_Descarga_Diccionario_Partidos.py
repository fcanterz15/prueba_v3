#####################################################
# Importación y carga de librerías
#####################################################

import pandas as pd
import numpy as np
import time
import requests
import json
from funciones_auxiliares import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

#####################################################
# Inicialización de variables
#####################################################

# Inicialización de la url de ACB para realizar la descarga
url = 'https://jv.acb.com/es'

# Inicialización de css de los depegables de temporada / competicion / jornada
css_temporada = 'body > article > div > div.sc-subwrap > div.sc > div.sc-opts > form > div.sc-opts-filter-prin > div.sc-opts-filter.sc-opts-filter--season > div > select'
css_competicion = 'body > article > div > div.sc-subwrap > div.sc > div.sc-opts > form > div.sc-opts-filter-prin > div.sc-opts-filter.sc-opts-filter--competition > div > select'
css_jornada = 'body > article > div > div.sc-subwrap > div.sc > div.sc-opts > form > div.sc-opts-filter-prin > div.sc-opts-filter.sc-opts-filter--round > div.sc-opts-filter-cnt > select'

# Ruta al archivo donde guardarás el diccionario
ruta_archivo = 'E:/TFM/02. Datos/Trabajo/01. Diccionarios/01_Diccionario_partidos.json'

#####################################################
# Ejecución
#####################################################

# 1. Se realizar la conexión de webdrives y se abre la página a la que apuntar
driver = webdriver.Chrome(executable_path='E:\Documentos\Selenium\chromedriver.exe')
driver.get(url)
time.sleep(5)

# 2. Se obtienen la temporadas a descargar y se elimina la que está en curso
l_temporada = obtener_valores_despegable(driver, css_temporada)
l_temporada = l_temporada[1:][::-1]
print(l_temporada)

# 3. Se realiza la descarga de partidos
# Se inicializa el diccionario final
diccionario_final = {}


for temporada in l_temporada:
    print(temporada)
    # Selección de temporada en el despegable
    seleccionar_despeglable(driver, css_temporada, temporada)
    time.sleep(1)
    
    # 3. Selección de valores de la jornada
    l_jornada = obtener_valores_despegable(driver, css_jornada)
    l_jornada = l_jornada[::-1]
    
    for jornada in l_jornada:
        time.sleep(1)
        
        # Selección de temporada en el despegable
        seleccionar_despeglable(driver, css_jornada, jornada)
        time.sleep(3)
        
        # Obtención de partidos de la jornada
        class_url_partido = 'sc-match__live'
        l_partidos = obtener_href_partidos(driver, class_url_partido)
        
        if temporada not in diccionario_final:
            diccionario_final[temporada] = {}
        diccionario_final[temporada][jornada] = l_partidos  

driver.close()

# 4. Se realiza el guardado del diccionario en formato JSON
with open(ruta_archivo, 'w') as archivo:
    json.dump(diccionario_final, archivo)

print(f'Diccionario guardado en {ruta_archivo}')