import pycountry
import eurostat as es
#import matplotlib.pyplot as plt

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


def TypesOfEnergy():
    try: 
        # Specificy the pivotal columns, geo\\time = country, indic=kind of energy
        id_vars = ['geo\\TIME_PERIOD', 'indic']
        # The indic column uses internal EU indicators, we'll translate them to what we want with this dictionary
        indicator_dictionary = {"C0000X0350-0370" : "Solid Fossil Fuels", "IS-CEL-GWH" : "Consumption", "IS-IEL-GWH" : "Imports"}
        df = es.get_data_df("ten00122")
        df.drop(columns=['freq','nrg_bal','unit'], inplace=True)
       # df = df.melt(id_vars=id_vars, var_name='Date', value_name='GWH')
       # df = df[df['indic'].isin(indicator_dictionary.keys())]
       # df['indic'] = df['indic'].replace(indicator_dictionary)
        #df.to_csv("ElectricityM.csv", index=False)
        return df
    except Exception as e:
        return f"quit with {e} as error"

df2 = TypesOfEnergy()
#print(df2)
df2.fillna(0, inplace=True)
#change column name to country and also energy_kind
df2 = df2.rename(columns={'geo\\TIME_PERIOD': 'country'})
df2 = df2.rename(columns={'siec': 'energy'})

belgiumdf = df2[df2['country'] == 'AL']
unique_values = belgiumdf['energy'].unique()

# Initialize a dictionary to store the summed energy values for each unique value
summed_energy_data = {}

# Loop through unique values and calculate the sum of energy for each
for value in unique_values:
    summed_energy_data[value] = belgiumdf[belgiumdf['energy'] == value][['2011']].sum()
    
# Print the summed energy for each unique value
for value, total_energy in summed_energy_data.items():
    print(f"Total energy for \n'{value}': {total_energy}")

total_energy_sum = sum(summed_energy_data.values())
print(f"Sum of all total energies: {total_energy_sum}")

# Define the reverse conversion factor
reverse_conversion_factor = 11.631  # GWh per ktoe

# Convert from ktoe to GWh
energy_gwh = total_energy_sum / reverse_conversion_factor

# Print the result
print(f"{total_energy_sum} ktoe is approximately equal to {energy_gwh} GWh")

#remap all energy values 
unique_energy_values = df2['energy'].unique()

# Print the unique energy values
for energy in unique_energy_values:
    print(energy)

# Define a mapping of old values to new values
value_mapping = {
    'C0000X0350-0370': 'Solid fossil fuels',
    'C0350-0370': 'Manufactured gases',
    'P1000': 'Peat and peat products',
    'S2000': 'Oil shale and oil sands',
    'O4000XBIO': 'Oil and petroleum products (excluding biofuel portion)',
    'G3000': 'Natural gas',
    'RA000': 'Renewables and biofuels',
    'W6100_6220': 'Non-renewable waste',
    'N900H': 'Nuclear heat',
    'H8000': 'Heat',
    'E7000': 'Electricity',
    'TOTAL': 'Total'
}
# Replace the values in the DataFrame
df2['energy'] = df2['energy'].replace(value_mapping)

#remove the total attribute for our plots
df2 = df2[df2['energy'] != 'Total']
print(df2.head(10))

df_pivot = df2.melt(id_vars=['energy', 'country'], var_name='year', value_name='consumption')

print(df_pivot)
grouped = df_pivot.groupby(['energy', 'year'])['consumption'].sum().unstack()

energy_groups = df2.groupby('energy')

# # Initialize the plot
# plt.figure()

# for name, group in energy_groups:
#     plt.bar(group.columns[2:], group.iloc[0, 2:], label=name)

# # Customize the plot
# plt.xlabel('Years')
# plt.ylabel('Energy Consumption (GWh)')
# plt.title('Energy Consumption by Type (2011-2021)')
# plt.xticks(rotation=45)
# plt.legend()

# # Show the plot
# plt.show()

