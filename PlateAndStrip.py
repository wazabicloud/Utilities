import pandas as pd
import datetime as dt
import os
import time
import numpy as np
from scipy.signal import argrelextrema
import sys

def max_min(df, n):
    extremes_df = pd.DataFrame()

    #Prima creo una colonna con 0 e 1 in base a se il valore della corrente è positivo o negativo:

    df["curr_sign"] = np.where(df["Current"] > 0, 1, 0)

    #Divido il dataframe nei punti in cui la differenza di curr_sign è diversa da 0

    slice_df = df.groupby((df["curr_sign"].diff(1) != 0).astype("float").cumsum())
    slice_df = slice_df.apply(lambda x: [x.index.min(),x.index.max()])

    for slice in slice_df:
        single_cycle = df.iloc[slice[0]:slice[1]].copy()

        #Se la corrente è negativa cerco un minimo
        if single_cycle.curr_sign.iloc[0] == 0:

            ex_to_add = single_cycle.iloc[argrelextrema(single_cycle.Potential.values, np.less_equal, order=n)[0]][["Time", "Potential", "Current"]]
            ex_to_add.sort_values(by=["Time"], inplace=True, ignore_index=True)
            
            #Altrimenti cerco un massimo
        else:

            ex_to_add = single_cycle.iloc[argrelextrema(single_cycle.Potential.values, np.greater_equal, order=n)[0]][["Time", "Potential", "Current"]]
            ex_to_add.sort_values(by=["Time"], inplace=True, ignore_index=True)
        
        extremes_df = extremes_df.append(ex_to_add.iloc[0])

    return extremes_df[["Time", "Potential", "Current"]]

def extract_data(filepath):
    with open(filepath, "r") as file:

        lines_list = file.readlines()
        lines_lens = []
        checked_elements = []

        list_to_df = []
        begin_time = None

        #Trovo la lunghezza di linea più ricorrente
        max_freq = 0
        comm_len = None

        for line in lines_list:
            lines_lens.append(len(line.split()))

        for i in lines_lens:
            if i in checked_elements:
                continue

            curr_freq = lines_lens.count(i)
            checked_elements.append(i)

            if curr_freq > max_freq:
                max_freq = curr_freq
                comm_len = i

        #Estraggo i dati in base alla lunghezza di linea più ricorrente, perché il neware fa cagare
        for line in lines_list:

            if len(line.split()) != comm_len:
                continue

            else:
                date_line = line.split()[9]
                time_line = line.split()[10]

                day = int(date_line.split("/")[1])
                month = int(date_line.split("/")[0])
                year = int(date_line.split("/")[2])
                hour = int(time_line.split(":")[0])
                minute = int(time_line.split(":")[1])
                second = int(time_line.split(":")[2])

                date = dt.datetime(year, month, day, hour, minute, second)

                if begin_time == None:
                    begin_time = date

                delta_time = date - begin_time
                delta_time = int(delta_time.total_seconds())

                potential = float(line.split()[2])
                current = float(line.split()[3])

                list_to_df.append([delta_time, potential, current])

    df = pd.DataFrame(list_to_df, columns=["Time", "Potential", "Current"])

    return df

# Determinare se il file è un .exe oppure è uno script di python

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

dirpath = os.path.dirname(application_path)

txt_files = []

for filename in os.listdir(dirpath):

    if not ".txt" in filename:
        continue
    else:
        txt_files.append(filename)

if len(txt_files) == 0:
    print("Nessun file .txt trovato!")
    input()
    quit()
else:
    print("Trovato/i", len(txt_files), "file.\n")

    #Scelgo il metodo di estrazione
    while True:
        desmod = input("Scegli il metodo di estrazione:\n\t1 - Normale\n\t2 - Un punto ogni n\n\t3 - Solo massimi e minimi\n\tQ - Chiudi\n")

        if not desmod in ["1", "2", "3", "Q"]:
            print("Comando non riconosciuto.")
            input()
            quit()

        elif desmod == "Q":
            quit()
        
        #Se normale non chiedo altro
        elif desmod == "1":
            break
        
        #Se uno ogni n verifico che sia un numero positivo
        elif desmod == "2":

            n = input("Un punto ogni quanti?\n")         

            try:
                n = int(n)
                if n > 0:
                    break
                else:
                    print("n deve essere un numero positivo!\n")
            except:
                print("n deve essere un numero intero!\n")

        #Se solo massimi e minimi chiedo l'intorno dei massimi e minimi
        elif desmod == "3":

            n = input("Che intorno di punti considero per il calcolo di massimi e minimi?\n")         

            try:
                n = int(n)
                if n > 0:
                    break
                else:
                    print("n deve essere un numero positivo!\n")
            except:
                print("n deve essere un numero intero!\n")

    while True:
        desoutput = input("Scegli il formato di conversione:\n\t1 - Excel\n\t2 - CSV\n\t3 - File di testo\n\tQ - Chiudi\n")

        if not desoutput in ["1", "2", "3", "Q"]:
            print("Comando non riconosciuto.\n")
            continue

        elif desoutput == "Q":
            quit()

        else:
            for filename in txt_files:
                print("Provo a convertire", filename + "...")
                filepath = os.path.join(dirpath, filename)

                #Provo ad estrarre un dataframe di punti
                try:
                    beg = time.time()
                    df = extract_data(filepath)
                    end = time.time()
                    req = end - beg
                    print(filename, "estratto con successo in", req, "secondi.")
                except:
                    print("Errore durante l'estrazione di", filename)
                    continue

                #Se sono richieste modifiche le applico prima di scrivere il nuovo file

                if desmod == "2":

                    final_df = df[df.index % n == 0]

                elif desmod == "3":

                    final_df = max_min(df, n)

                else:

                    final_df = df

                if desoutput == "1":
                    if len(final_df.index) > 1048576:
                        print("\nIl numero di colonne in", filename, "è troppo grande. Verrà creato un file .txt\n")
                        newname = "new_" + filename.split(".")[0] + ".tzt"
                        newpath = os.path.join(dirpath, newname)
                        final_df.to_csv(newpath, index=False)
                        break
                    else:                
                        newname = "new_" + filename.split(".")[0] + ".xlsx"
                        newpath = os.path.join(dirpath, newname)
                        final_df.to_excel(newpath, index=False)

                elif desoutput == "2":
                    newname = "new_" + filename.split(".")[0] + ".csv"
                    newpath = os.path.join(dirpath, newname)
                    final_df.to_csv(newpath, index=False)

                elif desoutput == "3":
                    newname = "new_" + filename.split(".")[0] + ".txt"
                    newpath = os.path.join(dirpath, newname)
                    final_df.to_csv(newpath, index=False)
    
        break

input("Premi un tasto per chiudere la finestra.")
quit()