import requests
import zipfile
import os
import pycountry
import pandas as pd
import regex as re
from tqdm import tqdm
from p_tqdm import p_map
import requests
import time
# Dit zijn meer algehele, saaie helper functies:

def FilterEmptyDict(input_dict):
    """
    Filter out empty entries (values) from a dictionary.
    Args: input_dict (dict): The dictionary to filter.
    Returns: dict: A new dictionary with empty entries removed.
    """
    return {key: val for key, val in input_dict.items() if val}


def DownloadFile(url, write_location, max_retries=3):
    """
    Download a file from a given URL and save it to a specified location with retry and error handling.
    
    Args:
        url (str): The URL of the file to download.
        write_location (str): The path where the downloaded file will be saved.
        max_retries (int): Maximum number of download retries in case of network errors.
        
    Returns:
        str or None: The path to the saved file or None if the download fails.
    """
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an error for non-200 status codes
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading new temperature data")
            with open(write_location, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            return write_location
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                print(f"Download failed on attempt {attempt + 1}. Retrying...")
                time.sleep(5)  # Add a delay before retrying
            else:
                print(f"Download failed after {max_retries + 1} attempts. Error: {e}")
                return None

def ExtractZip(zip_file, extract_path):
    """
    Extract a ZIP file to a specified location.
    Args: zip_file (str): The path to the ZIP file to extract; extract_path (str): The path where the ZIP file will be extracted.
    Returns: str or file: The path to the extracted folder or an error message if extraction fails.
    """
    if not os.path.exists(extract_path):
            os.makedirs(extract_path)
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        total_files = len(zip_ref.infolist())
        with tqdm(total=total_files, desc="Extracting data") as pbar:
            for member in zip_ref.infolist():
                zip_ref.extract(member, extract_path)
                pbar.update(1)
    return extract_path

def GenerateStationIDs(folderPath):
    """
    Reads the stations file and generates a dict with IDs and the countries
    Args: the folderpath to the stations file
    Return: dictionary: {ID : Country}; note that {country} is formatted in ISO3116 alpha-2
    """
    with open(folderPath + 'stations.txt') as f:
        lines = f.readlines()
        lines = lines[17:]
        f.close()
    reg = r"[\s]*(\d+),([\w\W\s]*),([a-zA-Z]{2})"
    CountryIDs = {}
    for line in lines:
        m = re.match(reg, line)
        if m:
            country = m.group(3)
            stationId = str(m.group(1)).zfill(5)
            CountryIDs[stationId] = country
    return CountryIDs

def RenameFiles(folderPath, CountryIDs, reg=r"TG_STAID0(\d*)", group=1):
    """
    Renames all the files in a folder if it matches the given group in the regex, then renames the file
    Args: the folderpath, dictionary that looks like {regex_match : new_name}, regex, group
    Return: none
    """
    for file in os.listdir(folderPath):
        match = re.match(reg, file)
        if not match:
            continue
        stationId = match.group(group)
        newName = CountryIDs[stationId] + stationId + '.txt'
        os.rename(os.path.join(folderPath, file), os.path.join(folderPath, newName))

def ConvertAlpha2(code):
    return pycountry.countries.get(alpha_2=code).alpha_3

# def CleanTemperatureDataframes(results, dataframeDict, folderPath = "data/temperature/", save = False):
#     """
#     Cleans and processes temperature dataframes.
#     Parameters: results (list): A list of tuples containing country names and their respective dataframes.
#         dataframeDict (dict): A dictionary to store the cleaned dataframes.
#         folderPath (str): The path to the folder where the cleaned dataframes will be saved.
#         save (bool): A flag indicating whether to save the cleaned dataframes to disk.
#     Returns: dict: A dictionary containing cleaned dataframes grouped by country name.
#     """
#     for result in results:
#         country = result[0]
#         df = result[1]
#         if country in dataframeDict.keys():
#             dataframeDict[country].append(df)
#     #Filter out the empty countries:
#     dataframeDict = {ConvertAlpha2(key): val for key, val in dataframeDict.items() if val}
#     #Average the temperatures of the same months
#     for country, dfList in dataframeDict.items():
#             concated = pd.concat(dfList, ignore_index=True)
#             dataframeDict[country] = concated.groupby('Date')['Temperature'].mean().round().reset_index()
    
    
#     #Legacy Saving Code, I'm unsure if it actually works
#     if save:    
#         for key, value in dataframeDict.items():
#             value.to_csv(folderPath+str(key)+".csv", index=False)
#     return dataframeDict

# def CombineSavedCSV(folder_path):
#     #Dit is Legacy Code, ik kan je oprecht niet met zekerheid vertellen of het werkt 
#     csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
#     combined_df = pd.DataFrame(columns=["Date"])
#     for file in csv_files:
#         df = pd.read_csv(os.path.join(folder_path, file))
#         df.set_index('Date', inplace=True)
#         country_name = os.path.splitext(file)[0]
#         df.rename(columns={'Temperature': country_name}, inplace=True)
#         combined_df = combined_df.join(df, how='outer')
#     combined_df = combined_df.reindex(sorted(combined_df.columns), axis=1)
#     return combined_df

# def CombineCSVDict(dict):
    # """
    # Combines multiple pandas DataFrames into a single DataFrame.
    # Parameters: dict: A dictionary containing the DataFrames to be combined.
    # Returns: A DataFrame containing data from all input DataFrames, matched on the Date column.
    # """
    # dfs = [df.set_index('Date').rename(columns={"Temperature" : country}) for country, df in dict.items()]
    # result = pd.concat(dfs, axis=1).reset_index()
    # result = pd.melt(result, id_vars=['Date'], var_name='Country', value_name='Temperature')
    # result = result.dropna(subset=['Temperature'])
    # result = result[result['Date']>= '2000']
    # return result

def DownloadTemperatureData(url, folderPath):
    """
    Downloading AND unzipping, what more do you want?!
    """
    download = DownloadFile(url, folderPath+"download.zip")
    ExtractZip(download, folderPath)

def ClassifyTemperatureData(folderPath):
    """
    Calls both the StationID generator and RenameFiles function; thus generates the station IDs and renames all the files
    """
    dict = GenerateStationIDs(folderPath)
    RenameFiles(folderPath, dict)

def RemoveFile(file):
    """
    Removes a file
    Args: File, the path to the file that will be removed
    """
    os.remove(file)


# Alles samenkomend ziet het er zo uit:
def TemperatureDownloader(csv=False):
    """
    Downloads, processes, and cleans temperature data from the KNMI Climate Explorer.
    """
    url = "https://knmi-ecad-assets-prd.s3.amazonaws.com/download/ECA_blend_tg.zip" #Yes we have a hardcoded URL, but according to archive.org the website hasn't changed (except for updated data) since 2013 
    # https://web.archive.org/web/20130331004540/https://www.ecad.eu/dailydata/index.php
    folderPath = "csv/" #Where to store the download.zip and unpack the .txt files
    EUList = ['AT', 'BE', 'BG', 'HR', 'CY', 'DK', 'EE', 'FI', 'FR', 'DE', 'IE', 'IT', 'LV', 'LU', 'NL', 'NO', 'PL', 'RO', 'ES', 'SE', 'CH', 'GB'] #The stations have alpha_2 internal ID's, this are the ID's we're using.

    # Prepare all the data for processing
    # TODO If internet dies halfway through the download, it fails and the function errors out
    try:
        #Downloads and unzips the required temperature in the provided path
        DownloadTemperatureData(url, folderPath)
        #The 'classify' function searches for the country the temperature measuring station is stationed in as well as the stationID, and renames the .txt file to [country][stationID]. This could be done in the following algorithm, but for debugging purposes we chose to keep it explicit. Also makes it easier to detect if data is relevant for us or not
        ClassifyTemperatureData(folderPath)

        files = [folderPath+filename for filename in os.listdir(folderPath) if filename.endswith(".txt")] #Get all the .txt file names in the folderpath, these are the [country][stationID files]  
        for txt in tqdm(files, desc="Preparing the data"):
            if not re.match(r"[a-zA-Z/]*/([a-zA-Z\ ]+)(\d+)" ,txt):
                print(f"No match with {txt}") #The dataset includes some metadata .txt files, such as 'stations.txt', 'date_timestamp.txt' or 'elements.txt', we use this regex to filter those out.
                continue
            if re.match(r"[a-zA-Z/]*/([a-zA-Z\ ]+)(\d+)", txt).group(1) in EUList: #The first part of the regex (i.e. group(1)) catches the country name, while the second part (i.e. group(2)) catches the stationID.
                country = ConvertAlpha2(re.match(r"[a-zA-Z/]*/([a-zA-Z\ ]+)(\d+)", txt).group(1))
            df = pd.read_csv(txt, header=None, skiprows=21, names=["STAID", "SOUID", "DATE", "TG", "Q_TG"], usecols=["DATE", "TG", "Q_TG"]) #The internal formatting of the .txt's is a little weird. In summary, the first 21 lines are 'metadata', while the lines after are more like a csv formatted as a.txt; This pandas function reads all the required data into a dataframe, and discards the unneccesary data
            df = df[df["Q_TG"].astype(int).isin([0, 1])] #The Q_TG indicates the 'quality' of the data measurement, 0 is quality, 1 is probably good, and 9999 is unreliable. We only take into consideration the data of qualities 0 or 1 
            df["TG"] = df["TG"].astype(float) / 10 #The data is stored in integer format, in steps of 0.1 degrees celsius (so a value of 100 meant 10 degrees C). We will be using floats either way, so we convert the data to the correct value immediately
            df["DATE"] = pd.to_datetime(df["DATE"], format="%Y%m%d").dt.strftime('%Y-%m') #The date is formatted as a raw string, so we convert the DATE column to a pandas.datetime value
            df = df[["DATE", "TG"]].rename(columns={'DATE': 'date', 'TG': 'temperature'}) #Rename the columns into something human-readable
            df = df.groupby('date')['temperature'].mean().round().reset_index() #The temperature data is daily. This algorithm up untill now has saved the DATE value as [year]-[month] but it still goes line by line, meaning it'll collect 31 different values for October either way. This function is used to calculate the arithmic mean to get a reliable 'average' temparature of that country in that given month. This is a chosen trade-off between data granularity to improve data clearity and usability
            df = df.dropna(subset=['temperature']) #Drop all NA' temperatures
            df = df[df['date']>= '2000'] #Drop all temperatures before the year 2000
            #The following 3 lines split the Date column into a seperate Year and Month column
            df['date'] = pd.to_datetime(df['date'])
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            df['country'] = country #Add a country column with the value of the current country
            df = df[["country", "year", "month", "temperature"]] #I wanted to have all dataframes in (more or less) the same order. No I'm not autistic and thinking such questions is rude >:£
            # db._load_data(exists="append", temperature=df) #Append the currently existing temperature table (which will be empty at the start of the loop) with the newly generated dataframe
            
        toClean = [os.path.join(folderPath, file) for file in os.listdir(folderPath) if file.endswith(".txt") or file.endswith(".zip")] #Remove the leftover .txt and .zip files, which total to about ~4 gigs
        p_map(RemoveFile, toClean, desc="Cleaning leftover files")

        if csv: #
            df.to_csv("csv/Temperature.csv")
        return
    except Exception as e:
        print(f"quit with \n {e} \n as error")


TemperatureDownloader()
