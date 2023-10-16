import requests
import zipfile
import os
import pandas as pd
import regex as re
from tqdm import tqdm
from p_tqdm import p_map, p_umap
from datetime import datetime

# Dit zijn meer algehele, saaie helper functies:

def FilterEmptyDict(input_dict):
    """
    Filter out empty entries (values) from a dictionary.
    Args: input_dict (dict): The dictionary to filter.
    Returns: dict: A new dictionary with empty entries removed.
    """
    return {key: val for key, val in input_dict.items() if val}

def DownloadFile(url, write_location):
    """
    Download a file from a given URL and save it to a specified location.
    Args: url (str): The URL of the file to download; write_location (str): The path where the downloaded file will be saved.
    Returns: str or file: The path to the saved file or an error message if the download fails.
    """
    #TODO If internet shits the bed halfway through, it'll crash, find a way to not have this happen lol
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading data")
        folder_path = os.path.dirname(write_location)
        with open(write_location, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        return write_location
    else:
        return f"Exited with {response.status_code} as error"

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

def GenerateTemperatureDataframes(filePath):
    """
    Generates a pandas DataFrame from a CSV file containing temperature data.
    Parameters: filePath (str): The path to the CSV file, regex matching on (text/)*(countryName)(number)
    Returns: tuple: A tuple containing the country name and the generated DataFrame.
    """
    if re.match(r"[a-zA-Z/]*/([a-zA-Z\ ]+)(\d+)" ,filePath):
        country = re.match(r"[a-zA-Z/]*/([a-zA-Z\ ]+)(\d+)", filePath).group(1)
    else:
        print(f"No match with {filePath}")
        return False, False
    with open(filePath, 'r') as f:
        df = pd.read_csv(f, header=None, skiprows=21, names=["STAID", "SOUID", "DATE", "TG", "Q_TG"], usecols=["DATE", "TG", "Q_TG"])
    df = df[df["Q_TG"].astype(int).isin([0, 1])]
    df["TG"] = df["TG"].astype(float) / 10
    df["DATE"] = pd.to_datetime(df["DATE"], format="%Y%m%d").dt.strftime('%Y-%m')
    df = df[["DATE", "TG"]]
    df = df.rename(columns={'DATE': 'Date', 'TG': 'Temperature'})
    return country, df

def CleanTemperatureDataframes(results, dataframeDict, folderPath = "data/temperature/", save = False):
    """
    Cleans and processes temperature dataframes.
    Parameters: results (list): A list of tuples containing country names and their respective dataframes.
        dataframeDict (dict): A dictionary to store the cleaned dataframes.
        folderPath (str): The path to the folder where the cleaned dataframes will be saved.
        save (bool): A flag indicating whether to save the cleaned dataframes to disk.
    Returns: dict: A dictionary containing cleaned dataframes grouped by country name.
    """
    for result in results:
        country = result[0]
        df = result[1]
        if country in dataframeDict.keys():
            dataframeDict[country].append(df)
    #Filter out the empty countries:
    dataframeDict = {key: val for key, val in dataframeDict.items() if val}
    #Average the temperatures of the same days
    for country, dfList in dataframeDict.items():
            concated = pd.concat(dfList, ignore_index=True)
            dataframeDict[country] = concated.groupby('Date')['Temperature'].mean().round().reset_index()
    #Legacy Saving Code, I'm unsure if it actually works
    if save:
        for key, value in dataframeDict.items():
            value.to_csv(folderPath+str(key)+".csv", index=False)
    return dataframeDict

def CombineSavedCSV(folder_path):
    #Dit is Legacy Code, ik kan je oprecht niet met zekerheid vertellen of het werkt
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    combined_df = pd.DataFrame(columns=["Date"])
    for file in csv_files:
        df = pd.read_csv(os.path.join(folder_path, file))
        df.set_index('Date', inplace=True)
        country_name = os.path.splitext(file)[0]
        df.rename(columns={'Temperature': country_name}, inplace=True)
        combined_df = combined_df.join(df, how='outer')
    combined_df = combined_df.reindex(sorted(combined_df.columns), axis=1)
    return combined_df

def CombineCSVDict(dict):
    """
    Combines multiple pandas DataFrames into a single DataFrame.
    Parameters: dict: A dictionary containing the DataFrames to be combined.
    Returns: A DataFrame containing data from all input DataFrames, matched on the Date column.
    """
    result = pd.DataFrame(columns=["Date"])
    dfs = [df.set_index('Date').rename(columns={"Temperature" : country}) for country, df in dict.items()]
    result = pd.concat(dfs, axis=1)
    return result


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
    Fucks your mother
    Args: File, the path to the file that will be removed
    """
    os.remove(file)


# Alles samenkomend ziet het er zo uit:
def TemperatureDownloader():
    """
    Downloads, processes, and cleans temperature data from the KNMI Climate Explorer.
    """
    url = "https://knmi-ecad-assets-prd.s3.amazonaws.com/download/ECA_blend_tg.zip"
    folderPath = "notebook/data/temperature/"
    EUList = ['AT', 'BE', 'BG', 'HR', 'CY', 'DK', 'EE', 'FI', 'FR', 'DE', 'IE', 'IT', 'LV', 'LU', 'NL', 'NO', 'PL',
              'RO', 'ES', 'SE', 'CH', 'GB']
    dataframeDict = {key: [] for key in EUList}

    # Prepare all the data for processing
    # TODO If internet dies halfway through the download, it fails and the function errors out
    # DownloadTemperatureData(url, folderPath)
    # ExtractZip(folderPath+"download.zip", folderPath)
    # ClassifyTemperatureData(folderPath)

    files = [folderPath + filename for filename in os.listdir(folderPath) if filename.endswith(".txt")]
    results = p_umap(GenerateTemperatureDataframes, files, desc="Preparing the data", num_cpus=4)
    print("Generating temperature mapping...")
    dict = CleanTemperatureDataframes(results, dataframeDict, save=False)
    dict = CombineCSVDict(dict)
    dict.to_csv(folderPath + "TemperatureData.csv")
    toClean = [os.path.join(folderPath, file) for file in os.listdir(folderPath) if file.endswith(".txt")]
    p_map(RemoveFile, toClean, desc="Cleaning leftover files")


TemperatureDownloader()