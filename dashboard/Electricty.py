import pycountry
import eurostat as es
import pandas as pd

def MonthlyElectricity(csv=False):
    try: 
        # Eurostat uses 'indic' with internal identifiers, this is the dictionary (pun intended) that translates those to a language we normies understand
        indicator_dictionary = {"IS-PEL-GWH" : "Production", "IS-CEL-GWH" : "Consumption", "IS-IEL-GWH" : "Imports"}
        # Use this list to translate the alpha_2 country codes into the alpha_3 used by Dash
        alpha2_to_alpha3 = {country.alpha_2: country.alpha_3 for country in pycountry.countries}

        
        df = es.get_data_df("EI_ISEN_M") #downloads the dataset 
        df['country'] = df['geo\\TIME_PERIOD'].map(alpha2_to_alpha3) #Add the alpha_3 country codes to column "country"
        df = df[df['indic'].isin(indicator_dictionary.keys())] #Filter out all the indics not in our dictionary, we don't use these (this is data cleaning!), other indics include: Natural gas imports, motor spirit refinery (no i dont know what this is), inland delivieries of brown coal (which, as we all know, is much more dangerous than it's cuddly cousins brown and polar-coal)
        df['indicator'] = df['indic'].replace(indicator_dictionary) #Use the dictionary to replace the names
        df.drop(columns=['freq','s_adj', 'geo\\TIME_PERIOD', 'indic'], inplace=True) #Drop the unnecesary columns (ALSO DATA CLEANING!)
        df = df.melt(id_vars=['country', 'indicator'], var_name='date', value_name='gwh') # flip the column from horizontal do vertical based around the Date column
        #The following 3 lines split the Date column into a seperate Year and Month column
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df = df[["country", "year", "month", "gwh", "indicator"]] #I wanted to have all dataframes in (more or less) the same order. No I'm not autistic and thinking such questions is rude >:()
        df = df.dropna(subset=['gwh', 'country']) #Drop the ones of which we don't have data ('GWH') and which aren't part of our country list (The data also has aggregate EU data which converts to an empty Country cell after the alpha_2->3 mapping, we use this to filter those out)
        if csv:
            df.to_csv("csv/MonthlyElectricity.csv")
        return df
    except Exception as e:
        print(f"quit with \n{e} \nas error")


def TypesOfEnergy(csv=False):
    try: 
        # Eurostat uses 'siec' with internal identifiers, this is the dictionary (pun intended) that translates those to a language we normies understand
        value_mapping = {'C0000X0350-0370': 'Solid fossil fuels','C0350-0370': 'Manufactured gases','P1000': 'Peat and peat products','S2000': 'Oil shale and oil sands','O4000XBIO': 'Oil and petroleum products (excluding biofuel portion)','G3000': 'Natural gas','RA000': 'Renewables and biofuels','W6100_6220': 'Non-renewable waste','N900H': 'Nuclear heat','H8000': 'Heat','E7000': 'Electricity','TOTAL': 'Total'}
        # Use this list to translate the alpha_2 country codes into the alpha_3 used by Dash
        alpha2_to_alpha3 = {country.alpha_2: country.alpha_3 for country in pycountry.countries}

        df = es.get_data_df("ten00122") #downloads the dataset 
        df['country'] = df['geo\\TIME_PERIOD'].map(alpha2_to_alpha3) #Add the alpha_3 country codes to column "country"
        df['indicator'] = df['siec'].replace(value_mapping) #Use the dictionary to replace the names, we use ALL indicators for this dataset
        df.drop(columns=['freq','nrg_bal','unit', 'geo\\TIME_PERIOD', 'siec'], inplace=True) #Drop the unnecesary columns (ALSO DATA CLEANING!)
        df = df.melt(id_vars=['indicator', 'country'], var_name='year', value_name='ktoe') # flip the column from horizontal do vertical based around the Date column
        df = df[["country", "year", "ktoe", "indicator"]] #I wanted to have all dataframes in (more or less) the same order. No I'm not autistic and thinking such questions is rude >:()
        df = df.dropna(subset=['ktoe', 'country'])#Drop the ones of which we don't have data ('KTOE') and which aren't part of our country list (The data also has aggregate EU data which converts to an empty Country cell after the alpha_2->3 mapping, we use this to filter those out)
        if csv: #Soms wil je een CSV, en soms niet :)))))
            df.to_csv("csv/TypesOfElectricity.csv")
        return df
    except Exception as e:
        return f"quit with \n{e} \nas error"

