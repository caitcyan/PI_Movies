#Esta es la API en la que deployamos algunas funciones que analizan el dataset.

from typing import Union
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
def read_root():
    return {"Bienvenidos a mi API para saber más sobre películas y series...Usa las funciones get_actor, get_max_duration,get_score_count."}

@app.get("/get_max_duration({year},{platform},{duration_type})")  
def get_max_duration(year : Union[str, None] = None, platform : Union[str, None] = None, duration_type : Union[str, None] = None):
    # Esta funcion te devuelve el valor Película con mayor duración con 
    # filtros opcionales de AÑO, PLATAFORMA Y TIPO DE DURACIÓN.
    # El año por default es 2020.Tomo el año del release date.
    # La plataforma default es disney.
    # La duración por default es en minutos.
    import pandas as pd
    import numpy as np
    if year == None:
        year = '2020'
    if platform == None:
        platform = 'disney'
    if  duration_type  == None:
        duration_type = 'min'
    # Cargamos nuestro dataset previamente limpiado.
    dataset = pd.read_csv('df.csv')
    # Filtramos para que solo aparezcan películas.
    dataset = dataset[dataset['type'] == 'movie']
    # Convertimos algunos campos para poder analizarlos correctamente.
    # dataset['date_added'] = pd.to_datetime(dataset['date_added'])
    # No tenemos en cuenta las peliculas que no tengan duración.
    dataset['duration_int'] = dataset['duration_int'].astype(int)
    dataset.drop(dataset[(dataset['duration_int'] == 0)].index, inplace=True)

    # Ahora procedemos a filtrar. 
    # Primero filtramos por año.
    year_filtered = dataset[dataset['release_year'] == float(year)]
    # Luego por plataforma.
    platform_filtered = platform_filter(year_filtered, platform)
    #Encontramos el maximo, ya sea en minutos o en seasons(el default es en min) y el titulo correspondiente del producto.
   
    maximo, producto = encontrar_maximo(platform_filtered,duration_type)

    if  np.isnan(maximo):
        return('Esta búsqueda no devolvió ningun resultado!:( Intenta con otros parámetros.')
    else:
        return {'El producto con más duración fue'+ producto + 'con ' + str(maximo) + ' '+ duration_type + ' de duración'}

@app.get("/get_max_duration()")  
def get_max_duration(year : Union[str, None] = None, platform : Union[str, None] = None, duration_type : Union[str, None] = None):
    # Esta funcion te devuelve el valor Película con mayor duración con 
    # filtros opcionales de AÑO, PLATAFORMA Y TIPO DE DURACIÓN.
    # El año por default es 2020.Tomo el año del release date.
    # La plataforma default es disney.
    # La duración por default es en minutos.
    import pandas as pd
    import numpy as np
    if year == None:
        year = '2020'
    if platform == None:
        platform = 'disney'
    if  duration_type  == None:
        duration_type = 'min'
    # Cargamos nuestro dataset previamente limpiado.
    dataset = pd.read_csv('df.csv')
    # Filtramos para que solo aparezcan películas.
    dataset = dataset[dataset['type'] == 'movie']
    # Convertimos algunos campos para poder analizarlos correctamente.
    # dataset['date_added'] = pd.to_datetime(dataset['date_added'])
    # No tenemos en cuenta las peliculas que no tengan duración.
    dataset['duration_int'] = dataset['duration_int'].astype(int)
    dataset.drop(dataset[(dataset['duration_int'] == 0)].index, inplace=True)

    # Ahora procedemos a filtrar. 
    # Primero filtramos por año.
    year_filtered = dataset[dataset['release_year'] == float(year)]
    # Luego por plataforma.
    platform_filtered = platform_filter(year_filtered, platform)
    #Encontramos el maximo, ya sea en minutos o en seasons(el default es en min) y el titulo correspondiente del producto.
   
    maximo, producto = encontrar_maximo(platform_filtered,duration_type)

    if  np.isnan(maximo):
        return('Esta búsqueda no devolvió ningun resultado!:( Intenta con otros parámetros.')
    else:
        return {'El producto con más duración fue'+ producto + 'con ' + str(maximo) + ' '+ duration_type + ' de duración'}


@app.get("/get_score_count({platform},{score},{year})")
def get_score_count(platform : str, score : str, year : str):
#Cantidad de películas por plataforma con un puntaje 
# mayor a score en determinado año(release date).
# Cargamos nuestro dataset previamente limpiado.
    import pandas as pd
    import numpy as np
    dataset = pd.read_csv('df.csv')
    score = float(score)
    # Filtramos para que solo aparezcan películas.
    dataset = dataset[dataset['type'] == 'movie']
    # Convertimos algunos campos para poder analizarlos correctamente.
    # dataset['date_added'] = pd.to_datetime(dataset['date_added'])
    dataset['score'] = dataset['score'].astype(float)
    # Ahora procedemos a filtrar. 
    # Primero filtramos por año.
    year_filtered = dataset[dataset['release_year'] == int(year)]
    # Luego por plataforma.
    platform_filtered = platform_filter(year_filtered, platform)
    #Por ultimo por score
    score_filtered = platform_filtered[platform_filtered['score'] > score]
    #Obtenemos la lista de peliculas
    #listapeliculas =  np.array_str(score_filtered.title.values)
    listapeliculas =  score_filtered.title.value_counts()
    return {'Existen ' + str(listapeliculas.shape[0]) + ' películas.'}

