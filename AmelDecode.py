import pandas as pd
import re

def _extract_single(handle_list, tech_list):
    """
    Funzione interna da chiamare se il file contiene una sola prova
    """

    #formatted_data è il dizionario che contiene tutte le informazioni di una singola prova (tech, units, datapoints)
    #I diversi formatted_data vanno inseriti in data_list per essere processati
    #Da extract_single() uscirà un solo formatted_data, mentre da extract_multiple() ne usciranno diversi
    data_list = list()
    formatted_data = dict()

    formatted_data["tech"] = tech_list[0]

    #Trovo unità di misura
    for line in handle_list:
        if not line.startswith("Xscale"):
            continue

        units = re.findall("\= (\S*)", line)

        for i in range(len(units)):
            if units[i] == "ï¿½A":
                units[i] = "µA"
            if units[i] == "ï¿½V":
                units[i] = "µV"
            if units[i] == "°K":
                units[i] = "K"

        formatted_data["units"] = units

    #Trovo inizio datapoints
    begin_row = 0
    for line in handle_list:
        if not line.startswith("Analysis-Cycle"):
            continue

        begin_row = handle_list.index(line) + 2
        break
    
    #Trovo fine datapoints
    end_row = handle_list[begin_row:].index("\n") + begin_row - 1
    
    if begin_row == 0 or end_row == 0:
        return None
    else:
        formatted_data["datapoints"] = (begin_row, end_row)

    data_list.append(formatted_data)

    return data_list

def _extract_multiple(handle_list, tech_list):
    """
    Funzione interna da chiamare se il file contiene prove multiple
    """
    
    #formatted_data è il dizionario che contiene tutte le informazioni di una singola prova (tech, units, datapoints)
    #I diversi formatted_data vanno inseriti in data_list per essere processati
    #Da extract_single() uscirà un solo formatted_data, mentre da extract_multiple() ne usciranno diversi
    data_list = list()


    #Trovo gli inizi dei dati
    begin_list = list()

    for line in handle_list:
        if not line.startswith("Analysis-Cycle"):
            continue

        begin_list.append(handle_list.index(line)+2)

    for i in range(len(tech_list)):
        formatted_data = dict()

        formatted_data["tech"] = tech_list[i]

        #Trovo le unità di misura
        formatted_data["units"] = list()

        for line in handle_list:
            if not line.startswith("MethodSequence."):
                continue
            
            unit_vec = line.split("=")[1].replace(" ", "").rstrip().split(",")

            if unit_vec[i] == "ï¿½A":
                unit_vec[i] = "µA"

            if unit_vec[i] == "ï¿½V":
                unit_vec[i] = "µV"

            if unit_vec[i] == "ï¿½K" or unit_vec[i] == "°K":
                unit_vec[i] = "K"

            formatted_data["units"].append(unit_vec[i])

        #Trovo i datapoints
        end_row = 0
        for line in handle_list[begin_list[i]:]:
            if not line.startswith("\n"):
                continue
            
            end_row = handle_list[begin_list[i]:].index(line) + begin_list[i] - 1

        formatted_data["datapoints"] = (begin_list[i], end_row)
        
        data_list.append(formatted_data)
        
    return data_list

