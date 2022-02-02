import AdmiralDecode
from pandas import DataFrame
from numpy import where, trapz
from tkinter import Tk, filedialog
import os

def GetArea():
    print("Choose files to analyse:")

    root = Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()
    file_list = filedialog.askopenfilenames(parent = root, title="Choose CV files", filetypes = [("CSV files", ".csv")])

    report = "File name, IdV [AV], Potential window [V], Scan rate [V/s], Capacity [F]"

    time = "Elapsed Time (s)"
    pot = "Working Electrode (V)"
    curr = "Current (A)"
    ramo = "Ramo"
    newcycle = "New cycle"

    if len(file_list) == 0:
        print("No files were selected!")
    else:
        for file in file_list:
            filename = os.path.basename(file)
            print(f"Analysis of {filename}...")

            try:
                df: DataFrame
                df = AdmiralDecode.extract_simple(file, normalize = True)[0]

                # Traslazione curva
                min_curr = df[curr].min()
                df[curr] = df[curr] - min_curr

                # Divisione in ramo catodico e anodico
                df[ramo] = where(
                    (df[pot].diff(1) > 0),
                    1,
                    0
                )

                # Trovo l'inizio dei nuovi cicli
                df[newcycle] = where(
                    (df[ramo].diff(1) == 0),
                    False,
                    True
                )

                new_begin = df[df[newcycle] == True].index[-2]
                df = df.iloc[new_begin:]

                # Calcolo scan rate e finestra di potenziale
                sub_df = df[df[ramo] == 0]

                d_pot = (sub_df[pot].max() - sub_df[pot].min())
                d_time = (sub_df[time].max() - sub_df[time].min())

                sc_rate = (d_pot / d_time)

                pot_window = df[pot].max() - df[pot].min()

                # Calcolo aree

                sub_df = df[df[ramo] == 0]
                c_area = trapz(sub_df[curr], sub_df[pot])

                sub_df = df[df[ramo] == 1]
                a_area = trapz(sub_df[curr], sub_df[pot])

                total_area = a_area + c_area
                capacity = total_area / (2 * pot_window * sc_rate)

                report_new_line = f"\n{filename}, {total_area}, {pot_window}, {sc_rate}, {capacity}"
                report = report + report_new_line
                print("Done!")
            except:
                print("Failed!")

    if len(report.split("\n")) == 1:
        print("The final report is empty! Please check that you have selected the correct files.")
    else:
        print("Choose report destination:")

        output_file = filedialog.asksaveasfile(title = "Save analysis result as:",mode='w', defaultextension=".csv", filetypes = [("CSV files", ".csv")])

        if output_file == None:
            print("Invalid save destination!")
        else:
            output_file.write(report)
            output_file.close()
            print(f"Saved as {output_file.name}")

if __name__ == "__main__":
    GetArea()