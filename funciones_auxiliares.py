import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score

def generar_visualizacion_barras(df,color,tempor):
    jornadas = df['JORNADA']
    volumen = df['VOLUMEN']
    
    plt.figure(figsize=(22, 3)) 
    bars = plt.bar(jornadas, volumen, color=color, edgecolor='black')

    for bar, vol in zip(bars, volumen):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, str(vol),
                ha='center', va='bottom')
        
    plt.tick_params(axis='x', labelrotation=80)
    plt.xlabel('Jornada')
    plt.ylabel('Nº de partidos disputados')
    plt.title('Temporada '+str(tempor))
    plt.grid(False)
    plt.ylim(0,10)
    plt.show()
    
def generar_visualizacion_barras_jugadores(df,color,temporada):
    jugadores = df['EQUIPO']
    volumen = df['NOMBRE_JUGADOR']

    plt.figure(figsize=(22, 3)) 
    bars = plt.bar(jugadores, volumen, color=color, edgecolor='black')

    for bar, vol in zip(bars, volumen):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, str(vol),
                ha='center', va='bottom')
        
    plt.tick_params(axis='x', labelrotation=80)
    plt.ylabel('Nº de jugadores inscritos')
    plt.title('Temporada '+str(temporada))
    plt.grid(False)
    plt.ylim(0,30)
    plt.show()
    
    
# Función que permite convertir los minutos jugados por el jugador a formato numérico
def procesar_minutos(valor): 

    # Se realiza la división del valor por el caracter ':'
    minutos = int(valor.split(':')[0])
    segundos = int(valor.split(':')[1])
    
    # Se realiza el redondeo de segundos
    if (segundos >= 30):
        return minutos + 1
    else:
        return minutos
    
# Funciónq ue permite realizar la divisón de los tiros de realizados de cualquier tipo
def obtener_tiros(valor):
    tiros_anotados, tiros_lanzados = map(int, valor.split('/'))
    return tiros_anotados, tiros_lanzados

# Función que permite realiza el procesamiento de la tabla del box_score
def procesar_BS(df):
    
    df = df.copy()
    # Selección de registos de jugadores
    df = df[~df['Unnamed: 0'].isin(['Equipo','Totales'])]

    # Eliminación de columna sobrante
    df.drop(['Unnamed: 0', 'T2%', 'T3%', 'TL%'], axis=1,inplace=True)

    # Conversión de la columna de dorsales a formato str
    df['NO.'] = df['NO.'].astype(int).astype(str)

    # Se realiza la conversión de minutos
    df['MIN'] = df['MIN'].apply(procesar_minutos)

    # Se realiza la conversión de los campos relacionados con el tiro
    df[['T2A', 'T2L']] = df['T2'].apply(obtener_tiros).apply(pd.Series)
    df[['T3A', 'T3L']] = df['T3'].apply(obtener_tiros).apply(pd.Series)
    df[['TLA', 'TLL']] = df['TL'].apply(obtener_tiros).apply(pd.Series)

    # Se eliminan los campos del tiro obsoletos
    df.drop(['T2','T3','TL'], axis=1, inplace=True)

    # Se realiza la conversión del campo del pérdidas
    df.rename(columns={'PÉR':'PER'},inplace=True)
    
    
    return df       


# Función que permite convertir las coordenadas 
def modificar_coordenadas(row):
    if row['x'] > 252:
        row['x'] = 508 - row['x']
        if row['y'] >= 142.5:
            row['y'] =  142.5 - (row['y'] - 142.5)
        elif row['y'] <= 142.5:
            row['y'] = 142.5 + (142.5 - row['y'])
    
    return row

