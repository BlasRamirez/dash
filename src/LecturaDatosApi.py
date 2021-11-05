import pandas as pd
import numpy as np
import requests, json

url_base = 'https://miax-gateway-jog4ew3z3q-ew.a.run.app'
headers = {'Content-Type': 'application/json'}

competi = 'mia_6'
user_key = 'AIzaSyBMf4hImQiZxY9e29KpFeiqtJtE0MSxgnM'

def descargaMaestro(indice):
    """
    Función que obtiene la información del índice:
        - Activos
        - Cuando entro en el índice y cuando salio
    Parameters
    ----------
        
    Returns
    ----------
    maestro_df: dataframe con la información del índice
    """
    url = f'{url_base}/data/ticker_master'
    params = {'competi': competi,
          'market': indice,
          'key': user_key}
    response = requests.get(url, params)
    tk_master = response.json()
    maestro_df = pd.DataFrame(tk_master['master'])
    return maestro_df

def descargaSerieDatosDeUnTicker(indice,ticker):
    """
    Función que obtiene las cotizaciones historicas de cierre de un activo en concreto
        
    Parameters
    ----------
        
    Returns
    ----------
    df_data: dataframe con los precios de cierre del activo indicado
    """
    url2 = f'{url_base}/data/time_series'
    params = {'market': indice,
              'key': user_key,
              'ticker': ticker,
              'close': False}
    response = requests.get(url2, params)
    tk_data = response.json()
    if response.status_code == 200:
        df_data = pd.read_json(tk_data, typ='frame')
    else: 
        print(response.text)
    return df_data

def descargaSerieDatosTotal(indice, campo, fechainicio, fechafin):
    """
    Función que obtiene las cotizaciones historicas de cierre de cada activo del índice.
        
    Parameters
    ----------
        
    Returns
    ----------
    dataframeCompleto: dataframe con los precios de cierre de los activos del indice indicado
    """
    tickers=descargaMaestro(indice).ticker.values
    fechas = pd.date_range(start=fechainicio, end=fechafin, freq='B')
    dataframeCompleto = pd.DataFrame(np.zeros((fechas.shape[0], tickers.shape[0])),index=fechas,columns=tickers)
    for tick in tickers:
        dataframeCompleto.loc[:,tick]= descargaSerieDatosDeUnTicker(indice,tick).loc[:,campo]
        
    return dataframeCompleto

def descargaSerieDatosIndice(indice, campo):
    """
    Función que obtiene las cotizaciones historicas de un índice
        
    Parameters
    ----------
        
    Returns
    ----------
    df_benchmark: dataframe con los precios de cierre del indice indicado
    """
    url2 = f'{url_base}/data/time_series'
    params = {'market': indice,
              'key': user_key,
              'ticker': 'benchmark',
              'close': False}
    response = requests.get(url2, params)
    tk_data = response.json()
    df_benchmark = pd.read_json(tk_data, typ='frame').loc[:,campo]
    return df_benchmark