@app.get("/get_count_platform({platform})") 
def get_count_platform(platform : str):
    # Cantidad de películas por plataforma con filtro de 
    # # PLATAFORMA. 
    import pandas as pd
    import numpy as np
    plataformas = ['amazon','disney','netflix','hulu']
    if platform in plataformas:
        dataset = pd.read_csv('df.csv')
        # Filtramos para que solo aparezcan películas.
        dataset = dataset[dataset['type'] == 'movie']
        
        # Ahora procedemos a filtrar por plataforma.
        platform_filtered = platform_filter(dataset, platform)
        #Contamos la cantidad de peliculas por cada plataforma.
        quantity = platform_filtered.title.value_counts()
        #Obtenemos la cantidad de peliculas
        return {'Existen ' + str(quantity.shape[0]) + ' películas en la plataforma ' + platform}
    else:
        return {'Introduce un valor válido de plataforma.'}
 
@app.get("/get_actor({platform},{year})") 
def get_actor(platform : str, year: str):
#Actor que más se repite según plataforma y año.
    import pandas as pd
    import numpy as np

    plataformas = ['amazon','disney','netflix','hulu']
    #year = ['2017','2018','2019','2020','2021','2022']
    if platform in plataformas:
        dataset = pd.read_csv('df.csv')
        # Filtramos para que solo aparezcan películas.
        dataset = dataset[dataset['type'] == 'movie']
        # Convertimos algunos campos para poder analizarlos correctamente.
        # dataset['date_added'] = pd.to_datetime(dataset['date_added'])
        year_filtered = dataset[dataset['release_year'] == float(year)]
        # Ahora procedemos a filtrar por plataforma.
        platform_filtered = platform_filter(year_filtered, platform)
        #Obtenemos el nombre del actor que mas se repite
        actores_g = platform_filtered.cast.tolist()
        lista_actores = []
        for actores in actores_g:
            if type(actores) != float:
                actores = actores.split(',')
                for actor1 in actores:
                    actor1 = actor1.strip()
                    lista_actores.append(actor1)
        arrayl =np.array(lista_actores)
        u, c = np.unique(arrayl, return_counts=True)
        nvecesmax = c.max()
        y = u[c == nvecesmax]
        if y.shape[0] != 0:
            #Obtenemos la cantidad de veces que estuvo ese actor
            actormasrepetido = y
            if y.shape[0] == 1:
                rpta = {'El actor ' + str(actormasrepetido) + ' es el que más se repite, ' + str(nvecesmax) +' veces'}
            else:
                rpta = {'Los actores ' + str(actormasrepetido) + ' son los que más se repiten, ' + str(nvecesmax) +' veces'}
            return  rpta
        else:
            return {'La lista está vacía.'}       
       
    else:
            return {'Introduce un valor válido de plataforma.'}

def platform_filter(dataframe, platform):

    if platform == 'disney':
        platform_filtered = dataframe[dataframe['id'].str[0] == 'd']
        return platform_filtered
    elif platform == 'netflix':
        platform_filtered = dataframe[dataframe['id'].str[0] == 'n']
        return platform_filtered
    elif platform == 'hulu':
        platform_filtered = dataframe[dataframe['id'].str[0] == 'h']
        return platform_filtered
    elif platform == 'amazon':
        platform_filtered = dataframe[dataframe['id'].str[0] == 'a']
        return platform_filtered

def encontrar_maximo(dataframe, type):
    import numpy as np
    if type == 'season':
        dfmaximo = dataframe[dataframe['duration_type']== 'season']
        maximo = dfmaximo['duration_int'].max()
        dffiltrado = dataframe[dataframe['duration_int']== maximo]
        #Agarramos solo el titulo.Lo convertimos en string.
        producto = np.array_str(dffiltrado['title'].values)
        #Quitamos los brackets innecesarios
        producto = str(producto).replace(' [', '').replace('[', '').replace(']', '')
        return maximo , producto
    elif type == 'min':
        dfmaximo = dataframe[dataframe['duration_type']== 'min']
        maximo = dfmaximo['duration_int'].max()
        dffiltrado = dataframe[dataframe['duration_int']== maximo]
        #Agarramos solo el titulo. Lo convertimos en string.
        producto = np.array_str(dffiltrado['title'].values)
        #Quitamos los brackets innecesarios.
        producto = str(producto).replace(' [', '').replace('[', '').replace(']', '')
        return maximo , producto