# Función que permite definir el espacio de la pista al que pertenece el tiro
def obtener_grupo(x,y):
    
    # Definición del Grupo 1
    if ((0 <= x) and (x < 101) and (101 <= y) and (y < 186)):
        
        return  'GRUPO 1'
    
    # Definición del Grupo 2
    if ((0 <= x) and (x < 50) and (186 <= y) and (y < 260)):
        
        return  'GRUPO 2'

    # Definición del Grupo 3
    if ((0 <= x) and (x < 50) and (25 <= y) and (y < 101)):
        
        return  'GRUPO 3'

    # Definición del Grupo 5
    if ((101 <= x) and (x < 141) and (101 <= y) and (y < 186)):
        
        return  'GRUPO 5'

    # Definición del Grupo 7
    if ((0 <= x) and (x < 50) and (260 <= y) and (y < 275)):
        
        return  'GRUPO 7'

    # Definición del Grupo 9
    if ((141 <= x) and (x < 252) and (101 <= y) and (y < 186)):
        
        return  'GRUPO 9'

    # Definición del Grupo 11
    if ((0 <= x) and (x < 50) and (10 <= y) and (y < 25)):
        
        return  'GRUPO 11'

    # Definición del Grupo 4
    if ((x >= 50) and (y <= 101) and (y - 25 >= ((76/91) * (x-50)))):
        
        return  'GRUPO 4'    

    # Definición del Grupo 6
    if ((x >= 50) and (y >= 186) and (y - 186 <= ((-74/91) * (x-141)))):
        
        return  'GRUPO 6'        
    
    # Definición del Grupo 8
    if ((x >= 50) and (x <= 252) and (10 <= y) and (y <= 101) and (y - 25 <= (76/91) * (x - 50))):
        
        return  'GRUPO 8'      

    # Definición del Grupo 10
    if ((x >= 50) and (x <= 252) and (186 <= y) and (y <= 275) and (y - 260 >= (74/-91) * (x - 50))):
        
        return  'GRUPO 10'                      
    return "Fuera de límites"

# Función que permite convertir los tiros anotados y los que no
def modificar_href(row):
    if 'in' in row['href'] or 'dunk' in row['href']:
        row['href'] = 'IN'
    elif 'out' in row['href']:
        row['href'] = 'OUT'
    
    return row

def procesar_CT(df_jugador):
    df_equipo = df_jugador.apply(modificar_coordenadas, axis=1)
    df_equipo['GRUPO'] = df_equipo.apply(lambda row: obtener_grupo(row['x'], row['y']), axis=1)
    df_equipo = df_equipo.apply(modificar_href, axis=1)
    df_equipo_lite = df_equipo[['D','NOMBRE','href','GRUPO']]
    df_equipo_lite.columns = ['D', 'NOMBRE', 'ACIERTO', 'GRUPO']
    df_equipo_group = pd.DataFrame(df_equipo_lite.value_counts()).reset_index()
    df_equipo_group.columns = ['D', 'NOMBRE', 'ACIERTO', 'GRUPO', 'VOLUMEN']
    df_equipo_volumen = df_equipo_group.groupby(['D', 'NOMBRE', 'ACIERTO', 'GRUPO']).sum().reset_index()
    df_volumen_transformado = pd.pivot_table(df_equipo_volumen, values='VOLUMEN', index=['D', 'NOMBRE'], columns=['GRUPO', 'ACIERTO'], aggfunc='sum')
    df_volumen_transformado.columns = ['_'.join(map(str, col)).strip() for col in df_volumen_transformado.columns.values]
    df_volumen_transformado = df_volumen_transformado.reset_index()
    df_volumen_transformado = df_volumen_transformado.fillna(0)
    return df_volumen_transformado

def scotts_bins(data):
    bin_width = 3.5 * np.std(data) / np.power(len(data), 1/3)
    bins = int(np.ceil((np.max(data) - np.min(data)) / bin_width))
    return bins

def obtener_distribucion_variable(df, var, ax):
    ax.hist(df[var], bins=scotts_bins(df[var]), color='skyblue', edgecolor='black')
    ax.set_title('Distribución de {}'.format(var))
    ax.set_xlabel(var)
    ax.set_ylabel('Frecuencia')

def obtener_boxplot_variable(df, var, ax):
    bp = ax.boxplot(df[var], vert=True, patch_artist=True, showmeans=True, showfliers=False)

    # Obtener los valores del primer cuartil (Q1) y tercer cuartil (Q3)
    q1 = np.percentile(df[var], 25)
    q3 = np.percentile(df[var], 75)

    # Agregar texto para mostrar Q1 y Q3 dentro del gráfico
    ax.text(1, q1, str(q1), fontsize=8, ha='left', va='top', color='black')
    ax.text(1, q3, str(q3), fontsize=8, ha='left', va='bottom', color='black')

    ax.set_title('Diagrama de Caja y Bigotes de {}'.format(var))
    ax.set_ylabel(var)
    
def obtener_eFGp(df):
    # Se calcula los tiros de campo anotados
    fg = df['T2A'] + df['T3A']
    
    # Se calcula los tiros de campos lanzados
    fga = df['T2L'] + df['T3L']
       
    return (fg + (0.5 * df['T3A'])) / fga

def obtener_eFGp_rival(df):
    # Se calcula los tiros de campo anotados
    fg = df['T2A_R'] + df['T3A_R']
    
    # Se calcula los tiros de campos lanzados
    fga = df['T2L_R'] + df['T3L_R']
    
    return (fg + (0.5 * df['T3A_R'])) / fga

