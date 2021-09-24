import requests
import json
import pandas as pd


auctions = pd.read_excel("datasets/auctions.xlsx", sheet_name="Запрос1")

with open('datasets/inn.txt', 'w') as outfile:
    json.dump({'data': list(df["ИНН заказчика"].unique())}, outfile)
