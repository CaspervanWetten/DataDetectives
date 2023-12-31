import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from numpy import asarray
from pandas import DataFrame, concat
from sklearn.metrics import mean_absolute_error


def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = DataFrame(data)
    cols = list()
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
    for i in range(0, n_out):
        cols.append(df.shift(-i))
    agg = concat(cols, axis=1)
    if dropnan:
        agg.dropna(inplace=True)
    return agg.values

def random_forest_predict(df):
    n_in = 50
    n_out = 12
    values = df.values
    train = series_to_supervised(values, n_in=n_in, n_out=n_out)
    trainX, trainy = train[:, :-n_out], train[:, -n_out:]
    model = RandomForestRegressor(max_depth=None, max_features="sqrt", min_samples_leaf=1, min_samples_split=2,
                                   n_estimators=500)
    model.fit(trainX, trainy)
    row = values[-n_in:].flatten()
    yhat = model.predict(asarray([row]))

    return yhat

def prediction(df):
    df['DATE'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    df = df.sort_values(by=["DATE"])
    dfpred2 = df[["DATE", "gwh"]]
    dfpred2.set_index('DATE', inplace=True)
    prediction = random_forest_predict(dfpred2)
    return prediction, dfpred2

def generate_fig(df):
    predresult = prediction(df)
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
    
    return resultsplot