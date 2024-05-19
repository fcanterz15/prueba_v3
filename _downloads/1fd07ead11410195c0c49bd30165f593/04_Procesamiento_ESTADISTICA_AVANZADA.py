#####################################################
# Importación y carga de librerías
#####################################################

import pandas as pd
import json
import os
from Funciones_Auxiliares_PD import *

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
l_temporadas = list(diccionario_plantillas.keys())

for temporada in l_temporadas:
    
    # Se inicializa la carpeta de la temporada
    ruta_equipos_temporada = ruta_estadisticas + '/' + temporada
    
    # Se obtiene el listado de equipos
    l_equipos = list(diccionario_plantillas[temporada].keys())
    
    # Se extraen los datos por cada uno de los equipos que hay en la temporada
    for equipo in l_equipos:
        
        # Se inicializa el dataframe del equipo
        df_equipo = pd.DataFrame()
        
        # Se obtiene el listado de partidos jugados por el equipo
        ruta_equipo_temporada = ruta_equipos_temporada + '/' + equipo
        ficheros = os.listdir(ruta_equipo_temporada)
            
        # Se seleccionan los ficheros de box score para el calculo de estadísticas
        ficheros = [fichero for fichero in ficheros if '01_' in fichero]
        fichero_equipo = [fichero for fichero in ficheros if not '_RIVAL' in fichero][0] 
        fichero_rival = [fichero for fichero in ficheros if '_RIVAL' in fichero][0]
        
        # Se realiza la carga de los ficheros
        df_equipo = pd.read_csv(ruta_equipo_temporada + '/' + fichero_equipo, sep=';')
        df_rival = pd.read_csv(ruta_equipo_temporada + '/' + fichero_rival, sep=';').rename(columns={'JUGADOR' : 'EQUIPO'})
        
        # Se obtienen las estadística totales del equipo
        df_equipo['EQUIPO'] = 'EQUIPO'
        df_equipo_total = df_equipo.drop(['NO.','JUGADOR'],axis=1).groupby('EQUIPO').sum().reset_index()
        
        # Se realiza el cálculo de las estadísticas avanzadas
        df_return = df_equipo[['NO.', 'JUGADOR']]
        df_return['eFG%'] = obtener_eFG_percentage(df_equipo)
        df_return['3Pr'] = obtener_3Pr(df_equipo)
        df_return['FTr'] = obtener_FTr(df_equipo)
        df_return['ORB%'] = obtener_ORB_percentage(df_equipo, df_equipo_total,df_rival)
        df_return['DRB%'] = obtener_DRB_percentage(df_equipo, df_equipo_total,df_rival)
        df_return['STL%'] = obtener_STL_percentage(df_equipo, df_equipo_total,df_rival)
        df_return['BLK%'] = obtener_BLK_percentage(df_equipo, df_equipo_total,df_rival)
        df_return['TOV%'] = obtener_TOV_percentage(df_equipo)
        df_return['AST%'] = obtener_AST_percentage(df_equipo, df_equipo_total)
        df_return['USG%'] = obtener_USG_percentage(df_equipo, df_equipo_total)
        df_return['STOP%'] = obtener_stop_p(df_equipo,df_equipo_total, df_rival)
        df_return = df_return.fillna(0).round(4)
        
        # Se realiza la creación de la carpeta de estadísticas
        ruta_estadistica_final = ruta_estadisticas + '/' + temporada + '/' + equipo
        
        # Se realiza el guardado de estadísttcas
        df_return.to_csv(ruta_estadistica_final + '/04_ESTADISTICAS_AVANZADAS.csv', sep=';',index=False)  
            
                