import pandas as pd
import numpy as np
import AmelDecode
from sklearn.linear_model import LinearRegression

def extract_LPR(df, potential, current, range, min_score=0.0):
    """
    Funzione per estrarre resistenza di polarizzazione lineare da un dataframe.
    La resistenza viene calcolata come la pendenza della retta che interpola di dati del potenziale in funzione della corrente.
    Nello specifico, il calcolo viene fatto solo all'interno di un certo range di potenziale intorno al potenziale di corrosione.
    È possibile specificare un valore di R^2 minimo al di sotto del quale la funzione restituisce None.

    df: dataframe da cui prendere i dati
    potential: colonna del dataframe in cui si trova il potenziale
    current: colonna del dataframe in cui si trova la corrente (o densità di corrente)
    range: range in mV all'interno del quale calcolare la resistenza (10 o 20 mV ideale)
    min_score: R^2 minimo da considerare
    """

    log_curr = df[current].transform(lambda x: np.log10(abs(x)))

    E_corr = df.loc[[log_curr.idxmin()], potential].values[0]

    pot = df.loc[abs(df[potential] - E_corr) < range, potential].values
    curr =  df.loc[abs(df[potential] - E_corr) < range, current].values.reshape((-1,1))
    
    model = LinearRegression()
    model.fit(curr, pot)

    LPR = model.coef_

    if model.score(curr, pot) > min_score:
        return float(LPR)
    else:
        return None