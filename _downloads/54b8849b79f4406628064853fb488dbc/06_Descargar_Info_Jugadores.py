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
url = 'https://www.acb.com/club/index/temporada_id/'

# Se inicializa el listado de temporadas a leer
l_temporadas = ['2019', '2020', '2021', '2022']

# Se inicializa el diccionario de almacenamiento
diccionario_plantillas = {}

# Se inicializa el css para enlistar las tablas
css_boton_lista = '#boton_cuerpo_plantilla_vista_listado'

# Se inicializan las tablas de información de jugadores
css_plantilla = 'body > div.contenedora.ui-helper-clearfix > div > section > div > section > section > section > div > table:nth-child(1)'
css_cantera = 'body > div.contenedora.ui-helper-clearfix > div > section > div > section > section > section > div > table:nth-child(2)'
css_bajas = 'body > div.contenedora.ui-helper-clearfix > div > section > div > section > section > section > div > table.roboto.defecto.tabla_plantilla.plantilla_bajas.clasificacion.tabla_ancho_completo'

# Se inicializa el css de la información del jugador
css_info_jugador = 'body > div.contenedora.ui-helper-clearfix > div > section > div > section > header > div > div.datos > div.f-l-a-100.contenedora_datos_basicos'

# Ruta al archivo donde guardarás el diccionario
ruta_archivo = 'E:/TFM/02. Datos/Trabajo/01. Diccionarios/02_Diccionario_plantillas.json'

######################################################
# EJECUCIÓN
######################################################

for temporada in l_temporadas:
    
    # Se inicializa el driver para realizar las búsquedas
    driver = webdriver.Chrome(executable_path='E:\Documentos\Selenium\chromedriver.exe')    

    # Se construye la url de la temporada
    url_temporada = url + temporada

    # Se obtiene la url de la temporada
    driver.get(url_temporada)
    
    # Se inicializa la temporada en el diccionario
    diccionario_plantillas[temporada] = {}
    
    # Se realiza la búsqueda de la información de los clubes
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    listado_clubes = soup.find('div', class_='listado_clubes')
    club_elements = listado_clubes.find_all('article', class_='club')
    
    # Se recorre el listado de clubs que componen el año
    for club in club_elements:
        # Se extrae el nombre del club y la url de este
        h4_element = club.find('h4', class_='nombre')
        club_name = h4_element.text.strip()
        club_href = h4_element.find('a')['href']

        # Se inicializa el club en el diccionario en la temporada
        diccionario_plantillas[temporada][club_name] = {}
        # Se añade la url del equipo
        diccionario_plantillas[temporada][club_name]['url_equipo'] = club_href
    
    # Se realiza el cierre del driver
    driver.quit()
    
for temporada in l_temporadas:
    
    # Se obtiene el listado de equipos de una temporada
    l_equipos = list(diccionario_plantillas[temporada].keys())
    
    for equipo in l_equipos:
        
        # Se construye la url de la plantilla
        url_equipo = diccionario_plantillas[temporada][equipo]['url_equipo']
        url_plantilla = 'https://www.acb.com' + url_equipo + '/temporada_id/' + temporada
        url_plantilla = url_plantilla.replace('/plantilla/', '/plantilla-lista/')
        
        # Se inicializa la página
        driver = webdriver.Chrome(executable_path='E:\Documentos\Selenium\chromedriver.exe') 
        driver.get(url_plantilla)
                
        # Se obtienen los diccionarios de jugadores
        dicc_plantilla = obtener_dicc_plantilla(driver,css_plantilla,'dorsal primero roboto_bold')
        dicc_cantera = obtener_dicc_plantilla(driver,css_cantera,'dorsal primero roboto_bold')
        dicc_bajas = obtener_dicc_plantilla(driver,css_bajas,'dorsal roboto_bold')
        
        dicc_plantilla.update(dicc_cantera)
        dicc_plantilla.update(dicc_bajas)
        
        diccionario_plantillas[temporada][equipo]['plantilla'] = dicc_plantilla
        # Se realiza el cierre del driver
        driver.quit()

for temporada in l_temporadas:
    
    # Se obtiene el listado de equipos de una temporada
    l_equipos = list(diccionario_plantillas[temporada].keys())
    
    for equipo in l_equipos:
        
        # Se obtiene el listado de jugadores del equipo
        l_jugadores = list(diccionario_plantillas[temporada][equipo]['plantilla'].keys())
        
        for jugador in l_jugadores:
            # Se realiza la apertura del driver del jugador
            url_jugador = diccionario_plantillas[temporada][equipo]['plantilla'][jugador]['url_jugador']
            url_jugador = 'https://www.acb.com' + url_jugador
            driver = webdriver.Chrome(executable_path='E:\Documentos\Selenium\chromedriver.exe') 
            driver.get(url_jugador)

            # Intenta encontrar la tabla usando el selector CSS
            tabla = driver.find_element_by_css_selector(css_info_jugador)
            tabla_html = tabla.get_attribute('outerHTML')
            soup = BeautifulSoup(tabla_html, 'html.parser')

            # Se obtiene la posición del jugador
            elemento_posicion = soup.find('div', class_='datos_basicos posicion roboto_condensed')
            posicion = elemento_posicion.find('span', class_='roboto_condensed_bold').text.strip()

            # Se obtiene la altura del jugador
            elemento_altura = soup.find('div', class_='datos_basicos altura roboto_condensed')
            altura = elemento_altura.find('span', class_='roboto_condensed_bold').text.strip()

            diccionario_plantillas[temporada][equipo]['plantilla'][jugador]['Altura'] = altura
            diccionario_plantillas[temporada][equipo]['plantilla'][jugador]['Posición'] = posicion

            driver.quit()

                
######################################################
# GUARDADDO
######################################################

with open(ruta_archivo, 'w') as archivo:
    json.dump(diccionario_plantillas, archivo)

print(f'Diccionario guardado en {ruta_archivo}')            