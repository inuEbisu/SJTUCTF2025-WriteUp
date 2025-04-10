import pickle
import os
import base64
import code

table = []
if os.path.exists("./table/table.pickle"):
    with open("./table/table.pickle", "rb") as f:
        table = pickle.load(f)
else:
    for subtask in range(0, 95):
        with open(f"./table/table_{subtask:02}.pickle", "rb") as f:
            table.extend(pickle.load(f))
    with open(f"./table/table.pickle", "wb") as f:
        pickle.dump(table, f)

print(len(table))
print(table[:10])