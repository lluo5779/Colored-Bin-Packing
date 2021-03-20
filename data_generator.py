import json
import random
import numpy as np

random.seed(123)

# NUM_COLORS = 4
# NUM_ITEMS = 30
# BIN_SIZE = 10

NC = [2, 4, 8]
NI = [2 ** i for i in range(5, 9)]
BS = [2 ** i for i in range(3, 5)]
BIN_SIZE_DISCREPANCY = [0, 1 / 4, 1 / 2, 3 / 4]
BIN_SIZE_DISCREPANCY_str = ['0', 'quarter', 'half', 'three-quarters']
NUM_SEEDS = 5

for NUM_COLORS in NC:
    for NUM_ITEMS in NI:
        for BIN_SIZE in BS:
            for DISCREPANCY, Dstr in zip(BIN_SIZE_DISCREPANCY, BIN_SIZE_DISCREPANCY_str):
                for seed in range(NUM_SEEDS):
                    ITEM_SIZES = [random.randint(1, int(BIN_SIZE - DISCREPANCY * BIN_SIZE)) for item in
                                  range(NUM_ITEMS)]
                    COLORS = [random.randint(0, NUM_COLORS - 1) for item in ITEM_SIZES]
                    for c in range(0, NUM_COLORS):
                        if c not in COLORS:
                            COLORS[c] = c

                    data = {
                        "NUM_COLORS": NUM_COLORS,
                        "NUM_ITEMS": NUM_ITEMS,
                        "BIN_SIZE": BIN_SIZE,
                        "DISCREPANCY": DISCREPANCY,
                        "ITEM_SIZES": ITEM_SIZES,
                        "COLORS": COLORS
                    }

                    with open("./data/instance_NC{}_NI{}_BS{}_D{}_S{}.json".format(str(NUM_COLORS).zfill(3),
                                                                                   str(NUM_ITEMS).zfill(3),
                                                                                   str(BIN_SIZE).zfill(3), Dstr, seed),
                              'w+') as f:
                        json.dump(data, f)
                    print("Finished ./data/instance_NC{}_NI{}_BS{}_D{}_S{}.json".format(NUM_COLORS, NUM_ITEMS, BIN_SIZE,
                                                                                        Dstr, seed))

# MAX_COLORS_IN_BIN = 40

# [Color][Item]
# ITEM_SIZES = [ np.random.choice(np.arange(2,6), p = [0.4, 0.3, 0.2, 0.1]) for item in range(NUM_ITEMS) ]
