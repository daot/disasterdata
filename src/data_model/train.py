import numpy as np
import pandas as pd
from preprocess import preprocess_dataframe, bsk_preprocessor
import joblib


df = pd.read_csv('./datasets/lahaina-label.tsv',sep='\t') # assuming column called ['text']
df = preprocess_dataframe(df) # cleaned text is now in df['cleaned']

# Do model training here