def extract(file_path):
    """
    Estrae i dati da un singolo file e restituisce una lista di dataframe, uno per ogni prova contenuta nel file.

    file_path: Percorso del file da cui estrarre i dati
    """

    extracted_df_list = list()

    with open(file_path, "r") as handle:
        lines_list = handle.readlines()

        #Estraggo le tecniche usate nel file e le piazzo in tech_list.
        #In base a len(tech_list) si decide se usare extract_single o extract_multiple

        #In ogni caso _extract_single o _multiple restituiscono una lista di dizionari.
        #Nei dizionari sono contenute le seguenti informazioni:
        #tech:  Tipo di esperimento
        #units: Unità di misura
        #datapoints: Un tuple che contiene riga di inizio e fine di ogni prova

        tech_list = list()

        for line in lines_list:
            if line.startswith("Technique"):
                line = line.replace(" ","").replace("Technique=","")
                for tech in line.rstrip().split(","):
                    if tech:
                        tech_list.append(tech)        
                break

        if len(tech_list) == 1:
            test_list = _extract_single(lines_list, tech_list)
        elif len(tech_list) > 1:
            test_list = _extract_multiple(lines_list, tech_list)
        else:
            return None

        #Per ogni prova estratta in test_list, vengono estratti i dati dal file

        for test in test_list:
            
            #header_list è la lista dei titoli delle colonne, che vengono decisi in base all'unità di misura
            header_list = list()

            for unit in test["units"]:

                header = "Unknown"

                if "V" in unit:
                    header = "Potential [" + unit + "]"
                elif "A" in unit:
                    header = "Current [" + unit + "]"
                elif "s" in unit:
                    header = "Time [" + unit + "]"
                elif "K" in unit:
                    header = "Temperature [" + unit + "]"

                header_list.append(header)

            #Inserisco i dati contenuti tra i due datapoints in un dataframe che ha per colonne header_list

            data_to_insert = list()
            data_beg = test["datapoints"][0]
            data_end = test["datapoints"][1]

            for line in lines_list[data_beg:data_end]:
                    
                newline = list()

                for item in line.split():
                    newline.append(float(item))

                data_to_insert.append(newline)

            extracted_df = pd.DataFrame(data_to_insert, columns=header_list)

            extracted_df_list.append(extracted_df)

    return extracted_df_list

def extract_norm(file_path):
    """
    Estrae i dati da un singolo file e restituisce una lista di dataframe, uno per ogni prova contenuta nel file.
    I valori di corrente e potenziale vengono normalizzati ad A e V, indipendentemente dall'unità di misura di partenza

    file_path: Percorso del file da cui estrarre i dati
    """

    extracted_df_list = list()

    with open(file_path, "r") as handle:
        lines_list = handle.readlines()

        #Estraggo le tecniche usate nel file e le piazzo in tech_list.
        #In base a len(tech_list) si decide se usare extract_single o extract_multiple

        #In ogni caso _extract_single o _multiple restituiscono una lista di dizionari.
        #Nei dizionari sono contenute le seguenti informazioni:
        #tech:  Tipo di esperimento
        #units: Unità di misura
        #datapoints: Un tuple che contiene riga di inizio e fine di ogni prova

        tech_list = list()

        for line in lines_list:
            if line.startswith("Technique"):
                line = line.replace(" ","").replace("Technique=","")
                for tech in line.rstrip().split(","):
                    if tech:
                        tech_list.append(tech)        
                break

        if len(tech_list) == 1:
            test_list = _extract_single(lines_list, tech_list)
        elif len(tech_list) > 1:
            test_list = _extract_multiple(lines_list, tech_list)
        else:
            return None

        #Per ogni prova estratta in test_list, vengono estratti i dati dal file

        for test in test_list:
            
            #header_list è la lista dei titoli delle colonne
            header_list = list()

            for unit in test["units"]:

                header = "Unknown"

                if "V" in unit:
                    header = "Potential [V]"
                elif "A" in unit:
                    header = "Current [A]"
                elif "s" in unit:
                    header = "Time [" + unit + "]"
                elif "K" in unit:
                    header = "Temperature [" + unit + "]"

                header_list.append(header)

            #Inserisco i dati contenuti tra i due datapoints in un dataframe che ha per colonne header_list

            data_to_insert = list()
            data_beg = test["datapoints"][0]
            data_end = test["datapoints"][1]

            for line in lines_list[data_beg:data_end]:
                    
                newline = list()

                for item in line.split():
                    newline.append(float(item))

                data_to_insert.append(newline)

            extracted_df = pd.DataFrame(data_to_insert, columns=header_list)

            #Correggo le colonne in base all'unità di misura

            if "mV" in test["units"]:
                extracted_df["Potential [V]"] = extracted_df["Potential [V]"].div(1000)
            elif "µV" in test["units"]:
                extracted_df["Potential [V]"] = extracted_df["Potential [V]"].div(1000000)
            elif "nV" in test["units"]:
                extracted_df["Potential [V]"] = extracted_df["Potential [V]"].div(1000000000)

            if "mA" in test["units"]:
                extracted_df["Current [A]"] = extracted_df["Current [A]"].div(1000)
            elif "µA" in test["units"]:
                extracted_df["Current [A]"] = extracted_df["Current [A]"].div(1000000)
            elif "nA" in test["units"]:
                extracted_df["Current [A]"] = extracted_df["Current [A]"].div(1000000000)
            
            extracted_df_list.append(extracted_df)

    return extracted_df_list