def obtener_ROp(df):
    return df['RO'] / (df['RO'] + df['RD_R'])

def obtener_ROp_rival(df):
    return df['RO_R'] / (df['RO_R'] + df['RD'])

def obtener_FTp(df):   
    fga = (df['T2L'] + df['T3L'])
    
    return df['TLA'] / fga

def obtener_FTp_rival(df):   
    fga = (df['T2L_R'] + df['T3L_R'])
    
    return df['TLA_R'] / fga

def obtener_tovp(df):    
    return df['TOV'] / (((df['T2L'] + df['T3L'] + (df['TLL'] * 0.44) + df['TOV'])))

def obtener_tovp_rival(df):    
    return df['TOV_R'] / (((df['T2L_R'] + df['T3L_R'] + (df['TLL_R'] * 0.44) + df['TOV_R'])))    

def obtener_oer(df):
    
    # Aplicación de fórmula de las posesiones
    poss = ((df['T2L'] + df['T3L'] + (df['TLL'] * 0.44) + df['TOV']) - df['RO']) 
    pts = (df['T2A'] * 2) + (df['T3A'] * 3) + (df['TLA'] * 1)
    return pts / poss

def obtener_der(df):
    
    # Aplicación de fórmula de las posesiones
    poss = ((df['T2L'] + df['T3L'] + (df['TLL'] * 0.44) + df['TOV']) - df['RO']) 
    pts = (df['T2A_R'] * 2) + (df['T3A_R'] * 3) + (df['TLA_R'] * 1)
    return pts / poss

def obtener_poss(df):
    return ((df['T2L'] + df['T3L'] + (df['TLL'] * 0.44) + df['TOV']) - df['RO']) 

def convertir_a_segundos(tiempo):
    minutos, segundos = map(int, tiempo.split(':'))
    total_segundos = minutos * 60 + segundos
    return total_segundos

def obtener_tiempo_pista(c_entrada,c_salida,s_entrada,s_salida):
    if (c_entrada == c_salida):
        tiempo_pista = s_entrada - s_salida

    elif (c_entrada != c_salida):
        l_prorroga = ['PR1', 'PR2', 'PR3', 'PR4']
        if (c_salida in l_prorroga):
            tiempo_pista = (300 + s_entrada) - s_salida
        else:
            tiempo_pista = (600 + s_entrada) - s_salida
            
    return tiempo_pista
    
