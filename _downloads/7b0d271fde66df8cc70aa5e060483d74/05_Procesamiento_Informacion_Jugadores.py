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
    
dicc_nombres_jugadores = {'N.Williams-Goss' : 'Will.-Goss', 'T. Pérez' : 'Tyson', 'Miller-McIntyre' : 'M-McIntyre','A.Antetokounmpo':'Alex Anteto','D.Milosavljevic':'Milosavljevc'}
    
# Inicialización de las carpetas de almacenamineto
l_temporadas = list(diccionario_plantillas.keys())
l_temporadas = ['2020','2021','2022']


for temporada in l_temporadas:
    
    # Se inicializa la carpeta de la temporada
    ruta_equipos_temporada = ruta_equipos + '/' + temporada
    
    # Se obtiene el listado de equipos
    l_equipos = list(diccionario_plantillas[temporada].keys())
    l_descartes = []
    # Se extraen los datos por cada uno de los equipos que hay en la temporada
    for equipo in l_equipos:
        

        # Se obtiene el listado de partidos jugados por el equipo
        ruta_equipo_temporada = ruta_equipos_temporada + '/' + equipo
        l_partidos = os.listdir(ruta_equipo_temporada)
        l_partidos = [fichero for fichero in l_partidos if '.csv' not in fichero]
        
        # Se definen los dataframes de retorno del equipo y del equipo rival
        df_informacion_equipo = pd.DataFrame()       
        df_ct_equipo = pd.DataFrame() 
        
        for partido in l_partidos:
            

            # Se obtiene el listado de ficheros dentro del equipo
            ruta_partido = ruta_equipo_temporada + '/' + partido
            ficheros = os.listdir(ruta_partido)
                       
            # Se selecciona el fichero del equipo y del rival
            fichero_equipo = [fichero for fichero in ficheros if equipo in fichero and 'VS' not in fichero][0]
            fichero_pbp = [fichero for fichero in ficheros if 'PBP' in fichero][0]
            fichero_ct = [fichero for fichero in ficheros if equipo in fichero and 'CARTA_TIRO' in fichero][0]

            ############################################################################
            # PROCESAMIENTO DE BOX SCORE Y PLAY BY PLAY
            ############################################################################            
            # Selección de DFs de los equipos
            df_equipo = pd.read_csv(ruta_partido + '/' + fichero_equipo, sep=';')
            df_pbp = pd.read_csv(ruta_partido + '/' + fichero_pbp, sep=';')
            
            
            # Selección de jugadores con dorsal
            df_equipo = df_equipo[~df_equipo['NO.'].isna()]

            # Selección de dorsal y nombre
            df_nombre_box_score = df_equipo[['NO.','JUGADOR']]
            df_nombre_pbp = df_pbp[df_pbp['EQUIPO'] == equipo][['NOMBRE']].drop_duplicates()
            df_nombre_pbp = df_nombre_pbp[~df_nombre_pbp['NOMBRE'].isna()]
            l_jugadores_pbp = list(df_nombre_pbp['NOMBRE'].unique())
            
            
            # Añadir la columna 'JUGADOR_PBP' al DataFrame
            df_nombre_box_score['JUGADOR_PBP'] = ''

            # Recorrer el DataFrame y asignar el valor correspondiente de la lista
            for index, row in df_nombre_box_score.iterrows():
                
                nombre_bs = row['JUGADOR']
                
                for jugador in l_jugadores_pbp:
                    
                    if jugador.replace('.','') in nombre_bs:
                        df_nombre_box_score.at[index, 'JUGADOR_PBP'] = jugador
                        l_jugadores_pbp.remove(jugador)
                        break
            if len(l_jugadores_pbp) > 0:
                l_jugadores_vacios = list(df_nombre_box_score[df_nombre_box_score['JUGADOR_PBP'] ==''].JUGADOR.unique())
                for vacio in l_jugadores_vacios:
                    if vacio in dicc_nombres_jugadores.keys():
                        l_jugadores_pbp.remove(dicc_nombres_jugadores[vacio])
                        df_nombre_box_score.loc[df_nombre_box_score['JUGADOR'] == vacio, 'JUGADOR_PBP'] = dicc_nombres_jugadores[vacio]
                l_descartes.extend(l_jugadores_pbp)
                # if len(l_jugadores_pbp) > 0:
                #     print(temporada)
                #     print(equipo)
                #     print(l_jugadores_pbp)
            
            
            df_informacion_equipo = pd.concat([df_informacion_equipo,df_nombre_box_score])
            
            ############################################################################
            # PROCESAMIENTO DE CARTA DE TIRO
            ############################################################################ 
            df_ct = pd.read_csv(ruta_partido + '/' + fichero_ct, sep=';')
            df_ct = df_ct[['D','NOMBRE']].drop_duplicates()
            df_ct_equipo = pd.concat([df_ct_equipo,df_ct])
        
        # Procesamiento extraido del BOX SCORE y PBP
        df_informacion_equipo['NO.'] = df_informacion_equipo['NO.'].astype(int)
        df_info_jugador = df_informacion_equipo[['NO.','JUGADOR']].drop_duplicates()
        df_informacion_equipo = df_informacion_equipo[df_informacion_equipo['JUGADOR_PBP'] != ''].drop_duplicates().reset_index().drop('index',axis=1)
        df_informacion_equipo = df_info_jugador.merge(df_informacion_equipo,how='left')
        df_informacion_equipo.columns = ['DORSAL', 'JUGADOR', 'JUGADOR_PBP']
        df_informacion_equipo['JUGADOR_BS'] = df_informacion_equipo['JUGADOR']
        
        # Procesamiento extraido de CARTA DE TIRO
        df_ct_equipo = df_ct_equipo.drop_duplicates().reset_index().drop('index',axis=1)
        df_ct_equipo['D'] = df_ct_equipo['D'].astype(int)
        df_ct_equipo.columns = ['DORSAL', 'JUGADOR']
        df_ct_equipo['JUGADOR_CT'] = df_ct_equipo['JUGADOR']
        
        # Se unen la información de las cartas de tiro, bs y pbp
        df_informacion_equipo = df_informacion_equipo.merge(df_ct_equipo, how='left')
        df_informacion_equipo['JUGADOR'] = df_informacion_equipo['JUGADOR'].apply(lambda x: x.split('.')[1].strip() if '.' in x else x.strip())
        
        
        if equipo == 'Movistar Estudiantes' and temporada == '2020':
            df_informacion_equipo['JUGADOR'] = df_informacion_equipo['JUGADOR'].replace('JJ Barea','Barea')
            df_informacion_equipo['JUGADOR'] = df_informacion_equipo['JUGADOR'].replace('Solá','Sola')
        if equipo == 'MoraBanc Andorra' and temporada == '2021':
            df_informacion_equipo['JUGADOR'] = df_informacion_equipo['JUGADOR'].replace('Diagné','Diagne')
        if equipo == 'Lenovo Tenerife' and temporada == '2022':
            df_informacion_equipo['JUGADOR'] = df_informacion_equipo['JUGADOR'].replace('Diagné','Diagne')        
                 
        ############################################################################
        # PROCESAMIENTO DE LA PLANTILLA
        ############################################################################
        df_return = pd.DataFrame(columns=['DORSAL','JUGADOR','POSICION','ALTURA'])
        jugadores =  list(diccionario_plantillas[temporada][equipo]['plantilla'].keys())
        
        for jugador in jugadores:
            
            dorsal = diccionario_plantillas[temporada][equipo]['plantilla'][jugador]['Dorsal']
            altura = diccionario_plantillas[temporada][equipo]['plantilla'][jugador]['Altura']
            posicion = diccionario_plantillas[temporada][equipo]['plantilla'][jugador]['Posición']
            
            nueva_fila = {'DORSAL' : dorsal,'JUGADOR' : jugador,'POSICION' : posicion,'ALTURA' : altura}
            df_return = df_return.append({'DORSAL': dorsal, 'JUGADOR': jugador, 'POSICION': posicion, 'ALTURA': altura}, ignore_index=True)
        
        df_return['DORSAL'] = df_return['DORSAL'].astype(int)
        
        ############################################################################
        # CREACIÓN DE TABLERO DE INFORMACIÓN
        ############################################################################
        df_tablon_informacion = df_return.merge(df_informacion_equipo, on = 'DORSAL')

        index_keep = []
        for index, row in df_tablon_informacion.iterrows():
            if row['JUGADOR_y'] in row['JUGADOR_x']:
                index_keep.append(index)

        df_tablon_informacion = df_tablon_informacion[df_tablon_informacion.index.isin(index_keep)] 
        df_tablon_informacion = df_tablon_informacion.drop('JUGADOR_y',axis=1).rename(columns={'JUGADOR_x':'JUGADOR'})    
        
        if (temporada=='2020') & (equipo=='Club Joventut Badalona'):
            df_tablon_informacion = df_tablon_informacion[~((df_tablon_informacion['JUGADOR']=='Arnau Parrado') & (df_tablon_informacion['JUGADOR_PBP']=='Parra'))]
        
        # Se realiza la creación de la carpeta de estadísticas
        ruta_estadistica_final = ruta_estadisticas + '/' + temporada + '/' + equipo
        
        # Se realiza el guardado de estadísttcas
        df_tablon_informacion.to_csv(ruta_estadistica_final + '/05_INFORMACION_JUGADORES.csv', sep=';',index=False)  
        # prueba = df_tablon_informacion[['DORSAL','JUGADOR']].groupby('JUGADOR').count().reset_index()

        # if len(prueba[prueba['DORSAL']>1]):
        #     print('JUGADOR DUPLICADO')
        #     print(temporada)
        #     print(equipo)
        
        # if len(df_return.merge(df_tablon_informacion)) != len(df_return):
        #    print('JUGADOR PERDIDO')
        #    print(temporada)
        #    print(equipo) 
            
    