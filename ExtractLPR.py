import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def extract_LPR(potential, current, E_range_min, E_range_max, min_score=0.0, complete=False):
    """
    Funzione per estrarre resistenza di polarizzazione lineare da un dataframe.
    La resistenza viene calcolata come la pendenza della retta che interpola di dati del potenziale in funzione della corrente.
    Nello specifico, il calcolo viene fatto solo all'interno di un certo range di potenziale intorno al potenziale di corrosione.
    È possibile specificare un valore di R^2 minimo al di sotto del quale la funzione restituisce None.

    potential: colonna del dataframe in cui si trova il potenziale
    current: colonna del dataframe in cui si trova la corrente
    E_range_min: estremo inferiore del range rispetto ad E_corr in cui calcolare l'LPR
    E_range_max: estremo superiore del range rispetto ad E_corr in cui calcolare l'LPR
    min_score: R^2 minimo da considerare
    complete: Se vero, restituisce un tuple con i_corr, E_corr, coefficiente angolare e intercetta
    """

    E_range_min = E_range_min/1000
    E_range_max = E_range_max/1000

    i_corr = current.abs().min()
    i_corr_index = current.abs().idxmin()

    E_corr = potential.loc[i_corr_index]

    df = pd.DataFrame({"potential": potential, "current": current})

    pot = df[((df["potential"] - E_corr) > E_range_min) & ((df["potential"] - E_corr) < E_range_max)]["potential"].values
    curr =  df[((df["potential"] - E_corr) > E_range_min) & ((df["potential"] - E_corr) < E_range_max)]["current"].values.reshape((-1,1))

    #Necessario per evitare di passare array vuoti al modello
    if len(curr) == 0 or len(pot) == 0:
        return None

    model = LinearRegression()
    model.fit(curr, pot)

    LPR = model.coef_
    interc = model.intercept_

    if model.score(curr, pot) > min_score:
        if complete == True:
            return (i_corr, E_corr, float(LPR), float(interc))
        else:
            return float(LPR)
    else:
        return None