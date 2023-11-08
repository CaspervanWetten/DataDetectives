import pandas as pd

def caculate_per_capita(population: pd.DataFrame, to_merge: pd.DataFrame):
    to_merge = to_merge[to_merge['indicator'] == 'Consumption']
    to_merge = to_merge.groupby(['country', 'year']).agg({'gwh': 'sum'}).reset_index().round()
    merged = pd.merge(population, to_merge, on=['country', 'year'], how='inner')
    merged["per_capita"] = merged["gwh"] / merged["population"]
    return merged
    
gwh = pd.read_csv("dashboard/csv/electricity_consumption.csv")
pop = pd.read_csv("dashboard/csv/population.csv")

print(caculate_per_capita(pop, gwh).head(25))
