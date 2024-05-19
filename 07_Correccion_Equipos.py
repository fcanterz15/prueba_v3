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
import shutil
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

# Ruta al archivo donde se guarda el diccionario
ruta_dicc_plantillas = 'E:/TFM/02. Datos/Trabajo/01. Diccionarios/02_Diccionario_plantillas.json'
ruta_dicc_partidos = 'E:/TFM/02. Datos/Trabajo/01. Diccionarios/01_Diccionario_partidos.json'

# Ruta de la carpeta de creación de carpetas
ruta_equipos = 'E:/TFM/02. Datos/ACB/EQUIPOS'

# Ruta de la carpeta de descarga de las jornadas
ruta_jornada = 'E:/TFM/02. Datos/ACB/JORNADAS'

#####################################################
# Ejecución
#####################################################

# Cargar el diccionario desde el archivo JSON
with open(ruta_dicc_plantillas, 'r') as archivo:
    diccionario_plantillas = json.load(archivo)
    
# Cargar el diccionario desde el archivo JSON
with open(ruta_dicc_partidos, 'r') as archivo:
    diccionario_partidos = json.load(archivo)    
    
l_temporadas = ['2020']
equipo_old = 'Iberostar Tenerife'
equipo_replace = 'Lenovo Tenerife'


for temporada in l_temporadas:
    
    # Se inicializa la carpeta de la temporada
    ruta_equipos_temporada = ruta_equipos + '/' + temporada
    
    # Se inicializa la ruta de cada una de las jornadas de las temporadas y se construye el listado
    ruta_jornada_temporada = ruta_jornada + '/' + temporada
    l_jornadas = os.listdir(ruta_jornada_temporada)
    
    for jornada in l_jornadas:
        
        # Se obtiene el listado de partidos de la jornada
        ruta_jornada_temporada_partidos = ruta_jornada_temporada + '/' + jornada
        l_partidos = os.listdir(ruta_jornada_temporada_partidos)
        
        # Se extrae el partido que haya jugado el equipo en la jornada
        partido = (list(filter(lambda x: equipo_old in x, l_partidos)))
        
        if len(partido) == 1:
            
            # Se crea el directorio del partido en la carpeta del equipo
            ruta_equipo_partido = ruta_jornada_temporada_partidos + '/' + partido[0]
            
            ficheros = os.listdir(ruta_equipo_partido)
            
            # Se realiza la selección de ficheros
            box_score_equipo = [fichero for fichero in ficheros if equipo_old in fichero and 'CARTA_TIRO' not in fichero and 'PBP' not in fichero][0]
            box_score_rival = [fichero for fichero in ficheros if equipo_old  not in fichero and 'CARTA_TIRO' not in fichero and 'PBP' not in fichero][0]
            ct_equipo = [fichero for fichero in ficheros if equipo_old   in fichero and 'CARTA_TIRO'  in fichero and 'PBP' not in fichero][0]
            ct_rival = [fichero for fichero in ficheros if equipo_old  not in fichero and 'CARTA_TIRO' in fichero and 'PBP' not in fichero][0]
            pbp_equipo = [fichero for fichero in ficheros if equipo_old in fichero and 'CARTA_TIRO' not in fichero and 'PBP' in fichero][0]

            # Se realiza la carga de ficheros
            df_box_score_equipo = pd.read_csv(ruta_equipo_partido + '/' + box_score_equipo, sep=';')
            df_box_score_rival = pd.read_csv(ruta_equipo_partido + '/' + box_score_rival, sep=';')
            df_ct_equipo = pd.read_csv(ruta_equipo_partido + '/' + ct_equipo, sep=';')
            df_ct_rival = pd.read_csv(ruta_equipo_partido + '/' + ct_rival, sep=';')
            df_pbp_equipo = pd.read_csv(ruta_equipo_partido + '/' + pbp_equipo, sep=';')
            
            # Se remplaza el nombre de equipo por el correcto
            df_pbp_equipo['EQUIPO'] = df_pbp_equipo['EQUIPO'].replace(equipo_old,equipo_replace)
            
            # Se realiza la creación de la carpeta
            ruta_nuevo_partido = ruta_jornada_temporada_partidos+ '/' + partido[0].replace(equipo_old,equipo_replace)
            os.makedirs(ruta_nuevo_partido)
            
            # Se realiza la carga de los ficheros modificados
            df_box_score_equipo.to_csv(ruta_nuevo_partido + '/' + box_score_equipo.replace(equipo_old,equipo_replace), sep=';',index=False)
            df_box_score_rival.to_csv(ruta_nuevo_partido + '/' + box_score_rival, sep=';',index=False)
            df_ct_equipo.to_csv(ruta_nuevo_partido + '/' + ct_equipo.replace(equipo_old,equipo_replace), sep=';',index=False)
            df_ct_rival.to_csv(ruta_nuevo_partido + '/' + ct_rival, sep=';',index=False)
            df_pbp_equipo.to_csv(ruta_nuevo_partido + '/' + pbp_equipo.replace(equipo_old,equipo_replace), sep=';',index=False)
            
            
            # Se elimina la carpeta incorrecta
            shutil.rmtree(ruta_equipo_partido)
            
            
