import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_hdf('./tier1/t1_run0.lh5', stop=100)

print(df.columns)
