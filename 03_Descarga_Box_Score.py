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
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

#####################################################
# Inicialización de variables
#####################################################

# Se inicializa el css de la cabecera del partido
css_cabecera = 'body > article > div > div.ge-cnt-body > div.he-wrap > div.he'

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
            url_partido = obtener_url_final(partido, 'resumen', 'estadisticas/ficha')
            # Inicialización del driver 
            driver = webdriver.Chrome(executable_path='E:\Documentos\Selenium\chromedriver.exe')    
            driver.get(url_partido)
            
            # Se realiza la obtención de la fecha del partido, equipo local y visitante
            fecha_partido, team_local, team_visitante = obtener_nombres_fecha(driver, css_cabecera)

            # Se realiza la lectura del box score del equipo local
            hacer_clic_en_boton(driver, css_button_local)
            bs_equipo_local = obtener_box_score(driver, css_table)

            # Se realiza la lectura del box score del equipo visitante
            hacer_clic_en_boton(driver, css_button_visitante)
            bs_equipo_visitante = obtener_box_score(driver, css_table)
            
            # Se realiza la creación de la carpeta de guardado
            partido_name = fecha_partido + '_' + team_local + '_VS_' + team_visitante
            ruta_partido = ruta_guardado + '/' + temporada + '/' + jornada + '/' + partido_name
            os.makedirs(ruta_partido)
            
            # Se realiza el guardado de los boxscores
            bs_equipo_local.to_csv(ruta_partido + '/' + team_local + '.csv', sep = ';', index=False)
            bs_equipo_visitante.to_csv(ruta_partido + '/' + team_visitante + '.csv', sep = ';', index=False)
            
            driver.quit()  

              