def obtener_quintetos(df,equipo):
    # Se inicializa la variable del quinteto
    l_quinteto = []
    # Se inicializa el dataframe de retorno
    columnas = ['EQUIPO','QUINTETO','CUARTO_ENTRADA','MINUTO_ENTRADA','CUARTO_SALIDA','MINUTO_SALIDA' ,'T2A','T2L','T3A','T3L','TLA','TLL','RO','RD','STL','TOV','AST','BLK', 'T2A_R', 'T2L_R', 'T3A_R', 'T3L_R', 'TLA_R', 'TLL_R','RO_R','RD_R', 'STL_R','TOV_R','AST_R','BLK_R']
    df_return = pd.DataFrame(columns=columnas)

    # Se inicializan las variables de control
    cuarto_entrada = '1C'
    minuto_entrada = '10:00'

    # Inicialización de sumatorios
    vol_T2A_quinteto = 0
    vol_T2L_quinteto = 0
    vol_T3A_quinteto = 0
    vol_T3L_quinteto = 0
    vol_TLA_quinteto = 0
    vol_TLL_quinteto = 0
    vol_RO_quinteto = 0
    vol_RD_quinteto = 0
    vol_STL_quinteto = 0
    vol_TOV_quinteto = 0
    vol_AST_quinteto = 0
    vol_BLK_quinteto = 0

    vol_T2A_quinteto_RIVAL = 0
    vol_T2L_quinteto_RIVAL = 0
    vol_T3A_quinteto_RIVAL = 0
    vol_T3L_quinteto_RIVAL = 0
    vol_TLA_quinteto_RIVAL = 0
    vol_TLL_quinteto_RIVAL = 0
    vol_RO_quinteto_RIVAL = 0
    vol_RD_quinteto_RIVAL = 0
    vol_STL_quinteto_RIVAL = 0
    vol_TOV_quinteto_RIVAL = 0
    vol_AST_quinteto_RIVAL = 0
    vol_BLK_quinteto_RIVAL = 0

    # Selección de registros de equipo
    for i in range(len(df)):
        # Se inicializa las variables del registro
        jugador_registro = df['NOMBRE'].iloc[i]
        equipo_registro = df['EQUIPO'].iloc[i]
        accion = df['ACCION'].iloc[i]
        cuarto = df['CUARTO'].iloc[i]
        minuto = df['MINUTO'].iloc[i]
        
        if ((equipo_registro==equipo) & (accion == 'Entra a pista')):
            l_quinteto.append(jugador_registro)
            if(len(l_quinteto)==5):
                cuarto_entrada = cuarto
                minuto_entrada = minuto
            
        elif ((equipo_registro==equipo) & (accion == 'Sale de la pista')):
            if not jugador_registro in l_quinteto:
                l_quinteto.append(jugador_registro)
                
            if(len(l_quinteto)==5):
                registro = {'EQUIPO':equipo,'QUINTETO':l_quinteto.copy(),'CUARTO_ENTRADA':cuarto_entrada,'MINUTO_ENTRADA':minuto_entrada ,'CUARTO_SALIDA':cuarto,'MINUTO_SALIDA':minuto,
                            'T2A':vol_T2A_quinteto,'T2L':vol_T2L_quinteto,
                            'T3A':vol_T3A_quinteto,'T3L':vol_T3L_quinteto,
                            'TLA':vol_TLA_quinteto,'TLL':vol_TLL_quinteto,
                            'RO':vol_RO_quinteto,'RD':vol_RD_quinteto,
                            'STL':vol_STL_quinteto,'TOV':vol_TOV_quinteto,
                            'AST':vol_AST_quinteto,'BLK':vol_BLK_quinteto,
                            'T2A_R':vol_T2A_quinteto_RIVAL,'T2L_R':vol_T2L_quinteto_RIVAL,
                            'T3A_R':vol_T3A_quinteto_RIVAL,'T3L_R':vol_T3L_quinteto_RIVAL,
                            'TLA_R':vol_TLA_quinteto_RIVAL,'TLL_R':vol_TLL_quinteto_RIVAL,
                            'RO_R':vol_RO_quinteto_RIVAL,'RD_R':vol_RD_quinteto_RIVAL,
                            'STL_R':vol_STL_quinteto_RIVAL,'TOV_R':vol_TOV_quinteto_RIVAL,
                            'AST_R':vol_AST_quinteto_RIVAL,'BLK_R':vol_BLK_quinteto_RIVAL
                            }
                # df_return = df_return.append(registro, ignore_index=True)
                df_return = pd.concat([df_return,pd.DataFrame([registro])]) 
                
                # Se resetean las variables
                vol_T2A_quinteto = 0
                vol_T2L_quinteto = 0
                vol_T3A_quinteto = 0
                vol_T3L_quinteto = 0
                vol_TLA_quinteto = 0
                vol_TLL_quinteto = 0
                vol_RO_quinteto = 0
                vol_RD_quinteto = 0
                vol_STL_quinteto = 0
                vol_TOV_quinteto = 0
                vol_AST_quinteto = 0
                vol_BLK_quinteto = 0
                
                vol_T2A_quinteto_RIVAL = 0
                vol_T2L_quinteto_RIVAL = 0
                vol_T3A_quinteto_RIVAL = 0
                vol_T3L_quinteto_RIVAL = 0
                vol_TLA_quinteto_RIVAL = 0
                vol_TLL_quinteto_RIVAL = 0
                vol_RO_quinteto_RIVAL = 0
                vol_RD_quinteto_RIVAL = 0
                vol_STL_quinteto_RIVAL = 0
                vol_TOV_quinteto_RIVAL = 0
                vol_AST_quinteto_RIVAL = 0
                vol_BLK_quinteto_RIVAL = 0

                
            l_quinteto.remove(jugador_registro)
        
        elif ((equipo_registro==equipo) & (accion == 'Tiro de 2 anotado')):
            vol_T2A_quinteto = vol_T2A_quinteto + 1
            vol_T2L_quinteto = vol_T2L_quinteto + 1
        elif ((equipo_registro==equipo) & (accion == 'Tiro de 2 fallado')):
            vol_T2L_quinteto = vol_T2L_quinteto + 1
        
        elif ((equipo_registro==equipo) & (accion == 'Tiro de 3 anotado')):
            vol_T3A_quinteto = vol_T3A_quinteto + 1
            vol_T3L_quinteto = vol_T3L_quinteto + 1
        elif ((equipo_registro==equipo) & (accion == 'Tiro de 3 fallado')):
            vol_T3L_quinteto = vol_T3L_quinteto + 1    

        elif ((equipo_registro==equipo) & (accion == 'Tiro Libre anotado')):
            vol_TLA_quinteto = vol_TLA_quinteto + 1
            vol_TLL_quinteto = vol_TLL_quinteto + 1
        elif ((equipo_registro==equipo) & (accion == 'Tiro Libre fallado')):
            vol_TLL_quinteto = vol_TLL_quinteto + 1  
        
        elif ((equipo_registro==equipo) & (accion == 'Rebote Ofensivo')):
            vol_RO_quinteto = vol_RO_quinteto + 1
        elif ((equipo_registro==equipo) & (accion == 'Rebote Defensivo')):
            vol_RD_quinteto = vol_RD_quinteto + 1
        
        elif ((equipo_registro==equipo) & (accion == 'Recuperación')):
            vol_STL_quinteto = vol_STL_quinteto + 1
        elif ((equipo_registro==equipo) & (accion == 'Pérdida')):
            vol_TOV_quinteto = vol_TOV_quinteto + 1       

        elif ((equipo_registro==equipo) & (accion == 'Asistencia')):
            vol_AST_quinteto = vol_AST_quinteto + 1  
        elif ((equipo_registro==equipo) & (accion == 'Tapón')):
            vol_BLK_quinteto = vol_BLK_quinteto + 1  
            
        elif ((equipo_registro!=equipo) & (accion == 'Tiro de 2 anotado')):
            vol_T2A_quinteto_RIVAL = vol_T2A_quinteto_RIVAL + 1
            vol_T2L_quinteto_RIVAL = vol_T2L_quinteto_RIVAL + 1
        elif ((equipo_registro!=equipo) & (accion == 'Tiro de 2 fallado')):
            vol_T2L_quinteto_RIVAL = vol_T2L_quinteto_RIVAL + 1       
            
        elif ((equipo_registro!=equipo) & (accion == 'Tiro de 3 anotado')):
            vol_T3A_quinteto_RIVAL = vol_T3A_quinteto_RIVAL + 1
            vol_T3L_quinteto_RIVAL = vol_T3L_quinteto_RIVAL + 1
        elif ((equipo_registro!=equipo) & (accion == 'Tiro de 3 fallado')):
            vol_T3L_quinteto_RIVAL = vol_T3L_quinteto_RIVAL + 1    

        elif ((equipo_registro!=equipo) & (accion == 'Tiro Libre anotado')):
            vol_TLA_quinteto_RIVAL = vol_TLA_quinteto_RIVAL + 1
            vol_TLL_quinteto_RIVAL = vol_TLL_quinteto_RIVAL + 1
        elif ((equipo_registro!=equipo) & (accion == 'Tiro Libre fallado')):
            vol_TLL_quinteto_RIVAL = vol_TLL_quinteto_RIVAL + 1           

        elif ((equipo_registro!=equipo) & (accion == 'Rebote Ofensivo')):
            vol_RO_quinteto_RIVAL = vol_RO_quinteto_RIVAL + 1
        elif ((equipo_registro!=equipo) & (accion == 'Rebote Defensivo')):
            vol_RD_quinteto_RIVAL = vol_RD_quinteto_RIVAL + 1     
            
        elif ((equipo_registro!=equipo) & (accion == 'Recuperación')):
            vol_STL_quinteto_RIVAL = vol_STL_quinteto_RIVAL + 1
        elif ((equipo_registro!=equipo) & (accion == 'Pérdida')):
            vol_TOV_quinteto_RIVAL = vol_TOV_quinteto_RIVAL + 1     
            
        elif ((equipo_registro!=equipo) & (accion == 'Asistencia')):
            vol_AST_quinteto_RIVAL = vol_AST_quinteto_RIVAL + 1  
        elif ((equipo_registro!=equipo) & (accion == 'Tapón')):
            vol_BLK_quinteto_RIVAL = vol_BLK_quinteto_RIVAL + 1     
            
    registro = {'EQUIPO':equipo,'QUINTETO':l_quinteto.copy(),'CUARTO_ENTRADA':cuarto_entrada,'MINUTO_ENTRADA':minuto_entrada ,'CUARTO_SALIDA':cuarto,'MINUTO_SALIDA':'00:00',
                            'T2A':vol_T2A_quinteto,'T2L':vol_T2L_quinteto,
                            'T3A':vol_T3A_quinteto,'T3L':vol_T3L_quinteto,
                            'TLA':vol_TLA_quinteto,'TLL':vol_TLL_quinteto,
                            'RO':vol_RO_quinteto,'RD':vol_RD_quinteto,
                            'STL':vol_STL_quinteto,'TOV':vol_TOV_quinteto,
                            'AST':vol_AST_quinteto,'BLK':vol_BLK_quinteto,
                            'T2A_R':vol_T2A_quinteto_RIVAL,'T2L_R':vol_T2L_quinteto_RIVAL,
                            'T3A_R':vol_T3A_quinteto_RIVAL,'T3L_R':vol_T3L_quinteto_RIVAL,
                            'TLA_R':vol_TLA_quinteto_RIVAL,'TLL_R':vol_TLL_quinteto_RIVAL,
                            'RO_R':vol_RO_quinteto_RIVAL,'RD_R':vol_RD_quinteto_RIVAL,
                            'STL_R':vol_STL_quinteto_RIVAL,'TOV_R':vol_TOV_quinteto_RIVAL,
                            'AST_R':vol_AST_quinteto_RIVAL,'BLK_R':vol_BLK_quinteto_RIVAL
                            }
    # df_return = df_return.append(registro, ignore_index=True)              
    df_return = pd.concat([df_return,pd.DataFrame([registro])])         
    return df_return         

