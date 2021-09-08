from logging import PlaceHolder
import dash
from dash import dependencies
from dash.dependencies import Output, State
from dash.development.base_component import Component
import dash_core_components as dcc
from dash_core_components.Input import Input
import dash_html_components as html
from datetime import date
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.tools import mpl_to_plotly
from dash.exceptions import PreventUpdate
import plotly.express as px
import model

app = dash.Dash(__name__)
server = app.server
app.layout = html.Div([ html.Div([
    html.P("Welcome to Stock Dash!", className="start", style= {'text-align': 'center'}),
    html.P("Enter the stock code:"),
    html.Div([
        dcc.Input(id = "stockCode" , type = "text", placeholder = "",  style={'marginRight':'10px'}),
        html.Button('Submit', id='submit', n_clicks=0, style = {'backgroundColor': 'rgb(10, 170, 170)', 'color':'white','width':'27%', 'border':'1.5px black solid','height': '50px','text-align':'center'} )
    ]),
    html.Div([
        dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(1995, 8, 5),
        max_date_allowed=date(2017, 9, 19),
        initial_visible_month=date(2017, 8, 5),
        end_date=date(2017, 8, 25)
    ), 
    html.Div([
        html.Button('Stock price', id='stockPrice', n_clicks=0, style = {'backgroundColor': 'rgb(10, 170, 170)', 'color':'white','width':'100%', 'border':'1.5px black solid','height': '50px','text-align':'center', 'marginTop': '100'}),
        dcc.Input(id = 'numberOfDays', type = "text"),
        html.Button('Forecast', id='forecast', n_clicks=0, style = {'backgroundColor': 'rgb(10, 170, 170)', 'color':'white','width':'25%', 'border':'1.5px black solid','height': '50px','text-align':'center', 'marginTop': '100'})
    ], className= 'buttons')
]),
    ],style = {'width':'25%','height': '800px'},className="inputs"), html.Div(
          [
            html.Div(
                  [  # Logo
                    # Company Name
                  ], 
                id = "name", className="header"),
            html.Div(id="description", className="description_ticker"),
            dcc.Graph(id="graphs-content"),
            dcc.Graph(id="main-content"),
            dcc.Graph(id="forecast-content")
          ],
        className="content")
 ], className = 'container')



@app.callback(
   [Output(component_id="name", component_property="children"),Output(component_id="description",component_property= 'children')],
    [dash.dependencies.Input(component_id = "submit", component_property = 'n_clicks')],
    [State(component_id="stockCode", component_property='value')]

)
def update_data(n_clicks, val1):
    if n_clicks == 0:
        return dash.no_update
    ticker = yf.Ticker(val1)
    inf = ticker.info
    df = pd.DataFrame().from_dict(inf, orient="index").T
    if 'longBusinessSummary' in df.columns:
        description = [df['shortName'] + ':' + df['longBusinessSummary']]
    else: description = ["No description available"]
    return df["shortName"], df["longBusinessSummary"]
@app.callback(
    [Output(component_id='graphs-content', component_property='figure'), Output(component_id='main-content', component_property='figure')],
    [dash.dependencies.Input(component_id = 'stockPrice', component_property = 'n_clicks')],
    [State(component_id='stockCode', component_property='value'),
    State(component_id='my-date-picker-range', component_property='start_date'),
    State(component_id = 'my-date-picker-range', component_property='end_date')]
)
def update_graph(n_clicks, value, start_date, end_date):
    if n_clicks == 0:
        return dash.no_update
    
    df = yf.download(value, start_date, end_date)
    df.reset_index(inplace=True)
    fig = px.line(df, x = "Date", y = ["Close", "Open"])
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig1 = px.scatter(df,
                    x= "Date",
                    y= "EWA_20",
                    title="Exponential Moving Average vs Date")

    
    return fig, fig1
@app.callback(
    Output(component_id="forecast-content", component_property="figure"),
    [dash.dependencies.Input("forecast", "n_clicks")],
    [State("stockCode", "value"),
    State(component_id='my-date-picker-range', component_property='start_date'),
    State(component_id = 'my-date-picker-range', component_property='end_date'),
    dash.dependencies.State("numberOfDays", "value")]
)
def update_forecast(n_clicks,value,start_date, end_date,numberOfDays):
    if n_clicks == 0:
        return dash.no_update
    df = yf.download(value, start = start_date, end = end_date)
    figure = model.predict_forecast(df, int(numberOfDays))
    return figure

if __name__ == "__main__":
    app.run_server(debug=True)
    