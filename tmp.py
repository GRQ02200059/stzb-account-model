import pandas as pd
data = pd.read_csv("Account.csv")
data.to_excel("Account.xlsx")