l_temporadas = ['2021']
equipo_name_old = '_Baskonia'
equipo_old = 'Baskonia'
equipo_replace = 'Bitci Baskonia'


for temporada in l_temporadas:
    
    # Se inicializa la carpeta de la temporada
    ruta_equipos_temporada = ruta_equipos + '/' + temporada
    
    # Se inicializa la ruta de cada una de las jornadas de las temporadas y se construye el listado
    ruta_jornada_temporada = ruta_jornada + '/' + temporada
    l_jornadas = os.listdir(ruta_jornada_temporada)
    
    for jornada in l_jornadas:
        
        # Se obtiene el listado de partidos de la jornada
        ruta_jornada_temporada_partidos = ruta_jornada_temporada + '/' + jornada
        l_partidos = os.listdir(ruta_jornada_temporada_partidos)
        
        # Se extrae el partido que haya jugado el equipo en la jornada
        partido = (list(filter(lambda x: equipo_name_old in x, l_partidos)))
        
        if len(partido) == 1:
            
            # Se crea el directorio del partido en la carpeta del equipo
            ruta_equipo_partido = ruta_jornada_temporada_partidos + '/' + partido[0]
            
            ficheros = os.listdir(ruta_equipo_partido)
            # Se realiza la selección de ficheros
            box_score_equipo = [fichero for fichero in ficheros if equipo_old in fichero and 'CARTA_TIRO' not in fichero and 'PBP' not in fichero][0]
            box_score_rival = [fichero for fichero in ficheros if equipo_old  not in fichero and 'CARTA_TIRO' not in fichero and 'PBP' not in fichero][0]
            ct_equipo = [fichero for fichero in ficheros if equipo_old   in fichero and 'CARTA_TIRO'  in fichero and 'PBP' not in fichero][0]
            ct_rival = [fichero for fichero in ficheros if equipo_old  not in fichero and 'CARTA_TIRO' in fichero and 'PBP' not in fichero][0]
            pbp_equipo = [fichero for fichero in ficheros if equipo_old in fichero and 'CARTA_TIRO' not in fichero and 'PBP' in fichero][0]
            
            # Se realiza la carga de ficheros
            df_box_score_equipo = pd.read_csv(ruta_equipo_partido + '/' + box_score_equipo, sep=';')
            df_box_score_rival = pd.read_csv(ruta_equipo_partido + '/' + box_score_rival, sep=';')
            df_ct_equipo = pd.read_csv(ruta_equipo_partido + '/' + ct_equipo, sep=';')
            df_ct_rival = pd.read_csv(ruta_equipo_partido + '/' + ct_rival, sep=';')
            df_pbp_equipo = pd.read_csv(ruta_equipo_partido + '/' + pbp_equipo, sep=';')
            
            # Se remplaza el nombre de equipo por el correcto
            df_pbp_equipo['EQUIPO'] = df_pbp_equipo['EQUIPO'].replace(equipo_old,equipo_replace)
            
            # Se realiza la creación de la carpeta
            ruta_nuevo_partido = ruta_jornada_temporada_partidos+ '/' + partido[0].replace(equipo_old,equipo_replace)
            os.makedirs(ruta_nuevo_partido)
            
            # Se realiza la carga de los ficheros modificados
            df_box_score_equipo.to_csv(ruta_nuevo_partido + '/' + box_score_equipo.replace(equipo_old,equipo_replace), sep=';',index=False)
            df_box_score_rival.to_csv(ruta_nuevo_partido + '/' + box_score_rival, sep=';',index=False)
            df_ct_equipo.to_csv(ruta_nuevo_partido + '/' + ct_equipo.replace(equipo_old,equipo_replace), sep=';',index=False)
            df_ct_rival.to_csv(ruta_nuevo_partido + '/' + ct_rival, sep=';',index=False)
            df_pbp_equipo.to_csv(ruta_nuevo_partido + '/' + pbp_equipo.replace(equipo_old,equipo_replace), sep=';',index=False)
            
            
            # Se elimina la carpeta incorrecta
            shutil.rmtree(ruta_equipo_partido)            
            
l_temporadas = ['2022']
equipo_name_old = '_Gran Canaria'
equipo_old = 'Gran Canaria'
equipo_replace = 'Dreamland Gran Canaria'