def procesar_pbp(df_pbp,equipo):
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
    return df_quintetos

# Función que permite obtener las posesiones obtenidas por un equipo
def obtener_posesiones(df_TM_STATS, df_OPP_STATS):
    Tm_FG = int(df_TM_STATS['T2A'].iloc[0]) + int(df_TM_STATS['T3A'].iloc[0])
    Tm_FGA = int(df_TM_STATS['T2L'].iloc[0]) + int(df_TM_STATS['T3L'].iloc[0])
    Tm_FTA = int(df_TM_STATS['TLL'].iloc[0])
    Tm_ORB = int(df_TM_STATS['RO'].iloc[0])
    Tm_DRB = int(df_TM_STATS['RD'].iloc[0])
    Tm_TOV = int(df_TM_STATS['PER'].iloc[0])

    Opp_FG = int(df_OPP_STATS['T2A'].iloc[0]) + int(df_OPP_STATS['T3A'].iloc[0])
    Opp_FGA = int(df_OPP_STATS['T2L'].iloc[0]) + int(df_OPP_STATS['T3L'].iloc[0])
    Opp_FTA = int(df_OPP_STATS['TLL'].iloc[0])
    Opp_ORB = int(df_OPP_STATS['RO'].iloc[0])
    Opp_DRB = int(df_OPP_STATS['RD'].iloc[0])
    Opp_TOV = int(df_OPP_STATS['PER'].iloc[0])
    
    return 0.5 * ((Tm_FGA + 0.4 * Tm_FTA - 1.07 * (Tm_ORB / (Tm_ORB + Opp_DRB)) * (Tm_FGA - Tm_FG) + Tm_TOV) + (Opp_FGA + 0.4 * Opp_FTA - 1.07 * (Opp_ORB / (Opp_ORB + Tm_DRB)) * (Opp_FGA - Opp_FG) + Opp_TOV))

