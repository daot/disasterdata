import numpy as np
import pandas as pd
from preprocess import preprocess
import joblib


df = pd.read_csv('./datasets/lahaina-label.tsv',sep='\t') # assuming column called ['text']
df = preprocess(df) # cleaned text is now in df['cleaned']

# Do model training here