for temporada in l_temporadas:
    
    # Se inicializa la carpeta de la temporada
    ruta_equipos_temporada = ruta_equipos + '/' + temporada
    
    # Se inicializa la ruta de cada una de las jornadas de las temporadas y se construye el listado
    ruta_jornada_temporada = ruta_jornada + '/' + temporada
    l_jornadas = os.listdir(ruta_jornada_temporada)
    
    for jornada in l_jornadas:
        
        # Se obtiene el listado de partidos de la jornada
        ruta_jornada_temporada_partidos = ruta_jornada_temporada + '/' + jornada
        l_partidos = os.listdir(ruta_jornada_temporada_partidos)
        
        # Se extrae el partido que haya jugado el equipo en la jornada
        partido = (list(filter(lambda x: equipo_name_old in x, l_partidos)))
        
        if len(partido) == 1:
            
            # Se crea el directorio del partido en la carpeta del equipo
            ruta_equipo_partido = ruta_jornada_temporada_partidos + '/' + partido[0]
            
            ficheros = os.listdir(ruta_equipo_partido)
            # Se realiza la selección de ficheros
            box_score_equipo = [fichero for fichero in ficheros if equipo_old in fichero and 'CARTA_TIRO' not in fichero and 'PBP' not in fichero][0]
            box_score_rival = [fichero for fichero in ficheros if equipo_old  not in fichero and 'CARTA_TIRO' not in fichero and 'PBP' not in fichero][0]
            ct_equipo = [fichero for fichero in ficheros if equipo_old   in fichero and 'CARTA_TIRO'  in fichero and 'PBP' not in fichero][0]
            ct_rival = [fichero for fichero in ficheros if equipo_old  not in fichero and 'CARTA_TIRO' in fichero and 'PBP' not in fichero][0]
            pbp_equipo = [fichero for fichero in ficheros if equipo_old in fichero and 'CARTA_TIRO' not in fichero and 'PBP' in fichero][0]
            
            # Se realiza la carga de ficheros
            df_box_score_equipo = pd.read_csv(ruta_equipo_partido + '/' + box_score_equipo, sep=';')
            df_box_score_rival = pd.read_csv(ruta_equipo_partido + '/' + box_score_rival, sep=';')
            df_ct_equipo = pd.read_csv(ruta_equipo_partido + '/' + ct_equipo, sep=';')
            df_ct_rival = pd.read_csv(ruta_equipo_partido + '/' + ct_rival, sep=';')
            df_pbp_equipo = pd.read_csv(ruta_equipo_partido + '/' + pbp_equipo, sep=';')
            
            # Se remplaza el nombre de equipo por el correcto
            df_pbp_equipo['EQUIPO'] = df_pbp_equipo['EQUIPO'].replace(equipo_old,equipo_replace)
            
            # Se realiza la creación de la carpeta
            ruta_nuevo_partido = ruta_jornada_temporada_partidos+ '/' + partido[0].replace(equipo_old,equipo_replace)
            os.makedirs(ruta_nuevo_partido)
            
            # Se realiza la carga de los ficheros modificados
            df_box_score_equipo.to_csv(ruta_nuevo_partido + '/' + box_score_equipo.replace(equipo_old,equipo_replace), sep=';',index=False)
            df_box_score_rival.to_csv(ruta_nuevo_partido + '/' + box_score_rival, sep=';',index=False)
            df_ct_equipo.to_csv(ruta_nuevo_partido + '/' + ct_equipo.replace(equipo_old,equipo_replace), sep=';',index=False)
            df_ct_rival.to_csv(ruta_nuevo_partido + '/' + ct_rival, sep=';',index=False)
            df_pbp_equipo.to_csv(ruta_nuevo_partido + '/' + pbp_equipo.replace(equipo_old,equipo_replace), sep=';',index=False)
            
            
            # Se elimina la carpeta incorrecta
            shutil.rmtree(ruta_equipo_partido)
            
            
l_temporadas = ['2022']
equipo = 'BAXI Manresa'
nombre_old = 'Pérez'
nombre_new = 'Tyson'

for temporada in l_temporadas:
    
    # Se inicializa la carpeta de la temporada
    ruta_equipos_temporada = ruta_equipos + '/' + temporada
    
    # Se inicializa la ruta de cada una de las jornadas de las temporadas y se construye el listado
    ruta_jornada_temporada = ruta_jornada + '/' + temporada
    l_jornadas = os.listdir(ruta_jornada_temporada)
    
    for jornada in l_jornadas:
        
        # Se obtiene el listado de partidos de la jornada
        ruta_jornada_temporada_partidos = ruta_jornada_temporada + '/' + jornada
        l_partidos = os.listdir(ruta_jornada_temporada_partidos)
        
        # Se extrae el partido que haya jugado el equipo en la jornada
        partido = (list(filter(lambda x: equipo in x, l_partidos)))
        
        # Se crea el directorio del partido en la carpeta del equipo
        ruta_equipo_partido = ruta_jornada_temporada_partidos + '/' + partido[0]
        ficheros = os.listdir(ruta_equipo_partido)
        pbp_equipo = [fichero for fichero in ficheros if equipo in fichero and 'CARTA_TIRO' not in fichero and 'PBP' in fichero][0]
        
        df_pbp_equipo = pd.read_csv(ruta_equipo_partido + '/' + pbp_equipo, sep=';')
        
        df_pbp_equipo.at[(df_pbp_equipo['EQUIPO']==equipo) & (df_pbp_equipo['NOMBRE']==nombre_old), 'NOMBRE'] = nombre_new
        
        df_pbp_equipo.to_csv(ruta_equipo_partido + '/' + pbp_equipo, sep=';',index=False)      