# Función para la obtención de la estadística avanzada AST%
def obtener_AST_percentage(df, df_TM_STATS):
    
    ast = df['AS']
    mp = df['MIN']
    Tm_MP = df_TM_STATS['MIN'].iloc[0]
    Tm_FG = df_TM_STATS['T2L'].iloc[0] + df_TM_STATS['T3L'].iloc[0]
    fg = df['T2L'] + df['T3L']

    return ast / (((mp / (Tm_MP / 5)) * Tm_FG) - fg)

# Función para la obtención de la estadística avanzada AST%
def obtener_AST_percentage(df, df_TM_STATS):
    
    ast = df['AS']
    mp = df['MIN']
    Tm_MP = df_TM_STATS['MIN'].iloc[0]
    Tm_FG = df_TM_STATS['T2L'].iloc[0] + df_TM_STATS['T3L'].iloc[0]
    fg = df['T2L'] + df['T3L']

    return ast / (((mp / (Tm_MP / 5)) * Tm_FG) - fg)


# Función para la obtención de la estadística avanzada BLK%
def obtener_BLK_percentage(df, df_TM_STATS,df_OPP_STATS):
    
    blk = df['TAP']
    mp = df['MIN']
    Tm_MP = df_TM_STATS['MIN'].iloc[0]
    Opp_FGA = df_OPP_STATS['T2L'].iloc[0] + df_OPP_STATS['T3L'].iloc[0]
    Opp_3PA = (df_OPP_STATS['T3L'].iloc[0])

    return (blk * (Tm_MP / 5)) / (mp * (Opp_FGA - Opp_3PA))

# Función para la obtención de la estadística avanzada eFG%
def obtener_eFG_percentage(df):
    
    fg = df['T2A'] + df['T3A']
    tp = df['T3A']
    fga = df['T2L'] + df['T3L']
    return (fg + 0.5 * tp) / fga

