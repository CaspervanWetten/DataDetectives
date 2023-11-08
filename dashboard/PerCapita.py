import pandas as pd

def caculate_per_capita(population: pd.DataFrame, to_merge: pd.DataFrame):
    to_merge = to_merge.groupby(['country', 'year', 'month', 'indicator']).agg({'gwh': 'sum'}).reset_index().round()
    merged = pd.merge(population, to_merge, on=['country', 'year'], how='inner')
    merged["gwh"] = merged["gwh"] / merged["population"]
    merged = merged[["country" , "year", 'month', "indicator", "gwh"]]
    return merged
