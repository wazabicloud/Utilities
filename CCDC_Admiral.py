import AdmiralDecode
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from scipy import integrate
import os

def CCDC_elab():

    final_columns = [
        "Charge Capacity [mAh]",
        "Discharge Capacity [mAh]",
        "Charge energy [mWh]",
        "Discharge energy [mWh]",
        "Coulombic efficiency [%]",
        "Energy efficiency [%]",
        "Average charge power [mW]",
        "Average discharge power [mW]",
        "Average charge current [mA]",
        "Average discharge current [mA]",
        "Average charge voltage [V]",
        "Average discharge voltage [V]",
        "Begin time [s]"
    ]

    final_df = pd.DataFrame(columns = final_columns)

    print("Choose files to analyse:")

    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()
    file_list = filedialog.askopenfilenames(parent = root, title="Choose CV files", filetypes = [("CSV files", ".csv")])

    for file in file_list:
        try:
            df_list = AdmiralDecode.extract_simple(file, normalize = True, split = True)

            for i, temp_df in enumerate(df_list):
                if i % 2 == 1 or i == len(df_list):
                    continue

                df = pd.concat([df_list[i], df_list[i + 1]], ignore_index = True)

                time = df.columns[2]
                work_v = df.columns[3]
                curr = df.columns[5]
                counter_v = df.columns[8]
                pot = "Voltage (V)"
                power = "Power (W)"

                df[pot] = df[work_v] - df[counter_v]
                df[curr] = df[curr] * 1000

                df[power] = df[pot].abs() * df[curr].abs()

                chg_df = df[df[curr] > 0]
                dchg_df = df[df[curr] < 0]

                chg_cap = np.abs(integrate.simpson(chg_df[curr], chg_df[time]) / 3600)
                dchg_cap = np.abs(integrate.simpson(dchg_df[curr], dchg_df[time]) / 3600)

                chg_energy = np.abs(integrate.simpson(chg_df[power], chg_df[time]) / 3600)
                dchg_energy = np.abs(integrate.simpson(dchg_df[power], dchg_df[time]) / 3600)

                chg_power = chg_df[power].mean()
                dchg_power = dchg_df[power].mean()

                chg_avg_pot = np.abs(chg_df[pot].mean())
                dchg_avg_pot = np.abs(dchg_df[pot].mean())

                chg_avg_curr = chg_df[curr].mean()
                dchg_avg_curr = dchg_df[curr].mean()

                begin_time = df[time].min()

                coul_eff = dchg_cap / chg_cap * 100
                ener_eff = dchg_energy / chg_energy * 100
                
                final_df.loc[len(final_df)] = [chg_cap, dchg_cap, chg_energy, dchg_energy, coul_eff, ener_eff, chg_power, dchg_power, chg_avg_curr, dchg_avg_curr, chg_avg_pot, dchg_avg_pot, begin_time]

        except:
            filename = os.path.basename(file)

            print(f"Error encountered while elaborating {filename}. It will be excluded from the final report.")

    final_df.sort_values(by = "Begin time [s]", inplace = True)
    final_df["Cycle number"] = final_df.index + 1

    cols = final_df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    final_df = final_df[cols]

    if len(final_df) > 0:
        print("Choose report destination:")

        output_file = filedialog.asksaveasfile(title = "Save analysis result as:", mode="w", defaultextension=".csv", filetypes = [("CSV files", ".csv")])

        if output_file == None:
            print("Invalid save destination!")
        else:
            final_df.to_csv(output_file, index = False, line_terminator = "\n")
            print(f"Saved as {output_file.name}")
            output_file.close()
    else:
        print("The final report is empty, this might be due to errors in the individual cycles elaboration.")

if __name__ == "__main__":
    CCDC_elab()