# Función para la obtención de la estadística avanzada DRB%
def obtener_DRB_percentage(df, df_TM_STATS,df_OPP_STATS):
    
    drb = df['RD']
    mp = df['MIN']
    Tm_MP = df_TM_STATS['MIN'].iloc[0]
    Tm_DRB = df_TM_STATS['RD'].iloc[0]
    Opp_ORB = df_OPP_STATS['RO'].iloc[0]

    return (drb * (Tm_MP / 5)) / (mp * (Tm_DRB + Opp_ORB))

# Función para la obtención de la estadística avanzada ORB%
def obtener_ORB_percentage(df, df_TM_STATS,df_OPP_STATS):
    
    orb = df['RO']
    mp = df['MIN']
    Tm_MP = df_TM_STATS['MIN'].iloc[0]
    Tm_ORB = df_TM_STATS['RO'].iloc[0]
    Opp_DRB = df_OPP_STATS['RD'].iloc[0]

    return (orb * (Tm_MP / 5)) / (mp * (Tm_ORB + Opp_DRB))

# Función para la obtención de la estadística avanzada STL%
def obtener_STL_percentage(df, df_TM_STATS,df_OPP_STATS):
    
    stl = df['REC']
    mp = df['MIN']
    Tm_MP = df_TM_STATS['MIN'].iloc[0]
    Opp_Poss = obtener_posesiones(df_OPP_STATS, df_TM_STATS)

    return (stl * (Tm_MP / 5)) / (mp * Opp_Poss)

# Función para la obtención de la estadística avanzada TOV%
def obtener_TOV_percentage(df):
    
    tov = df['PER']
    fga = df['T2L'] + df['T3L']
    fta = df['TLA']

    return tov / (fga + 0.44 * fta + tov)

# Función para la obtención de la estadística avanzada USG%
def obtener_USG_percentage(df, df_TM_STATS):
    
    fga = df['T2L'] + df['T3L']
    fta = df['TLL']
    tov = df['PER']
    mp = df['MIN']
    Tm_MP = df_TM_STATS['MIN'].iloc[0]
    Tm_FGA = df_TM_STATS['T2L'].iloc[0] + df_TM_STATS['T3L'].iloc[0]
    Tm_FTA = df_TM_STATS['TLL'].iloc[0]
    Tm_TOV = df_TM_STATS['PER'].iloc[0]

    return ((fga + 0.44 * fta + tov) * (Tm_MP / 5)) / (mp * (Tm_FGA + 0.44 * Tm_FTA + Tm_TOV))

# Función que permite obtener el rating de tiro de tres
def obtener_3Pr(df):
    
    # Se obtienen el listado de ratio de 3 (3PA / FGA)
    tpar = df['T3L'] / (df['T3L']  + df['T2L'])
    
    return tpar

# Función que permite obtener el rating de tiro libres
def obtener_FTr(df):
    
    # Se obtienen el listado de ratio deFT (FTA / FGA)
    ftr = df['TLL'] / (df['T3L']  + df['T2L'])
    
    return ftr

def obtener_dor_team(df_TM_STATS, df_OPP_STATS):
    ro_rival = df_OPP_STATS['RO'].iloc[0]
    rd_team = df_TM_STATS['RO'].iloc[0]
    return ro_rival / (ro_rival + rd_team)

def obtener_dfg(df_OPP_STATS):
    fg_rival = df_OPP_STATS['T2A'].iloc[0] + df_OPP_STATS['T3A'].iloc[0]
    fga_rival = df_OPP_STATS['T2L'].iloc[0] + df_OPP_STATS['T3L'].iloc[0]
    return fg_rival / fga_rival

def obtener_fmwt(dfg, dor):
    return (dfg * (1 - dor)) / ((dfg * (1 - dor)) + ((1 - dfg) * dor)) 

def obtener_stops_1(df, fmwt, dor):
    stl = df['REC']
    blk = df['TAP']
    drb = df['RD']
    return stl + blk + fmwt * (1 - 1.07 * dor) + drb * (1 - fmwt)

