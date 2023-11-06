import pandas as pd
from Database import Database

def caculate_per_capita(population: pd.DataFrame, to_merge: pd.DataFrame, to_match = "gwh", group_by = "year"):
    to_merge = to_merge[to_merge['indicator'] == 'Consumption']
    gwh_avg = to_merge.groupby(group_by)[to_match].mean().reset_index()
    per_cap = pd.merge(population, gwh_avg, on = ["year", "country"])
    per_cap["per_capita"] = per_cap[to_match] / per_cap["population"]
    
    return per_cap
    
gwh = pd.read_csv("dashboard\csv\electricity_consumption.csv")
pop = pd.read_csv("dashboard\csv\population.csv")

print(caculate_per_capita(pop, gwh))
