import pandas as pd

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

    with open (file_path, "r") as handle:
        lines_list = handle.readlines()

        #Pulizia dati, da decidere in base a che formato sono i csv:

        if ";" in lines_list[1]:
            for i in range(len(lines_list)):
                lines_list[i] = lines_list[i].replace(",", ".").replace(";", ",").replace("\"", "").rstrip().split(",")
        else:
            for i in range(len(lines_list)):
                lines_list[i] = lines_list[i].replace(";", ",").replace("\"", "").rstrip().split(",")

        #Estrazione header per dataframe
        header_list = lines_list[0]

        #Divisione delle varie prove in dataframes

        extracted_df_list = list()
        data_to_insert = list()
        current_step_number = 0

        for line in lines_list[1:]:

            #Controllo se lo step number cambia

            step_num = line[0].split("_")[0]

            #Se cambia inserisco i dati presenti in data_to_insert in un dataframe e prima di ricominciare svuoto la lista
            if step_num != current_step_number:

                current_step_number = step_num

                extracted_df_list.append(pd.DataFrame(data_to_insert, columns=header_list))

                data_to_insert = []

            #Converto tutti in float e inserisco
            for i in range(len(line)):
                if i < 2:
                    continue
                else:
                    line[i] = float(line[i])

            data_to_insert.append(line)

        #Alla fine del loop devo comunque aggiungere ciò che rimane in un ultimo
        #dataframe e cancellare il primo elemento della lista che è vuoto

        extracted_df_list.append(pd.DataFrame(data_to_insert, columns=header_list))
        del extracted_df_list[0]

        #Normalizzazione se richiesta
        if normalize == True:
            for i in range(len(extracted_df_list)):
                if "Current (mA)" in extracted_df_list[i].columns.tolist():

                    extracted_df_list[i]["Current (mA)"] = extracted_df_list[i]["Current (mA)"].div(1000)
                    extracted_df_list[i].rename(columns={"Current (mA)": "Current (A)"}, inplace=True)

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

    Parameters
    ----------
    file_path : str
        The path of the file from which the data must be extracted.

    normalize : bool, optional
        If true, all the data regarding potential and current will
        be provided in V and A respectively.
    """
    with open (file_path, "r") as handle:
        lines_list = handle.readlines()

        #Pulizia dati, da decidere in base a che formato sono i csv:

        if ";" in lines_list[1]:
            for i in range(len(lines_list)):
                lines_list[i] = lines_list[i].replace(",", ".").replace(";", ",").replace("\"", "").rstrip().split(",")
        else:
            for i in range(len(lines_list)):
                lines_list[i] = lines_list[i].replace(";", ",").replace("\"", "").rstrip().split(",")

        #Estrazione header per dataframe
        header_list = lines_list[0]

        #Divisione delle varie prove in dataframes

        extracted_df_list = list()

        data_to_insert = list()
        current_step_number = 0
        current_test = str()

        for line in lines_list[1:]:

            #Controllo se lo step number cambia

            step_num = line[0].split("_")[0]

            #Se cambia inserisco i dati presenti in data_to_insert in un dataframe e prima di ricominciare svuoto la lista
            if step_num != current_step_number:

                current_step_number = step_num
                complete_df = pd.DataFrame(data_to_insert, columns=header_list)

                #Se chiesta la normalizzazione cambio la corrente
                if normalize == True:
                    if "Current (mA)" in complete_df.columns.tolist():
                        complete_df["Current (mA)"] = complete_df["Current (mA)"].div(1000)
                        complete_df.rename(columns={"Current (mA)": "Current (A)"}, inplace=True)

                test = current_test
                name = file_path
                points = len(complete_df)

                new_element = {
                    "name": name,
                    "test":  test,
                    "data": complete_df,
                    "points": points
                }

                extracted_df_list.append(new_element)

                data_to_insert = []
                current_test = line[1]

            #Converto tutti in float e inserisco
            for i in range(len(line)):
                if i < 2:
                    continue
                else:
                    line[i] = float(line[i])

            data_to_insert.append(line)

        #Alla fine del loop devo comunque aggiungere ciò che rimane in un ultimo
        #dataframe e cancellare il primo elemento della lista che è vuoto

        complete_df = pd.DataFrame(data_to_insert, columns=header_list)

        #Se chiesta la normalizzazione cambio la corrente
        if normalize == True:
            complete_df["Current (mA)"] = complete_df["Current (mA)"].div(1000)
            complete_df.rename(columns={"Current (mA)": "Current (A)"}, inplace=True)

        test = current_test
        name = file_path
        points = len(complete_df)

        new_element = {
            "name": name,
            "test":  test,
            "data": complete_df,
            "points": points
        }

        extracted_df_list.append(new_element)

        del extracted_df_list[0]

    return extracted_df_list