def obtener_stops_2(df, df_TM_STATS, df_OPP_STATS, fmwt, dor):
    tmdfga = df_OPP_STATS['T2L'].iloc[0] + df_OPP_STATS['T3L'].iloc[0]
    tmdfgm = df_OPP_STATS['T2A'].iloc[0] + df_OPP_STATS['T3A'].iloc[0]
    tmblk = df_TM_STATS['TAP'].iloc[0]
    tmmin = df_TM_STATS['MIN'].iloc[0]
    tmdto = df_OPP_STATS['PER'].iloc[0]
    tmstl = df_TM_STATS['REC'].iloc[0]
    min = df['MIN']
    pf = df['FP']
    tmpf = df_TM_STATS['FP'].iloc[0]
    tmdfta = df_OPP_STATS['TLL'].iloc[0]
    tmdft_p = df_OPP_STATS['TLA'].iloc[0] / df_OPP_STATS['TLL'].iloc[0]
    return (((tmdfga - tmdfgm - tmblk) / tmmin) * fmwt * (1 - 1.07 * dor) + ((tmdto - tmstl) / tmmin)) * min + (pf / tmpf) * 0.4 * tmdfta * (1 - tmdft_p)**2

def obtener_stop_p(df,df_TM_STATS, df_OPP_STATS):
    team_poss = obtener_posesiones(df_TM_STATS, df_OPP_STATS)
    dor = obtener_dor_team(df_TM_STATS, df_OPP_STATS)
    dfg = obtener_dfg(df_OPP_STATS)
    fmwt = obtener_fmwt(dfg, dor)
    stops_1 = obtener_stops_1(df, fmwt, dor)
    stops_2 = obtener_stops_2(df, df_TM_STATS, df_OPP_STATS, fmwt, dor)
    stops = stops_1 + stops_2
    tmmin = df_TM_STATS['MIN'].iloc[0]
    min = df['MIN']
    return (stops * tmmin) / (team_poss * min)

def procesar_ADVANCED_STATS(df_equipo, df_equipo_total, df_rival):
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
    
    return df_return

def obtener_silueta(data,n_clusters):
    clusterer = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = clusterer.fit_predict(data)

    silhouette_avg = silhouette_score(data, cluster_labels)

    # Compute the silhouette scores for each sample
    sample_silhouette_values = silhouette_samples(data, cluster_labels)

    # Calcular el número total de valores negativos
    total_negative_values = np.sum(sample_silhouette_values < 0)
    total_samples = np.sum(sample_silhouette_values)

    fig, ax = plt.subplots()
    fig.set_size_inches(16, 8)

    y_lower = 10
    for i in range(n_clusters):
        ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == i]
        ith_cluster_silhouette_values.sort()
        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i

        color = cm.nipy_spectral(float(i) / n_clusters)
        ax.fill_betweenx(
            np.arange(y_lower, y_upper),
            0,
            ith_cluster_silhouette_values,
            facecolor=color,
            edgecolor=color,
            alpha=0.7,
        )

        ax.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
        y_lower = y_upper + 10

    # Mostrar el Average silhouette score y el Total negative silhouette values en un recuadro dentro del gráfico
    ax.text(
        0.95, 0.95, 
        f"Promedio de la silueta: {silhouette_avg:.2f}\n% de valores negativos: {round(total_negative_values/total_samples,3)}",
        verticalalignment="top",
        horizontalalignment="right",
        transform=ax.transAxes,
        bbox=dict(facecolor='white', alpha=0.7)
    )

    # Dibujar la línea de umbral de la silueta
    ax.axvline(x=silhouette_avg, color="red", linestyle="--")

    ax.set_xlabel("Valor del coeficiente de silueta")
    ax.set_ylabel("Etiqueta del clúster")
    ax.set_title(f"Método de la silueta para {n_clusters} clústeres")

    ax.set_yticks([])
    ax.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

    plt.show()

def obtener_poss(df):
    return ((df['T2L'] + df['T3L'] + (df['TLL'] * 0.44) + df['TOV']) - df['RO']) 

def obtener_visualizacion_quinteto(ax, df, posicion):
    vol_clusters = df[posicion].value_counts()
    vol_clusters = vol_clusters.sort_index()
    colores_por_valor = {    0: 'tab:blue',    1: 'tab:orange',    2: 'tab:green',    3: 'tab:red',    4: 'tab:purple',    5: 'tab:brown'}
    # Creación de la visualización
    ax.axis('equal')
    wedges, texts, autotexts = ax.pie(vol_clusters, autopct=lambda pct: f"{pct:.1f}%\n{int(pct/100.*sum(vol_clusters))}", startangle=90, wedgeprops=dict(edgecolor='black'), colors=[colores_por_valor.get(idx, 'gray') for idx in vol_clusters.index])
    for text in texts:
        text.set_color('black')
    for autotext in autotexts:
        autotext.set_color('black')
    ax.set_title(posicion)
    ax.legend(wedges, vol_clusters.index, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), title='Clusters', labels=vol_clusters.index)

