import pandas as pd
import numpy as np
import re

def _extract_csv(raw_input):
    for i in range(len(raw_input)):
        raw_input[i] = raw_input[i].replace("\xb0", "°").replace("\t", ",").replace("\n", "")
        raw_input[i] = raw_input[i].split(",")

    df = pd.DataFrame(raw_input)
    df.replace("", np.NaN, inplace=True)

    # Filtering data according to which dataframe it belongs to:

    # Columns of the single dataframes
    df.loc[0:2, 1] = "Header"

    # Cycles
    df.loc[(df[0].notna()) & (df[1].isna()), 1] = "Cycle"

    # Steps
    df.loc[(df[2].notna()) & (df[1].isna()), 1] = "Step"

    # Single data
    df.loc[df[1].isna(), 1] = "Data"

    # Once the data is sorted I can fill the cycle and step columns and remove the rest
    df.loc[3:, [0, 2]] = df.loc[3:, [0, 2]].ffill()
    df.loc[[1,2], 0] = "Cycle ID"
    df.loc[2, 2] = "Step ID"
    df.dropna(axis=1, how="all", inplace=True)

    # CYCLES DATA
    cycles_df = df.loc[df[1] == "Cycle", :].copy()
    cycles_df.reset_index(drop=True, inplace=True)
    cycles_df.dropna(axis=1, how="all", inplace=True)

    # Renaming columns
    new_cols = df.loc[0,:].dropna().values
    cycles_df.columns=new_cols
    cycles_df.drop(columns=["Header"], inplace=True)

    # Fixing time
    cycles_df["Plat_Time(h:min:s.ms)"] = cycles_df["Plat_Time(h:min:s.ms)"].apply(lambda x: _convert_time(x))
    cycles_df["Charge Time(h:min:s.ms)"] = cycles_df["Charge Time(h:min:s.ms)"].apply(lambda x: _convert_time(x))
    cycles_df["Discharge Time(h:min:s.ms)"] = cycles_df["Discharge Time(h:min:s.ms)"].apply(lambda x: _convert_time(x))
    cycles_df.rename(columns={
        "Plat_Time(h:min:s.ms)": "Plat_Time(s)",
        "Charge Time(h:min:s.ms)": "Charge Time(s)",
        "Discharge Time(h:min:s.ms)": "Discharge Time(s)"
    }, inplace=True)

    # STEPS DATA

    steps_df = df.loc[df[1] == "Step", :].copy()
    steps_df.reset_index(drop=True, inplace=True)
    steps_df.dropna(axis=1, how="all", inplace=True)

    # Renaming columns
    new_cols = df.loc[1,:].dropna()
    steps_df.columns=new_cols
    steps_df.drop(columns=["Header"], inplace=True)

    # Fixing time
    steps_df["Step Time(h:min:s.ms)"] = steps_df["Step Time(h:min:s.ms)"].apply(lambda x: _convert_time(x))
    steps_df.rename(columns={
        "Step Time(h:min:s.ms)": "Step Duration(s)"
    }, inplace=True)

    # DATAPOINTS

    datapoints_df = df.loc[df[1] == "Data", :].copy()
    datapoints_df.reset_index(drop=True, inplace=True)

    # Renaming columns
    new_cols = df.loc[2,:]
    datapoints_df.columns=new_cols
    datapoints_df.drop(columns=["Header"], inplace=True)
    datapoints_df.dropna(axis=1, how="all", inplace=True)

    # Fixing time
    datapoints_df["Time(h:min:s.ms)"] = datapoints_df["Time(h:min:s.ms)"].apply(lambda x: _convert_time(x))
    datapoints_df.rename(columns={
        "Time(h:min:s.ms)": "Relative Time(s)"
    }, inplace=True)

    # Conversion to numeric

    cycles_df = cycles_df.apply(pd.to_numeric, errors = "ignore")
    steps_df = steps_df.apply(pd.to_numeric, errors = "ignore")
    datapoints_df = datapoints_df.apply(pd.to_numeric, errors = "ignore")
    # cycles_df["Cycle ID"] = pd.to_numeric(cycles_df["Cycle ID"], errors="ignore")

    # steps_df["Step ID"] = pd.to_numeric(steps_df["Step ID"], errors="ignore")
    # steps_df["Cycle ID"] = pd.to_numeric(steps_df["Cycle ID"], errors="ignore")

    # datapoints_df["Step ID"] = pd.to_numeric(datapoints_df["Step ID"], errors="ignore")
    # datapoints_df["Cycle ID"] = pd.to_numeric(datapoints_df["Cycle ID"], errors="ignore")

    # Adding the relative time to each df
    steps_df.loc[0, "Begin Time(s)"] = 0.0
    steps_df.loc[1: , "Begin Time(s)"] = steps_df.iloc[:-1]["Step Duration(s)"].cumsum().values

    for i in cycles_df["Cycle ID"].unique():
        cycles_df.loc[cycles_df["Cycle ID"] == i, "Step Duration(s)"] = steps_df.loc[steps_df["Cycle ID"] == i, "Step Duration(s)"].sum()

    cycles_df.loc[0, "Begin Time(s)"] = 0.0
    cycles_df.loc[1: , "Begin Time(s)"] = cycles_df.iloc[:-1]["Step Duration(s)"].cumsum().values

    for i in datapoints_df["Step ID"].unique():
        datapoints_df.loc[(datapoints_df["Step ID"] == i), "Begin Time(s)"] = datapoints_df.loc[(datapoints_df["Step ID"] == i), "Relative Time(s)"] + steps_df.loc[steps_df["Step ID"] == i, "Begin Time(s)"].sum()

    final_dict = {
        "cycles_df": cycles_df,
        "steps_df": steps_df,
        "datapoints_df": datapoints_df
    }

    return final_dict

