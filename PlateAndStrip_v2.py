import NewareDecode
from scipy.signal import argrelextrema
import tkinter as tk
import numpy as np
from tkinter import filedialog
import pandas as pd

def PlateAndStrip():
    print("Choose files to analyse:")

    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()
    file_list = filedialog.askopenfilenames(parent = root, title = "Choose Neware files:", filetypes = [("CSV files", ".csv"), ("TXT files", ".txt")])

    if len(file_list) == 0:
        print("No file was selected!")
    else:
        while True:
            print("Choose extraction method:\n\t1 - Normal\n\t2 - One point every n\n\t3 - Only maxima and minima\n")
            extract_mode = input("> ")

            match extract_mode:
                # Estrazione normale
                case "1":
                    break

                # Un punto ogni n
                case "2":
                    print("Which value should I use for n?\n")   
                    while(True):
                        n = input("> ")
                        try:
                            n = int(n)
                            if n > 0:
                                break
                            else:
                                print("n must be a positive number!\n")
                        except:
                            print("n must be an integer number!\n")
                    break

                # Solo massimi e minimi
                case "3":
                    print("Choose a range for maxima and minima search\n")   
                    while(True):
                        n = input("> ")
                        try:
                            n = int(n)
                            if n > 0:
                                break
                            else:
                                print("n must be a positive number!\n")
                        except:
                            print("n must be an integer number!\n")
                    break
                case _:
                    print("\nCommand not recognized!")

        for file in file_list:
            df = NewareDecode.extract_datapoints(file)

            pot = df.columns[4]
            curr = df.columns[5]
            time = df.columns[-1]
            id = df.columns[1]

            final_df = pd.DataFrame(columns = [time, curr, pot])

            match extract_mode:
                # Estrazione normale
                case "1":
                    final_df = df[[time, curr, pot]]
                
                # Uno ogni n
                case "2":
                    final_df = df[df.index % n == 0][[time, curr, pot]]

                # Solo massimi e minimi
                case "3":
                    for cycle in df[id].unique():
                        sub_df = df[df[id] == cycle]

                        if sub_df[curr].mean() > 0:
                            extremes = sub_df.iloc[argrelextrema(sub_df[pot].values, np.greater_equal, order=n)[0]][[time, curr, pot]]
                            extremes.sort_values(by=[time], inplace=True, ignore_index=True)
                        else:
                            extremes = sub_df.iloc[argrelextrema(sub_df[pot].values, np.less_equal, order=n)[0]][[time, curr, pot]]
                            extremes.sort_values(by=[time], inplace=True, ignore_index=True)

                        final_df = pd.concat([final_df, extremes.iloc[[0]]], ignore_index = True)



PlateAndStrip()