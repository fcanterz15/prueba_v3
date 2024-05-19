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

# Inicialización de la url de ACB para realizar la descarga
url = 'https://jv.acb.com/es'

# Inicialización de css de los depegables de temporada / competicion / jornada
css_temporada = 'body > article > div > div.sc-subwrap > div.sc > div.sc-opts > form > div.sc-opts-filter-prin > div.sc-opts-filter.sc-opts-filter--season > div > select'
css_competicion = 'body > article > div > div.sc-subwrap > div.sc > div.sc-opts > form > div.sc-opts-filter-prin > div.sc-opts-filter.sc-opts-filter--competition > div > select'
css_jornada = 'body > article > div > div.sc-subwrap > div.sc > div.sc-opts > form > div.sc-opts-filter-prin > div.sc-opts-filter.sc-opts-filter--round > div.sc-opts-filter-cnt > select'

# Se inicializa el css de la cabecera del partido
css_cabecera = 'body > article > div > div.ge-cnt-body > div.he-wrap > div.he'


css_button_local = 'body > article > div > div.ge-cnt-body > div.ge-cnt-body-bottom > div > div.sm-table.sm-table--local > div.ge-btn.ge-btn'
css_button_visitante = 'body > article > div > div.ge-cnt-body > div.ge-cnt-body-bottom > div > div.sm-table.sm-table--visitor > div.ge-btn.ge-btn'

css_table_local = 'body > article > div > div.ge-cnt-body > div.ge-cnt-body-bottom > div > div.sm-table.sm-table--local > table > tbody'
css_table_visitante = 'body > article > div > div.ge-cnt-body > div.ge-cnt-body-bottom > div > div.sm-table.sm-table--visitor > table > tbody'

css_carta_tiro_local = 'body > article > div > div.ge-cnt-body > div.ge-cnt-body-bottom > div > div.sm-gra-wrap > div.sm-gra > svg > g:nth-child(3)'
css_carta_tiro_visitante = 'body > article > div > div.ge-cnt-body > div.ge-cnt-body-bottom > div > div.sm-gra-wrap > div.sm-gra > svg > g:nth-child(4)'

#####################################################
# Inicialización de variables
#####################################################

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
l_temporadas = [ '2022-2023']    
for temporada in l_temporadas:
    
    # Se obtiene las jornadas de la temporada
    l_jornadas = list(diccionario_final[temporada].keys())
    
    for jornada in l_jornadas:
        
        # Se obtiene los partidos de la jornada
        partidos = diccionario_final[temporada][jornada]
        
        for partido in partidos:
            
            # Se obtiene la url del partido y se abre el navegador
            url_partido = obtener_url_final(partido, 'resumen', 'cartadetiro')
            # Inicialización del driver 
            driver = webdriver.Chrome(executable_path='E:\Documentos\Selenium\chromedriver.exe')    
            driver.get(url_partido)
            time.sleep(2)
            # Se realiza la obtención de la fecha del partido, equipo local y visitante
            fecha_partido, team_local, team_visitante = obtener_nombres_fecha(driver, css_cabecera)

            # Se limpia la carta de tiro despulsando los tiros realizados por ambos equipos
            hacer_clic_en_boton(driver,css_button_local)
            hacer_clic_en_boton(driver,css_button_visitante)
            time.sleep(2)
            # Se obtienen las cartas de tiro de los jugadores del equipo local y visitante
            df_carta_tiro_local = obtener_carta_tiro(driver, css_table_local, css_carta_tiro_local)
            df_carta_tiro_visitante = obtener_carta_tiro(driver, css_table_visitante, css_carta_tiro_visitante)
            
            # Se realiza la creación de la carpeta de guardado
            partido_name = fecha_partido + '_' + team_local + '_VS_' + team_visitante
            ruta_partido = ruta_guardado + '/' + temporada + '/' + jornada + '/' + partido_name
            
            # Se realiza el guardado de los boxscores
            df_carta_tiro_local.to_csv(ruta_partido + '/' + team_local + '_CARTA_TIRO.csv', sep = ';', index=False)
            df_carta_tiro_visitante.to_csv(ruta_partido + '/' + team_visitante + '_CARTA_TIRO.csv', sep = ';', index=False)
            
            driver.quit()  

              