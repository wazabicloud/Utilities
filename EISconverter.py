import AdmiralDecode
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

# Nomi colonne
adm_freq = "Frequency (Hz)"
adm_assZ = "|Z| (Ohms)"
adm_phase = "Phase (deg)"
adm_ReZ = "Z' (Ohms)"
adm_ImZ = "-Z"" (Ohms)"

bio_freq = "freq/Hz"
bio_assZ = "|Z|/Ohm"
bio_phase = "Phase(Z)/deg"
bio_ReZ = "Re(Z)/Ohm"
bio_ImZ = "-Im(Z)/Ohm"

columns_to_rename = {
    adm_freq: bio_freq,
    adm_assZ: bio_assZ,
    adm_phase: bio_phase,
    adm_ReZ: bio_ReZ,
    adm_ImZ: bio_ImZ
}

def fix_numbers(x):
    x = "{:.7E}".format(x)
    x = str(x)

    pre_exp = x[:-2]
    exp = "0" + x[-2:]

    x = pre_exp + exp
    x = x.replace(".", ",")

    return x

def Convert():
    print("Choose files to analyse:")

    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()
    file_list = tk.filedialog.askopenfilenames(parent = root, title = "Choose Admiral EIS files", filetypes = [("CSV files", ".csv")])

    if len(file_list) == 0:
        print("No file was selected!")
    else:
        for file in file_list:
            dir = os.path.dirname(file)
            filename = os.path.basename(file)
            print(f"Converting {filename}...")
            try:
                df: pd.DataFrame
                df = AdmiralDecode.extract_simple(file)[0]
                
                for header in df.columns:
                    if header in columns_to_rename.keys():
                        continue
                    else:
                        df.drop([header], axis=1, inplace=True)

                df.rename(columns=columns_to_rename, inplace=True)
                
                df = df.applymap(lambda x: fix_numbers(x))

                filename = filename[:-4] + ".txt"
                output_file = os.path.join(dir, filename)

                df.to_csv(output_file, index = False, sep = "\t")
                print("Done!")

            except:
                print("Failed!")

if __name__ == "__main__":
    Convert()