def _prepare_txt(raw_input):

    for i, row in enumerate(raw_input):
        raw_input[i] = re.sub(r'(\S)\t+', r'\1,\t', raw_input[i])

        if raw_input[i].startswith("\t\t\t\t\t\t"):
            raw_input[i] = raw_input[i].replace("\t\t\t\t\t\t", ",,\t", 1)
        elif raw_input[i].startswith("\t\t\t"):
            raw_input[i] = raw_input[i].replace("\t\t\t", ",\t", 1)

    return raw_input

def _convert_time(time_string: str):
    """
    Internal function to convert timestamps
    """

    hours = float(time_string.split(":")[0])
    minutes = float(time_string.split(":")[1])
    seconds = float(time_string.split(":")[2])

    total_time = 3600*hours + 60*minutes + seconds

    return total_time

def _convert_time(time_string: str):
    """
    Internal function to convert dates
    """

    hours = float(time_string.split(":")[0])
    minutes = float(time_string.split(":")[1])
    seconds = float(time_string.split(":")[2])

    total_time = 3600*hours + 60*minutes + seconds

    return total_time

def extract_complete(file_path: str):
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
    with open(file_path, "r") as handle:
        raw_input = handle.readlines()

    if ".csv" in file_path:
        with open(file_path, "r") as handle:
            raw_input = handle.readlines()

        final_dict = _extract_csv(raw_input)
    elif ".txt" in file_path:
        with open(file_path, "r") as handle:
            raw_input = handle.readlines()

        final_dict = _extract_csv(_prepare_txt(raw_input))

    return final_dict

def extract_cycles(file_path: str):
    """
    Extracts data from a single file and filters out only
    the lines involving the cycles data.

    Parameters
    ----------
    file_path : str
        The path of the file from which the data must be extracted.
    """

    return extract_complete(file_path)["cycles_df"]

def extract_steps(file_path: str):
    """
    Extracts data from a single file and filters out only
    the lines involving the steps data.

    Parameters
    ----------
    file_path : str
        The path of the file from which the data must be extracted.
    """

    return extract_complete(file_path)["steps_df"]

def extract_datapoints(file_path: str):
    """
    Extracts data from a single file and filters out only
    the individual datapoints.

    Parameters
    ----------
    file_path : str
        The path of the file from which the data must be extracted.
    """

    return extract_complete(file_path)["datapoints_df"]

if __name__ == "__main__":
    print(extract_complete("data.txt"))