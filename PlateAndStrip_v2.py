import NewareDecode
from scipy.signal import argrelextrema
import tkinter as tk
from tkinter import filedialog

def PlateAndStrip():
    print("Choose files to analyse:")

    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()
    file_list = filedialog.askopenfilenames(parent = root, title = "Choose CV files", filetypes = [("CSV files", ".csv")])

    if len(file_list) == 0:
        print("No file was selected!")
    else:
        for file in file_list: