import numpy as np
import pandas as pd
from preprocess import preprocess
import joblib

def main():
    df = pd.read_csv('./datasets/lahaina-label.tsv',sep='\t')
    df = preprocess(df)

    # Do model training here

if __name__ == "__main__":
    main()