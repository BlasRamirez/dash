import dash
from dash import dcc
from dash import html
from dash.dcc.Dropdown import Dropdown
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import api_handler 
import plotly.graph_objects as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



app.layout = html.Div([
    html.H1(
        children = "Primer Dash Master"  
        ,style = {'color':'#89b394','text-align':'center','justify':'center','padding-top':'100px','font-weight':'bold',
            'font-family':'courier',
            'padding-left':'1px'  }),
    html.H5(
        id = "subtitulo"
        ,children = "Miax Api"  
        ,style = {'color':'#89b394','text-align':'center','justify':'center','padding-top':'30px','font-weight':'bold',
                'font-family':'courier',
                'padding-left':'1px'  }),
        
    html.Div([

        html.Div([
            dcc.Dropdown(
                id = 'markets',
                options=[
                    {'label':'IBEX', 'value': 'IBEX'},
                    {'label':'DAX', 'value': 'DAX'},
                    {'label':'EUROSTOXX', 'value': 'EUROSTOXX'}
                ],
                value='IBEX'
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id = 'tickers'
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.RadioItems(
                id='radiobuton',
                options=[{'label': i, 'value': i} for i in ['Linea', 'Velas']],
                value='Linea',
                labelStyle={'display': 'inline-block'}
            ),
        dcc.Graph(
            id='grafico_precio'
        )
    ])
])


# Callback
@app.callback(
    [Output('tickers', 'options'),
    Output('tickers', 'value')],
    Input('markets', 'value'))
def devuelveAccionesMercado(mercado):
    # componentes
    ah = api_handler.APIBMEHandler(market=mercado, algo_tag="bramirez1")
    
    #lista de acciones
    ticker_master = ah.get_ticker_master()
    ticks = list(ticker_master.ticker)
    Dropdown_values = [{'label':tick, 'value': tick} for tick in ticks]
    primer_valor = Dropdown_values[0]['value']
    # Devolvemos
    return Dropdown_values,primer_valor


# Callback
@app.callback(
    Output('subtitulo', 'children'),
    [Input('tickers', 'value'),
    Input('markets', 'value')])
def cambiatitulo(titulo,mercado):
    # Devolvemos
    return f"Grafico de la accion {titulo} del indice {mercado}"


# Callback
@app.callback(
    Output('grafico_precio', 'figure'),
    [Input('markets', 'value'),
     Input('tickers', 'value'),
     Input('radiobuton', 'value')])
def cambiarTipoGrafico(mercado,ticker,radio):
    # componentes
    ah = api_handler.APIBMEHandler(market=mercado,algo_tag="bramirez1")

    if radio == "Linea":
        #datos
        ticker_data = ah.get_close_data_ticker(ticker=ticker)
        # figuras
        fig = px.line(ticker_data) 
    else:
        ticker_data = ah.get_data_ticker(ticker=ticker)
        # fig = px.line(ticker_data)
        fig = go.Figure(go.Candlestick(
            x=ticker_data.index,
            open=ticker_data['open'],
            high=ticker_data['high'],
            low=ticker_data['low'],
            close=ticker_data['close']
        ))
    
    # Devolvemos
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)