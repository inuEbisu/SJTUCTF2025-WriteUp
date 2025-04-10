import pickle
import os
import base64
import code

table = []
combinations = []
with open("./table/table.pickle", "rb") as f:
    table = pickle.load(f)
with open("./table/all_combinations.pickle", "rb") as f:
    combinations = pickle.load(f)

mystery = base64.b85decode("4mQWHMUK~Hxkx!J>1D@ZuS6TdSv#koy{vj+OgUd8")

try:
    text = b""
    idx = 7
    target = mystery[idx*4 : (idx+1)*4]
    print(target)
    index = table.index(target)
    print(index)
    chunk = combinations[index]
    print(chunk)
    text += chunk

    print(text)
except ValueError as e:
    print(e)
    code.interact(local=locals())