import pandas as pd
import numpy as np

def extract(filename):
    with open(filename, "r") as handle:
        raw_input = handle.readlines()

    for i in range(len(raw_input)):
        raw_input[i] = raw_input[i].replace("\xb0", "°").replace("\t", ",")
        raw_input[i] = raw_input[i].split(",")

    df = pd.DataFrame(raw_input)
    df.replace("", np.NaN, inplace=True)
    df[2] = df[2].fillna(method='ffill')
    
    print(df)

    #print(df.loc[:500,2].to_string())

extract("test.csv")