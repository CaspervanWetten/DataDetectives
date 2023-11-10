from sqlalchemy import create_engine, text, inspect, Table
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
import numpy as np
from numpy import asarray
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.metrics import mean_absolute_error
from matplotlib import pyplot

# Dit is de hoe de dfpred wordt gegenereerd als je show_plot aanroept en de query die hieronderstaat hieraan meegeeft zou het moeten werken

#query_6 = '''SELECT * FROM electricity_consumption'''
#con = engine.connect()
#dfpred = pd.read_sql(query_6, con, index_col = "index" )

def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = DataFrame(data)
    cols = list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
    # put it all together
    agg = concat(cols, axis=1)
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg.values

def random_forest_predict(df):
    n_in = 50
    n_out = 40
    # transform the time series data into supervised learning
    values = df.values
    train = series_to_supervised(values, n_in=n_in, n_out=n_out)
    # split into input and output columns
    trainX, trainy = train[:, :-n_out], train[:, -n_out:]  # Separate the last n_out columns as output

    # fit model with the provided hyperparameters
    model = RandomForestRegressor(max_depth= None, max_features="sqrt", min_samples_leaf= 1, min_samples_split=2, n_estimators=500)
    model.fit(trainX, trainy)

    # construct an input for a new prediction
    row = values[-n_in:].flatten()

    # make the prediction
    yhat = model.predict(asarray([row]))

    return yhat

def prediction(df, country, indicator):
    df.drop("Unnamed: 0", axis = 1, inplace = True)  # dit 
    df['DATE'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    df.drop("year", axis = 1, inplace= True)
    df.drop("month", axis = 1, inplace = True)
    dcountry = "AUT"
    dindicator = "Consumption"
    df = df[(df["country"] == country) & (df["indicator"] == indicator)]
    #dfpred["DATE"] = dfpred["DATE"].astype(str)
    dfpred2 = df[["DATE","gwh"]]
    dfpred2.set_index('DATE', inplace = True)
    prediction = random_forest_predict(dfpred2)
    return prediction, dfpred2
    
def show_plot(df, country, indicator):
    predresult = prediction(df, country, indicator)
    resultsplot = predresult[1]
    resultsplot = resultsplot.reset_index()
    resultsplot["DATE"] = pd.to_datetime(resultsplot["DATE"])
    resultsplot["predict"] = False
    result = predresult[0].reshape(-1)
    for value in result:
        last_date = resultsplot["DATE"].max()
        new_date = last_date + pd.DateOffset(months=1)
        list_row = [new_date, value, True]
        resultsplot.loc[len(resultsplot)] = list_row
    fig = px.line(resultsplot, x = "DATE",y ="gwh", color = "predict" )
    return fig