import pandas as pd
import re
import datetime as dt

def extract_simple(file_path: str, normalize=False):

    """
    Extracts data from a single file and organizes it
    according to the different techniques used.

    Returns a list of dataframes, each element corresponding
    to a different step.

    Parameters
    ----------
    file_path : str
        The path of the file from which the data must be extracted.

    normalize : bool, optional
        If true, all the data regarding potential and current will
        be provided in V and A respectively.
    """

    extracted_df_list = list()

    with open (file_path, "r") as handle:
        lines_list = handle.readlines()

    #Trovo la riga degli header che è già indicata nel file

    header_line = int(lines_list[1].strip().split(" : ")[1]) - 1

    headers = lines_list[header_line].rstrip().split("\t")

    #Elaboro le righe coi dati
    for i in range(len(lines_list[header_line+1:])):

        i = i + header_line + 1

        #Divido in colonne
        lines_list[i] = lines_list[i].replace(",", ".").rstrip().split("\t")

        for j in range(len(lines_list[i])):

            #Trasformo i numeri indicati in notazione scientifica se lo sono
            if re.search("\+[0-9]{3}|\-[0-9]{3}", lines_list[i][j]) != None:

                base = float(lines_list[i][j].split("E")[0])
                exp = float(lines_list[i][j].split("E")[1])
                
                lines_list[i][j] = base * (10 ** exp)

            #Altrimenti devo comunque trasformare i numeri in floats
            else:
                try:
                    lines_list[i][j] = float(lines_list[i][j])
                except:
                    continue

    #Creo il dataframe

    df = pd.DataFrame(lines_list[header_line+1:], columns=headers)

    if normalize == True:
        if "Ewe/mV" in df.columns.tolist():
            df["Ewe/mV"] = df["Ewe/mV"].div(1000)
            df.rename(columns={"Ewe/mV": "Ewe/V"}, inplace=True)

        if "<I>/mA" in df.columns.tolist():
            df["<I>/mA"] = df["<I>/mA"].div(1000)
            df.rename(columns={"<I>/mA": "<I>/A"}, inplace=True)

    extracted_df_list.append(df)

    return extracted_df_list

def extract_complete(file_path:str, normalize=False):
    """
    Extracts data from a single file and organizes it
    according to the different techniques used.

    Returns a list of dictionaries, each element corresponding
    to a different step.
    The dictionaries contain the following keys:
        name: name of the file
        test: name of the technique used
        data: extracted data
        points: number of points
        timestamp: time at which the file was created

    Parameters
    ----------
    file_path : str
        The path of the file from which the data must be extracted.

    normalize : bool, optional
        If true, all the data regarding potential and current will
        be provided in V and A respectively.
    """

    extracted_df_list = list()

    with open (file_path, "r") as handle:
        lines_list = handle.readlines()

    #Trovo la riga degli header che è già indicata nel file

    header_line = int(lines_list[1].strip().split(" : ")[1]) - 1

    headers = lines_list[header_line].rstrip().split("\t")

    #Elaboro le righe coi dati
    for i in range(len(lines_list[header_line+1:])):

        i = i + header_line + 1

        #Divido in colonne
        lines_list[i] = lines_list[i].replace(",", ".").rstrip().split("\t")

        for j in range(len(lines_list[i])):

            #Trasformo i numeri indicati in notazione scientifica se lo sono
            if re.search("\+[0-9]{3}|\-[0-9]{3}", lines_list[i][j]) != None:

                base = float(lines_list[i][j].split("E")[0])
                exp = float(lines_list[i][j].split("E")[1])
                
                lines_list[i][j] = base * (10 ** exp)

            #Altrimenti devo comunque trasformare i numeri in floats
            else:
                try:
                    lines_list[i][j] = float(lines_list[i][j])
                except:
                    continue

    #Creo il dataframe

    df = pd.DataFrame(lines_list[header_line+1:], columns=headers)

    if normalize == True:
        if "Ewe/mV" in df.columns.tolist():
            df["Ewe/mV"] = df["Ewe/mV"].div(1000)
            df.rename({"Ewe/mV": "Ewe/V"}, axis="columns", inplace=True)

        if "<I>/mA" in df.columns.tolist():
            df["<I>/mA"] = df["<I>/mA"].div(1000)
            df.rename({"<I>/mA": "<I>/A"}, axis="columns", inplace=True)

    #Trovo altri parametri
    test = lines_list[3].rstrip()

    for i in range(len(lines_list)):
        if not "Acquisition started" in lines_list[i]:
            continue
        
        raw_date = lines_list[i].split(" : ")[1].rstrip()

        date_line = raw_date.split()[0]
        time_line = raw_date.split()[1]

        day = int(date_line.split("/")[0])
        month = int(date_line.split("/")[1])
        year = int(date_line.split("/")[2])
        hour = int(time_line.split(":")[0])
        minute = int(time_line.split(":")[1])
        second = int(time_line.split(":")[2])

        date = dt.datetime(year, month, day, hour, minute, second)

    new_dict = {
        "name": file_path,
        "test":  test,
        "data": df,
        "points": len(df),
        "timestamp": date
    }

    extracted_df_list.append(new_dict)

    return extracted_df_list