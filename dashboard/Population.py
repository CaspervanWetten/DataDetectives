import wbgapi as wb

def DownloadPopulationData(csv=False): 
    EUList_alpha3 = ['BEL', 'BGR', 'CZE', 'DNK', 'DEU', 'EST', 'IRL', 'GRC', 'ESP', 'FRA', 'HRV', 'ITA', 'CYP', 'LVA', 'LTU', 'LUX', 'HUN', 'MLT', 'NLD', 'AUT', 'POL', 'PRT', 'ROU', 'SVN', 'SVK', 'FIN', 'SWE'] #The alpha_3 codes of the countries from which we want dat 
   
    try:
        df = wb.data.DataFrame('SP.POP.TOTL', EUList_alpha3 ,range(2008, 2050, 1)) #Download the correct Dataset
        df = df.reset_index() #It indexes on the economy by default, so we add a new index to translate the economy to Countries (Data cleaning!)
        df.rename(columns = {'economy':'country'}, inplace = True)
        df.columns = df.columns.str.replace("YR", "") #By default the columns are named like "YR2011" but we want just "2011" (Data cleaning!)
        df = df.melt(id_vars=['country'], var_name='year', value_name='population').sort_values(["year", "country"])
        df['population'] = df['population'].astype(int) #The population value defaults to a float (probably because some Americans only count as 2/3th) so we convert them to integers here
        if csv: # 
            df.to_csv("csv/Population.csv")
        return df
    except Exception as e:
        print(f"quit with {e} as error")

