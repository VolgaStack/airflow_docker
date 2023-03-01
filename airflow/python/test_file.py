import pandas as pd
import locale

date = '2021-01-01'

url = f'https://api.exchangerate.host/timeseries?start_date={date}&end_date={date}&base=EUR&symbols=USD&format=csv'

df = pd.read_csv(url)
rate_list = df["rate"].to_list()

if rate_list:
    rate = rate_list.pop().replace(',','.')


print(rate)

