import pandas as pd
import tkinter as tk
import NewareExtractor
import EISconverter
import AreaCV

# Elenco dei comandi
commands_dict = {
    "1": "Neware Extractor",
    "2": "EIS to Bio-logic",
    "3": "Supercap analysis",
    "4": "Plate and strip",
    # "H": "Help",
    "Q": "Quit"
}

def PrintInitMsg():
    init_msg = str()
    for command in commands_dict:
        init_msg = init_msg + f"{command} - {commands_dict[command]}\n"
    print(init_msg)

if __name__ == "__main__":
    print("Welcome to SEElib.")

    while(True):
        print("What do you want to do?\n")
        PrintInitMsg()
        user_command = input("> ")

        match user_command:
            case "1":
                NewareExtractor.Extract()
            case "2":
                EISconverter.Convert()
            case "3":
                AreaCV.GetArea()
            case "H":
                print("Help message.")
            case "Q":
                print("Bye!")
                quit()
            case _:
                print("\nCommand not recognized!")
