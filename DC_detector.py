import pandas as pd
import matplotlib.pyplot as plt
import csv

# Choose different seg number to drop different part of timeseries data
seg = 12
# set threshold 10 pip in forex
thre = 10 * 1e-4
ins = "EURUSD"
# time frame 5 minutes
timeframe = "5"
train_data_length = 288
# Look pivot_len bars right and pivot_len bars left side to find local extremes
pivot_len = 10


# load data
def find_delimiter(filename):
    sniffer = csv.Sniffer()
    with open(filename) as fp:
        delimiter = sniffer.sniff(fp.read(5000)).delimiter
    return delimiter

data_path = f"./data_price/{ins}{timeframe}.csv"
data = pd.read_csv(data_path, delimiter=find_delimiter(data_path))
df = data.iloc[-(seg+1)*(train_data_length):-seg*(train_data_length) ,4].reset_index(drop=True)


# find all local extremes
price_indexes , indexes = [] , []

for i in range(pivot_len , len(df)-pivot_len):
    if df[i] == max(df[i-pivot_len : i+pivot_len]) or df[i] == min(df[i - pivot_len: i + pivot_len]):
        indexes.append(i)
        price_indexes.append(df[i])

# qualified means the price difference between two extremes is more than the specified threshold
# find qualified local extremes
ext_index , ext_price  = [] ,  []
ext_index.append(indexes[0])
ext_price.append(price_indexes[0])
pointer , old_pointer = 0,  0
DC_index , DC_price = [] , []


# init flag variable to find the first trend (upward or downward)
for i in range(1, len(indexes)):
    if price_indexes[i] > price_indexes[0]+thre :
        flag = "max"
        break
    if price_indexes[i] < price_indexes[0] - thre :
        flag = "min"
        break


while True:
    old_pointer = pointer
    for k in range(pointer , len(indexes)):
        if price_indexes[k] - ext_price[-1] > thre and flag == "max":
            ext_price.append(price_indexes[k])
            ext_index.append(indexes[k])
            pointer = k
            for j in range(k , len(indexes)):
                if ext_price[-1] < price_indexes[j] :
                    ext_price.pop()
                    ext_price.append(price_indexes[j])
                    ext_index.pop()
                    ext_index.append(indexes[j])
                    pointer = j
                elif ext_price[-1] - price_indexes[j]  > thre :
                    break

            for idx in range(ext_index[-1] , len(df)):
                if ext_price[-1] - df[idx] > thre:
                    DC_price.append(df[idx])
                    DC_index.append(idx)
                    break

            flag = "min"
            break

        elif ext_price[-1] - price_indexes[k]  > thre and flag == "min":
            ext_price.append(price_indexes[k])
            ext_index.append(indexes[k])
            pointer = k
            for j in range(k, len(indexes)):
                if ext_price[-1] > price_indexes[j]:
                    ext_price.pop()
                    ext_price.append(price_indexes[j])
                    ext_index.pop()
                    ext_index.append(indexes[j])
                    pointer = j
                elif price_indexes[j] - ext_price[-1] > thre:
                    break

            for idx in range(ext_index[-1], len(df)):
                if  df[idx] - ext_price[-1]  > thre:
                    DC_price.append(df[idx])
                    DC_index.append(idx)
                    break

            flag = "max"
            break
    if pointer == old_pointer:
        break

ext_price = ext_price[1:]
ext_index = ext_index[1:]


plt.figure(figsize=(12, 6))
plt.scatter(ext_index , ext_price, color="#ebb134", s=400, alpha=0.7)
plt.scatter(indexes, price_indexes, color="green", s=100, alpha=0.7)
plt.scatter(DC_index, DC_price, color="crimson", s=100, alpha=0.7)
for i in range(len(DC_index)):
    plt.plot([DC_index[i],ext_index[i]] , [DC_price[i],ext_price[i]]
             , linestyle ="dashed" , color="crimson" , linewidth = 3)
plt.plot(df , color="black")
plt.legend(["Qualified Local Extremes" , "All Local Extremes" , "Directional Changes (DC)" , "DC Section"])
plt.title(f"threshold = {thre * 1e4} pip  , instrument = {ins}")
plt.show()



