#####################################################
# Importación y carga de librerías
#####################################################

import pandas as pd
import numpy as np
import time
import requests
import json
import os
import re
from datetime import datetime
from funciones_auxiliares import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


#####################################################
# Inicialización de variables
#####################################################

# Se inicializa el css de la cabecera del partido
css_cabecera = 'body > article > div > div.ge-cnt-body > div.he-wrap > div.he'
css_scroll = 'body > article > div > div.ge-cnt-body > div.ge-cnt-body-bottom > div'
css_height = 'body > article > div > div.ge-cnt-body > div.ge-cnt-body-bottom > div'

# Se inicializa el css de la tabla de box_score para su lectura
css_table = 'body > article > div > div.ge-cnt-body > div.ge-cnt-body-bottom > div > div.ta-wrap > table'

# Se inicializan los csspara los botones de los equipos en la lectura de box score
css_button_local = 'body > article > div > div.ge-cnt-body > div.ge-cnt-body-bottom > div > div.bs-head > div.bs-head-shield-wrap > div:nth-child(1)'
css_button_visitante = 'body > article > div > div.ge-cnt-body > div.ge-cnt-body-bottom > div > div.bs-head > div.bs-head-shield-wrap > div:nth-child(2)'

# Ruta al archivo donde se guarda el diccionario
ruta_archivo = 'E:/TFM/02. Datos/Trabajo/01. Diccionarios/01_Diccionario_partidos.json'

# Ruta de la carpeta de creación de carpetas
ruta_guardado = 'E:/TFM/02. Datos/ACB/JORNADAS'

#####################################################
# Ejecución
#####################################################

# Cargar el diccionario desde el archivo JSON
with open(ruta_archivo, 'r') as archivo:
    diccionario_final = json.load(archivo)
    
# Se realiza la obtención de las temporadas a descargar
l_temporadas = list(diccionario_final.keys())

for temporada in l_temporadas:
    
    # Se obtiene las jornadas de la temporada
    l_jornadas = list(diccionario_final[temporada].keys())
    
    for jornada in l_jornadas:
        
        # Se obtiene los partidos de la jornada
        partidos = diccionario_final[temporada][jornada]
        
        for partido in partidos:
            
            # Se obtiene la url del partido y se abre el navegador
            url_partido = obtener_url_final(partido, 'resumen', 'jugadas')
            # Inicialización del driver 
            driver = webdriver.Chrome(executable_path='E:\Documentos\Selenium\chromedriver.exe')    
            driver.get(url_partido)
            
            # Se realiza la obtención de la fecha del partido, equipo local y visitante
            fecha_partido, team_local, team_visitante = obtener_nombres_fecha(driver, css_cabecera)

            # Se realiza el scroll de la pantalla
            realizar_scroll_pantalla(driver,css_scroll,css_height)
            
            # Se realiza la obtención del codigo html de la página tras el scroll
            element = driver.find_element_by_css_selector(css_scroll)
            html = element.get_attribute('outerHTML')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Se realiza la selección de los elementos pp
            pp_elements = soup.find_all(class_='pp-item')   
            
            # Se obtiene el play by play
            pbp_brute = obtener_play_by_play(pp_elements, team_local, team_visitante)
            
            # Se realiza la creación de la ruta
            partido_name = fecha_partido + '_' + team_local + '_VS_' + team_visitante
            ruta_partido = ruta_guardado + '/' + temporada + '/' + jornada + '/' + partido_name
                       
            # Se realiza el guardado de los boxscores
            pbp_brute.to_csv(ruta_partido + '/PBP_' + team_local + '_VS_' + team_visitante + '.csv', sep = ';', index=False)
            
            driver.quit()  

          