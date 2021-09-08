from sklearn.ensemble import RandomForestRegressor
import yfinance as yf
import pandas as pd
import sklearn
import datetime
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn import preprocessing
import math
import numpy as np
import plotly.graph_objs as go
from sklearn.linear_model import LinearRegression
def predict_forecast(df, forecast_days):
    pred = "Close"
    df.fillna(value = "999999", inplace = True)
    df["label"] = df[pred].shift(forecast_days)

    x = np.array(df.drop(['label'], 1))
    x = preprocessing.scale(x)
    x_small = x[-forecast_days:]
    x = x[:-forecast_days]
    df.dropna(inplace=True)
    y = np.array(df['label'])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state = 0)

    model = SVR(kernel = 'rbf',C = 100, gamma = 0.06)
    model.fit(x_train, y_train)
    model.score(x_test, y_test)
    model5 = RandomForestRegressor(n_estimators = 150, random_state = 0)
    model5.fit(x_train, y_train)
    confidence5 = model5.score(x_test, y_test)
    last_date = df.iloc[-1].name
    #name of last date
    last_unix = last_date.timestamp()
    one_day = 86400
    #number of seconds in a day
    next_unix = last_unix + one_day
    predict_1 = model5.predict(x_small)
    dataframe = pd.DataFrame()
    for i in predict_1:
        next_date = datetime.datetime.fromtimestamp(next_unix)
        next_unix += one_day
        dataframe[next_date] = [i]
    model = SVR()
    model.fit(x_train, y_train)
    model.score(x_test, y_test)
    dataframe = dataframe.transpose()
    dataframe.reset_index(inplace = True)
    dataframe.columns = ["Date", "Predicted Close"]
    trace1 = go.Scatter(x = dataframe.Date, y = dataframe["Predicted Close"])
    fig = go.Figure(data = trace1)
    return fig