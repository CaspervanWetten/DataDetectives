import wbgapi as wb

def DownloadPopulationData(): 
    EUList_alpha3 = ['BEL', 'BGR', 'CZE', 'DNK', 'DEU', 'EST', 'IRL', 'GRC', 'ESP', 'FRA', 'HRV', 'ITA', 'CYP', 'LVA', 'LTU', 'LUX', 'HUN', 'MLT', 'NLD', 'AUT', 'POL', 'PRT', 'ROU', 'SVN', 'SVK', 'FIN', 'SWE']
   
    try:
        pop_data = wb.data.DataFrame('SP.POP.TOTL', EUList_alpha3 ,range(2008, 2050, 1))
        pop_data_2 = pop_data.reset_index()
        pop_data_2.rename(columns = {'economy':'country'}, inplace = True)
        pop_data_2.columns = pop_data_2.columns.str.replace("YR", "")
        pop_data_2 = pop_data_2.melt(id_vars=['country'], var_name='Date', value_name='Population').sort_values("country")
        return pop_data_2
    except Exception as e:
        print(f"quit with {e} as error")