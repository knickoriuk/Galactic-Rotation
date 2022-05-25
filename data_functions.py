import pickle
import numpy as np
import pandas as pd
import os

def load_pickle(filename):
    ''' (str) -> dict
    Opens a .pkl file in the `Data` folder and returns the data stored inside.
    '''
    file = open('Data/' + filename,'rb')
    data = pickle.load(file,encoding="latin1")
    file.close()
    return data

def create_dataframe(set_on, set_off):
    ''' (dict, dict) -> pandas.DataFrame
    Given two dictionaries of data, both corresponding to the same longitude,
    and both with keys `freqs`, `data`, and `time`, constructs a single
    DataFrame. `set_on` should be the dataset corresponding to a latitude of 0,
    whereas `set_off` is the dataset with non-zero latitude. 
    
    Removes data points near the frequencies 1420, 1419.2, and 1423.5 MHz.
    '''
    data = {'freq': set_on['freqs'],
            'data': set_on['data'].mean(axis=0).flatten(),
            'baseline': set_off['data'].mean(axis=0).flatten()}
    df = pd.DataFrame(data=data)
    
    # Remove the internally-generated emission line at 1420 MHz and other RFI 
    df = df.drop(df[np.abs(df.freq-1420) < 0.01].index)
    df = df.drop(df[np.abs(df.freq-1419.2) < 0.05].index)
    df = df.drop(df[np.abs(df.freq-1423.5) < 0.05].index)
    return df

def get_all_datasets():
    ''' (None) -> dict of pandas.DataFrame
    Iterates through the files in the `Data` folder and creates a dictionary of
    DataFrames, where the key is the longitude corresponding to the DataFrame. 
    '''
    longitudes = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 
                  65, 70, 75, 80, 85, 90, 95, 100, 110, 130, 
                  140, 150, 160, 170, 180, 190, 120]
    data = {}
    file_list = os.listdir('Data')
    file_list.sort()
    file_list = file_list[:-2] # ignore the text file and a folder
    
    for i in range(len(file_list)//2):
        # Reads pickle files in alphabetical order, assuming files are in 
        # pairs for each longitude. See `data_info.txt` for file description.
        filename_norm = file_list[2*i]
        filename_data = file_list[2*i+1]
        set_on = load_pickle(filename_data)
        set_off = load_pickle(filename_norm)
        data[longitudes[i]] = create_dataframe(set_on, set_off)
    return data
