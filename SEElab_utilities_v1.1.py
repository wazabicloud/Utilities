import pandas as pd
import tkinter as tk
import NewareExtractor
import EISconverter
import AreaCV
import PlateAndStrip_v2
import CCDC_Admiral
import sys

# Elenco dei comandi
commands_dict = {
    "1": "Neware Extractor",
    "2": "EIS to Bio-logic",
    "3": "Supercap analysis",
    "4": "Plate and strip",
    "5": "Admiral Charge/Discharge",
    "H": "Help",
    "Q": "Quit"
}

def PrintInitMsg():
    init_msg = str()
    for command in commands_dict:
        init_msg = init_msg + f"{command} - {commands_dict[command]}\n"
    print(init_msg)

def PrintHelpMsg():
    print("""   NewareExtractor: A tool to extract data from neware software. The tool can read .csv and .txt files obtained from "General Report" and divide them in three separate entities for cycles, steps and individual datapoints. It can't read .nda files directly.

    EIS to Bio-logic: A tool to convert EIS files obtained from Admiral potentiostats to a file that can be read by EC-lab. It creates .txt files that can be imported into EC-lab, then when they are imported, EC-lab automatically creates a .mpr file in the same directory.

    Supercap analysis: A tool to perform quantitative analysis of super capacitors cyclic voltammograms. By default it will consider only the last cycle of the file. Currently only Admiral files are supported.

    Plate and Strip: A tool to analyse plate and strip curves obtained from Neware files. It only accepts .csv and .txt files extracted with "General report".

    Admiral Charge/Discharge: Admiral does not provide experiment summary for custom charge discharge experiments. This tool does that
    """)

if __name__ == "__main__":
    print("Welcome to SEElib.")

    while(True):
        print("What do you want to do?\n")
        PrintInitMsg()
        user_command = input("> ")

        match user_command.lower():
            case "1":
                NewareExtractor.Extract()
            case "2":
                EISconverter.Convert()
            case "3":
                AreaCV.GetArea()
            case "4":
                PlateAndStrip_v2.PlateAndStrip()
            case "5":
                CCDC_Admiral.CCDC_elab()
            case "h":
                PrintHelpMsg()
            case "q":
                print("Bye!")
                sys.exit()
            case _:
                print("\nCommand not recognized!")