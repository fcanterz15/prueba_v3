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
from Funciones_Auxiliares_PD import *
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
ruta_estadisticas = 'E:/TFM/02. Datos/ACB/ESTADISTICAS'

#####################################################
# Ejecución
#####################################################

# Cargar el diccionario desde el archivo JSON
with open(ruta_dicc_plantillas, 'r') as archivo:
    diccionario_plantillas = json.load(archivo)
    
# Cargar el diccionario desde el archivo JSON
with open(ruta_dicc_partidos, 'r') as archivo:
    diccionario_partidos = json.load(archivo)    
    
    
# Inicialización de las carpetas de almacenamineto
l_temporadas = ['2020', '2021', '2022']#list(diccionario_plantillas.keys())

for temporada in l_temporadas:
    
    # Se inicializa la carpeta de la temporada
    ruta_equipos_temporada = ruta_equipos + '/' + temporada
    
    # Se obtiene el listado de equipos
    l_equipos = list(diccionario_plantillas[temporada].keys())
    
    # Se extraen los datos por cada uno de los equipos que hay en la temporada
    for equipo in l_equipos:
        
        # Se inicializa el dataframe del equipo
        df_equipo = pd.DataFrame()
        
        # Se obtiene el listado de partidos jugados por el equipo
        ruta_equipo_temporada = ruta_equipos_temporada + '/' + equipo
        l_partidos = os.listdir(ruta_equipo_temporada)
        l_partidos = [fichero for fichero in l_partidos if '.csv' not in fichero]
        
        for partido in l_partidos:
            
            # Se obtiene el listado de ficheros dentro del equipo
            ruta_partido = ruta_equipo_temporada + '/' + partido
            ficheros = os.listdir(ruta_partido)
            
            # Se seleccionan los ficheros de box score
            ficheros = [fichero for fichero in ficheros if 'PBP' in fichero]
            
            # Se selecciona el fichero del equipo y del rival
            fichero_pbp = ficheros[0]
            
            # Se realiza la lectura del dataframe del pbp
            df_pbp = pd.read_csv(ruta_partido + '/' + fichero_pbp, sep=';')
            
            # Se ordena el dataframe para su procesamineto
            df_pbp = df_pbp.sort_values(by=['CUARTO','MINUTO','ACCION'],ascending=[True, False, False]).reset_index().drop('index',axis=1)
            
            # Estandarización de acciones
            df_pbp['ACCION'] = df_pbp['ACCION'].replace('Cinco Inicial','Entra a pista')
            df_pbp['ACCION'] = df_pbp['ACCION'].replace('Mate','Tiro de 2 anotado')
            df_pbp['ACCION'] = df_pbp['ACCION'].replace('Mate fallado','Tiro de 2 fallado')
            df_pbp['ACCION'] = df_pbp['ACCION'].replace('Triple anotado','Tiro de 3 anotado')
            df_pbp['ACCION'] = df_pbp['ACCION'].replace('Triple fallado','Tiro de 3 fallado')
            
            # Se obtiene el dataframe de quintetos
            df_quintetos = obtener_quintetos(df_pbp,equipo)
            
            # Se convierten los minutos a segundo
            df_quintetos['SEGUNDOS_ENTRADA'] = df_quintetos.MINUTO_ENTRADA.apply(convertir_a_segundos)
            df_quintetos['SEGUNDOS_SALIDA'] = df_quintetos.MINUTO_SALIDA.apply(convertir_a_segundos)
            
            # Extracción del tiempo en pista que ha estado cada quinteto
            df_quintetos['TIEMPO_PISTA'] =  df_quintetos.apply(lambda row: obtener_tiempo_pista(row['CUARTO_ENTRADA'], row['CUARTO_SALIDA'], row['SEGUNDOS_ENTRADA'], row['SEGUNDOS_SALIDA']), axis=1)
                     
            # Se transforma la variable quinteto
            df_quintetos['QUINTETO'] = df_quintetos['QUINTETO'].apply(lambda lista: sorted(lista))
            df_quintetos['J1'] = df_quintetos['QUINTETO'].apply(lambda lista: lista[0])
            df_quintetos['J2'] = df_quintetos['QUINTETO'].apply(lambda lista: lista[1])
            df_quintetos['J3'] = df_quintetos['QUINTETO'].apply(lambda lista: lista[2])
            df_quintetos['J4'] = df_quintetos['QUINTETO'].apply(lambda lista: lista[3])
            df_quintetos['J5'] = df_quintetos['QUINTETO'].apply(lambda lista: lista[4])
            
            # Eliminación de columnas
            df_quintetos.drop(['QUINTETO','CUARTO_ENTRADA', 'MINUTO_ENTRADA','CUARTO_SALIDA', 'MINUTO_SALIDA','SEGUNDOS_ENTRADA', 'SEGUNDOS_SALIDA'],axis=1,inplace=True)
            
            # Se concatena el dataframe de quintetos al del equipo
            df_equipo = pd.concat([df_equipo,df_quintetos])
            
        # Se convierte las columnas a formato int
        columnas_a_convertir = ['T2A', 'T2L', 'T3A', 'T3L', 'TLA', 'TLL', 'RO', 'RD', 'STL','TOV', 'AST', 'BLK', 'T2A_R', 'T2L_R', 'T3A_R', 'T3L_R', 'TLA_R','TLL_R', 'RO_R', 'RD_R', 'STL_R', 'TOV_R', 'AST_R', 'BLK_R','TIEMPO_PISTA']
        df_equipo[columnas_a_convertir] = df_equipo[columnas_a_convertir].astype('int64')
        
        # Se realiza el agrupado de los quintetos
        df_equipo_agregado = df_equipo.groupby(by=['EQUIPO', 'J1', 'J2', 'J3', 'J4', 'J5']).sum().reset_index()
        
        ruta_estadistica_final = ruta_estadisticas + '/' + temporada + '/' + equipo
        df_equipo_agregado.to_csv(ruta_estadistica_final + '/03_ESTADISTICAS_QUINTETO_EQUIPO.csv', sep=';',index=False)      