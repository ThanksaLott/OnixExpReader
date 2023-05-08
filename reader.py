# -*- coding: utf-8 -*-
"""
Created on Mon May  8 15:15:30 2023

@author: lott
GS d- s:+ a- C++ t 5 X R tv b+ D+ G e+++ h r++ 
"""

import os
import numpy as np
import zipfile
import pandas as pd


def verify_columns(header:list):
    if not (header[-1].decode("utf-8").strip().split("\t") == 
            list(columns_dtypes.keys())):
        raise ValueError("Columns in header do not match columns in "
                         + "'columns_dtype'")

def findheader(lines:list, prompt:str = "TimeStamp"):
    """
    Finds the line in which the header ends

    Parameters
    ----------
    lines : list
        List of utf-8 encoded strings.
    prompt : str, optional
        Keyword with which the last line of the header starts.
        The default is "TimeStamp".

    Returns
    -------
    int
        line in which the header ends.

    """
    for i, line in  list(enumerate(lines)):
        if line.decode("utf-8").startswith(prompt):
            return i # return row when found the header
    return -1 # return -1 when no header is found

def findtail(lines:list, prompt:str = "### Acquisition Ended") -> int:
    """
    Finds the line in which the tail starts

    Parameters
    ----------
    lines : list
        List of utf-8 encoded strings.
    prompt : str, optional
        Keyword with which the first line of the tail starts.
        The default is "### Acquisition Ended".

    Returns
    -------
    int
        line in which the tail starts.

    """
    for i, line in  reversed(list(enumerate(lines))):
        if line.decode("utf-8").startswith(prompt):
            return i # return row when found the tail
    return -1 # return -1 when no tail is found

def seperateheadertail(lines:list) -> [list, list, list]:
    """
    Seperates the header and tail from the data. Returns each as lists.

    Parameters
    ----------
    lines : list
        List of utf-8 encoded strings..

    Returns
    -------
    [list, list, list]
        List of utf-8 encoded header, data and tail.
        
    """
    headerline = findheader(lines)
    tailline = findtail(lines)
    header = lines[:headerline+1]
    data = lines[headerline+1:tailline]
    tail = lines[tailline:]
    return [header, data, tail]

def rundata_from_(file:str) -> pd.DataFrame:
    """
    Generates a pandas Dataframe containing the RunData of an .OnixExp file.
    
    Removes Header and tail.

    Parameters
    ----------
    file : str
        Path to the .OnixExp file.

    Returns
    -------
    data_df : pd.DataFrame
        Pandas dataframe containing the RunData of an .OnixExp file.

    """
    archive = zipfile.ZipFile(file, "r")
    rundata = archive.open("RunData.txt")
    lines = rundata.readlines()
    header, data, tail = seperateheadertail(lines)
    
    data_list= []
    for line in data:
        vals = line.decode("utf-8").strip().split("\t")
        
        temp_list = []
        
        for ii in range(0, len(vals)): # correct the datatypes
            temp_list.append(list(columns_dtypes.values())[ii](vals[ii]))
        data_list.append(temp_list)
    
    data_df = pd.DataFrame(data_list, columns=columns_dtypes.keys())
    return data_df

def get_wells(df):
    """
    returns a dataframe that only contains the wells
    """
    return df.loc[:,["V1","V2","V3","V4","V5","V6","V7","V8"]]

def insert_pressure(df):
    """
    Returns a new DataFrame, where "X" is replaced with the pressure in a well.
    """
    new_df = df.copy()
    for well in ["V1","V2","V3","V4","V5","V6","V7","V8"]:
        new_df[well] = np.where(new_df[well] == "X", new_df["X"], 0)
    return new_df

def plot_all_wells(df):
    """
    A quick overview plot to see whether the pattern looks good.
    """
    import matplotlib.pyplot as plt
    plt.figure()
    for well in ["V1","V2","V3","V4","V5","V6","V7","V8"]:
        plt.plot(df["TimeStamp"], df[well], label = well)
    plt.legend()
    plt.xlabel("Time / s")
    plt.ylabel("pressure / kPa")
    plt.show()

if __name__ == "__main__":
    
    columns_dtypes = {
    "TimeStamp" : int, # in seconds
    "Step" : int,
    "Repetition" : int,
    "V1" : str, # Well 1
    "V2" : str, # Well 2
    "V3" : str,
    "V4" : str,
    "V5" : str,
    "V6" : str,
    "V7" : str,
    "V8" : str,
    "X" : float, # pressure
    "Y" : float,
    "Temperature" : float,
    "Gas" : str,
    "Flags0" : str,
    "Flags1" : str,
    "Flags2" : str,
    "Discrete_Input" : int,
    "StatusRegister" : int,
    "RunState" : int
    }
    
    file = "test/example_experiment.OnixExp"
    data_df = rundata_from_(file)
    plot_all_wells(insert_pressure(data_df))