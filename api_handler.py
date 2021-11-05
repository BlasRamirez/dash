import requests
import json
import logging
import pandas as pd


logger = logging.getLogger('bramirez')


def allocs_to_frame(json_allocations):

    alloc_list = []
    for json_alloc in json_allocations:
        #print(json_alloc)
        allocs = pd.DataFrame(json_alloc['allocations'])
        allocs.set_index('ticker', inplace=True)
        alloc_serie = allocs['alloc']
        alloc_serie.name = json_alloc['date'] 
        alloc_list.append(alloc_serie)
    all_alloc_df = pd.concat(alloc_list, axis=1).T
    return all_alloc_df


class APIBMEHandler:
    
    def __init__(self, market, algo_tag):
        self.url_base = 'https://miax-gateway-jog4ew3z3q-ew.a.run.app'
        self.competi = 'mia_7'
        self.user_key = 'AIzaSyBMf4hImQiZxY9e29KpFeiqtJtE0MSxgnM'
        self.market = market
        self.algo_tag = algo_tag
    
    def get_ticker_master(self):
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
        url = f'{self.url_base}/data/ticker_master'
        params = {'competi': self.competi,
                  'market': self.market,
                  'key': self.user_key}
        response = requests.get(url, params)
        tk_master = response.json()
        maestro_df = pd.DataFrame(tk_master['master'])
        return maestro_df
    
    def get_close_data(self):
        """
        Función que obtiene las cotizaciones historicas de cierre de cada activo del índice.
        
        Parameters
        ----------
        
        Returns
        ----------
        data_close: dataframe con los precios de cierre de los activos del indice indicado
        """
        maestro_df = self.get_ticker_master()
        data_close = {}
        for i, data in maestro_df.iterrows():
            ticker = data.ticker
            logger.info(ticker)
            data_close[ticker] = self.get_close_data_ticker(ticker)
        data_close = pd.DataFrame(data_close)
        return data_close
    
    def get_close_data_ticker(self, ticker):
        """
        Función que obtiene las cotizaciones historicas de cierre de un activo en concreto
        
        Parameters
        ----------
        
        Returns
        ----------
        data_close: dataframe con los precios de cierre del activo indicado
        """
        url = f'{self.url_base}/data/time_series'
        params = {'market': self.market,
                  'key': self.user_key,
                  'ticker': ticker}
        response = requests.get(url, params)
        tk_data = response.json()
        series_data = pd.read_json(tk_data, typ='series')
        return series_data
    
    def get_data_ticker(self, ticker):
        url = f'{self.url_base}/data/time_series'
        params = {'market': self.market,
                  'key': self.user_key,
                  'ticker': ticker,
                  'close': False}
        response = requests.get(url, params)
        tk_data = response.json()
        df_data = pd.read_json(tk_data, typ='frame')
        return df_data
    
    def get_user_algos(self):
        """
        Función que obtiene los algoritmos disponibles y su información a partir de su token.
        
        Parameters
        ----------
        
        Returns
        ----------
        data_close: dataframe con los algoritmos para un usuario a partir de su token.
        """
        url = f'{self.url_base}/participants/algorithms'
        params = {'competi': self.competi,
                  'key': self.user_key}
        response = requests.get(url, params)
        algos = response.json()
        if algos:
            algos_df = pd.DataFrame(algos)
            print(algos_df.to_string())
            return algos_df

    def post_alloc(self, str_date, alloc_list):
        """
        Función que envia al API los pesos de los activos en los que quiere invertir el usuario.
        
        Parameters
        ----------
        str_date: fechas en las que invierte los activos.
        alloc_list: lista de los activos y pesos en los cuales invierte el usuario a la fecha anterior indicada.
        
        Returns
        ----------
        
        """
        url = f'{self.url_base}/participants/allocation'
        url_auth = f'{url}?key={self.user_key}'
        data = {
            'competi': self.competi,
            'algo_tag': self.algo_tag,
            'market': self.market,
            'date': str_date,
            'allocation': alloc_list,
        }
        response = requests.post(url_auth, data=json.dumps(data))
        #print(response.json())
    
    def get_allocs(self):
        """
        Función que obtiene la composición actual de la cartera del algotirmo y el índice indicado.
        
        Parameters
        ----------
        
        Returns
        ----------
        data_close: dataframe con los pesos de los activos en los que esta invertido a cada fecha.
        """
        url = f'{self.url_base}/participants/algo_allocations'
        params = {
            'key': self.user_key,
            'competi': self.competi,
            'algo_tag': self.algo_tag,
            'market': self.market,
        }
        response = requests.get(url, params)
        df = allocs_to_frame(response.json())
        return df
    
    def run_backtest(self):
        """
        Función que obtiene el resultado del back test de nuestro algoritmo a las fechas en las que estan subidos los pesos y los activos en los que estoy invertido.
        
        Parameters
        ----------
        
        Returns
        ----------
        data_close: resultados del back test
        """
        url = f'{self.url_base}/participants/exec_algo'
        url_auth = f'{url}?key={self.user_key}'
        params = {
            'competi': self.competi,
            'algo_tag': self.algo_tag,
            'market': self.market,
        }
        response = requests.post(url_auth, data=json.dumps(params))
        if response.status_code == 200:
            exec_data = response.json()
            status = exec_data.get('status')
            print(status)
            res_data = exec_data.get('content')
            trades = None
            if res_data:
                print(pd.Series(res_data['result']))
                trades = pd.DataFrame(res_data['trades'])
            return res_data
        else:
            exec_data = dict()
            print(response.text)
    
    def delete_allocs(self):
        """
        Función borra todos los registros de un algoritmo y un índice en concreto
        
        Parameters
        ----------
        
        Returns
        ----------
        
        """
        url = f'{self.url_base}/participants/delete_allocations'
        url_auth = f'{url}?key={self.user_key}'
        params = {
            'competi': self.competi,
            'algo_tag': self.algo_tag,
            'market': self.market,
        }
        response = requests.post(url_auth, data=json.dumps(params))
        print(response)
