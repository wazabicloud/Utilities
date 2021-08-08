import pandas as pd
import numpy as np

def extract_complete(filename):
    """
    Extracts data from a single file and organizes it
    in three different dataframes (cycle, step and datapoints).

    Returns a dictionary with three elements:
    cycles_df: dataframe with data related to the whole cycles.
    steps_df: dataframe with data related to the individual steps.
    datapoints_df: dataframe with the single acquisitions.

    Parameters
    ----------
    file_path : str
        The path of the file from which the data must be extracted.
    """
    with open(filename, "r") as handle:
        raw_input = handle.readlines()

    for i in range(len(raw_input)):
        raw_input[i] = raw_input[i].replace("\xb0", "°").replace("\t", ",").replace("\n", "")
        raw_input[i] = raw_input[i].split(",")

    df = pd.DataFrame(raw_input)
    df.replace("", np.NaN, inplace=True)

    # Filtering data according to which dataframe it belongs to:

    # Column names
    df.loc[0:2, 1] = "Header"

    # Cycles
    df.loc[(df[0].notna()) & (df[1].isna()), 1] = "Cycle"

    # Steps
    df.loc[(df[2].notna()) & (df[1].isna()), 1] = "Step"

    # Single data
    df.loc[df[1].isna(), 1] = "Data"

    df.dropna(axis=1, how="all", inplace=True)

    # CYCLES DATA

    cycles_df = df.loc[df[1] == "Cycle", :].copy()
    cycles_df.reset_index(drop=True, inplace=True)
    cycles_df.dropna(axis=1, how="all", inplace=True)

    # Renaming columns
    new_cols = df.loc[0,:].dropna()
    cycles_df.columns=new_cols
    cycles_df.drop([0], inplace=True)
    cycles_df.drop(columns=["Header"], inplace=True)

    # STEPS DATA

    steps_df = df.loc[df[1] == "Step", :].copy()
    steps_df.reset_index(drop=True, inplace=True)
    steps_df.dropna(axis=1, how="all", inplace=True)

    # Renaming columns
    new_cols = df.loc[1,:].dropna()
    steps_df.columns=new_cols
    steps_df.drop(columns=["Header"], inplace=True)

    # DATAPOINTS

    datapoints_df = df.loc[df[1] == "Data", :].copy()
    datapoints_df.reset_index(drop=True, inplace=True)

    # Renaming columns
    new_cols = df.loc[2,:]
    datapoints_df.columns=new_cols
    datapoints_df.drop(columns=["Header"], inplace=True)

    datapoints_df.dropna(axis=1, how="all", inplace=True)

    final_dict = {
        cycles_df: cycles_df,
        steps_df: steps_df,
        datapoints_df: datapoints_df
    }

    return final_dict

def extract_cycles(filename):
    """
    Extracts data from a single file and filters out only
    the lines involving the cycles data.

    Parameters
    ----------
    file_path : str
        The path of the file from which the data must be extracted.
    """

    return extract_complete(filename)["cycles_df"]

def extract_steps(filename):
    """
    Extracts data from a single file and filters out only
    the lines involving the steps data.

    Parameters
    ----------
    file_path : str
        The path of the file from which the data must be extracted.
    """

    return extract_complete(filename)["steps_df"]

def extract_datapoints(filename):
    """
    Extracts data from a single file and filters out only
    the individual datapoints.

    Parameters
    ----------
    file_path : str
        The path of the file from which the data must be extracted.
    """

    return extract_complete(filename)["datapoints_df"]