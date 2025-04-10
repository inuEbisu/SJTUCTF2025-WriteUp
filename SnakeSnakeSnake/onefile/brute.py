import check
import base64
import itertools
import pickle
import sys

mystery = base64.b85decode("4mQWHMUK~Hxkx!J>1D@ZuS6TdSv#koy{vj+OgUd8")

# if os.path.exists("../all_combinations.pickle"):
#     with open("../all_combinations.pickle", "rb") as f:
#         all_combinations = pickle.load(f)
# else:
#     all_combinations = [
#         bytes(combination)
#         for combination in itertools.product(range(32, 127), repeat=4)
#     ]

#     with open("../all_combinations.pickle", "wb") as f:
#         pickle.dump(all_combinations, f)

SUBTASK = int(sys.argv[1])
SUBTASK_LEN = 95 ** 3
all_combinations = [
    bytes((SUBTASK + 0x20, ) + combination)
    for combination in itertools.product(range(32, 127), repeat=3)
]

print(all_combinations[0:4])

table = [
    check.transform(b"R3v3r51ng__py7h0n_1s-n07_h4rd!:)" + combination)[28:]
    for combination in all_combinations
]

print("2")

with open(f"../table/table_{SUBTASK:02}.pickle", "wb") as f:
    pickle.dump(table, f)

print("3")