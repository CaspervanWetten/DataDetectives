import pycountry
import eurostat as es

def MonthlyElectricity():
    try: 
        # Specificy the pivotal columns, geo\\time = country, indic=kind of energy
        id_vars = ['geo\\TIME_PERIOD', 'indic']
        # The indic column uses internal EU indicators, we'll translate them to what we want with this dictionary
        indicator_dictionary = {"IS-PEL-GWH" : "Production", "IS-CEL-GWH" : "Consumption", "IS-IEL-GWH" : "Imports"}
        alpha2_to_alpha3 = {country.alpha_2: country.alpha_3 for country in pycountry.countries}


        df = es.get_data_df("EI_ISEN_M")
        df.drop(columns=['freq','s_adj'], inplace=True)
        df = df.melt(id_vars=id_vars, var_name='Date', value_name='GWH')
        df = df[df['indic'].isin(indicator_dictionary.keys())]
        df['indic'] = df['indic'].replace(indicator_dictionary)
        df = df.dropna(subset=['GWH'])
        df['geo\\TIME_PERIOD'] = df['geo\\TIME_PERIOD'].map(alpha2_to_alpha3)
        return df
    except Exception as e:
        print(f"quit with {e} as error")
