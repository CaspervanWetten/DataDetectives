from Database import Database 
import pandas as pd
import os as os

db=Database()


LIST = os.listdir('C:\\Users\\valke\\OneDrive\\Documenten\\GitHub\\DataDetectives\\dashboard\\data')

for file in LIST:
    path = os.path.join('C:\\Users\\valke\\OneDrive\\Documenten\\GitHub\\DataDetectives\\dashboard\\data', file)
    with open(path):
        df = pd.read_csv(path)
    a = file.split(".")[0]
    db._load_data(a=df)
    print(file.split(".")[0])    
    
    
    
print(db._fetch_data("electricity",False))


