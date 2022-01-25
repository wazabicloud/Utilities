import NewareDecode
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

def Extract():
    print("Choose files to analyse:")

    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()
    file_list = tk.filedialog.askopenfilenames(parent = root, title = "Choose CV files", filetypes = [("CSV files", ".csv")])

    if len(file_list) == 0:
        print("No file was selected!")
    else:
        for file in file_list:
            if ".csv" not in file:
                continue

            dir = os.path.dirname(file)
            filename = os.path.basename(file)

            cycle_path = os.path.join(dir, "cycles")
            steps_path = os.path.join(dir, "steps")
            data_path = os.path.join(dir, "datapoints")

            print("Extracting " + filename)

            with open(file, "r") as handle:
                extracted_data = NewareDecode.extract_complete(file)

            for path_to_check in [cycle_path, steps_path, data_path]:
                if os.path.exists(path_to_check):
                    continue
                else:
                    os.makedirs(path_to_check)

            extracted_data["cycles_df"].to_csv(os.path.join(cycle_path, filename), index = False)
            extracted_data["steps_df"].to_csv(os.path.join(steps_path, filename), index = False)
            extracted_data["datapoints_df"].to_csv(os.path.join(data_path, filename), index = False)

            print(f"{filename} done!")

if __name__ == "__main__":
    Extract()