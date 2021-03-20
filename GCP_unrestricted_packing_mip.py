import random
import numpy as np
from utils import *
import os

##
from docplex.mp.model import Model

def MIP_model_unrestricted(params):
    NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, Timelimit, SEED = params
    print("*** Running MIP Unrestricted with instance NUM_COLORS{} NUM_ITEMS{} BIN_SIZE {} DISCREPANCY {} SEED {}".format(NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY,SEED))

    mdl = Model()

    X = [[mdl.binary_var(name="x_{}_{}".format(item, bin)) for bin in range(NUM_BINS)] for item in range(NUM_ITEMS)]

    bin_used = [mdl.binary_var(name="bin_{}".format(bin)) for bin in range(NUM_BINS)]

    for item in range(NUM_ITEMS):
        mdl.add_constraint(
            mdl.sum(X[item]) == 1,
            ctname='itemsatleastonce_{}'.format(item)
        )

    for bin in range(NUM_BINS):
        mdl.add_constraint(
            mdl.sum(X[item][bin] * ITEM_SIZES[item] for item in range(NUM_ITEMS)) <= BIN_SIZE,
            ctname='binscapacity_{}'.format(bin)
        )

    # # # Something weird here
    # for bin in range(NUM_BINS):
    #     for item in range(NUM_ITEMS):
    #         for item2 in range(item+1, NUM_ITEMS):
    #             if COLORS[item] == COLORS[item2]:
    #                 # print("WTF ", item, item2, COLORS[item], COLORS[item2], bin)
    #                 mdl.add_constraint(
    #                     mdl.sum(X[i][bin] for i in range(item+1, item2)  if COLORS[i] != COLORS[item]) >= (X[item][bin] + X[item2][bin] - 1),
    #                     ctname='special'
    #                 )


    for bin in range(NUM_BINS-1):
        mdl.add_constraint(
            bin_used[bin] >= bin_used[bin+1]
        )

    for bin in range(NUM_BINS):
        for item in range(NUM_ITEMS):
            mdl.add_constraint(
                bin_used[bin] >= X[item][bin]
            )


    color_counts = [mdl.continuous_var_list(NUM_COLORS) for bin in range(NUM_BINS)]
    for bin in range(NUM_BINS):
        for color in range(NUM_COLORS):
            mdl.add_constraint(
                mdl.sum(X[item][bin] for item in range(NUM_ITEMS) if COLORS[item] == color) == color_counts[bin][color]
            )

    for bin in range(NUM_BINS):
        total_count = mdl.sum(color_counts[bin])
        mdl.add_constraint(
            total_count / 2 + 0.5 >= mdl.max(color_counts[bin])
        )


    mdl.minimize(mdl.sum(bin_used))
    try:
        mdl.set_time_limit(Timelimit)
        msol = mdl.solve(log_output=True)
        # print(msol)
        # print(mdl.solve_details)

        Xs = []
        for item in range(NUM_ITEMS):
            for bin in range(NUM_BINS):
                if msol[X[item][bin]]:
                    Xs.append(bin)
                    break

        mdl._myInstance = (NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, SEED)

        if solution_checker(Xs, params, 'unrestricted_mip'):
            write_to_global_mip(msol, mdl, 'unrestricted')

    except Exception as err:
        print(err)
        write_to_global_failed(NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, SEED, 'unrestricted_mip', is_bad_solution=False)
        # print(COLORS)
        # print(ITEM_SIZES)

##
if __name__ == "__main__":
    from os import listdir
    from os.path import isfile, join

    random.seed(123)
    TIMEOUT = 3600
    # NUM_COLORS = 20
    # NUM_ITEMS = 30
    # BIN_SIZE = 10
    # DISCREPANCY = 0
    #
    # MAX_COLORS_IN_BIN = 40
    #
    # # [Color][Item]
    # # ITEM_SIZES = [ np.random.choice(np.arange(2,6), p = [0.4, 0.3, 0.2, 0.1]) for item in range(NUM_ITEMS) ]
    #
    #
    #
    # ITEM_SIZES = [random.randint(1, BIN_SIZE) for item in range(NUM_ITEMS)]
    # COLORS = [random.randint(0,NUM_COLORS-1) for item in ITEM_SIZES]
    # COLORS[:5] = [0, 1,2,0, 0]
    #
    # NUM_BINS = NUM_ITEMS
    # param = NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, 10

    PATH_INSTANCE = "./data/"
    onlyfiles = [f for f in listdir(PATH_INSTANCE) if isfile(join(PATH_INSTANCE, f)) and ".json" in f]
    params = []
    for instance_i, filename in enumerate(onlyfiles):
        print(filename)
        with open("./data/"+filename, 'r') as f:
            data = json.load(f)

        NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS = list(data.values())
        NUM_BINS = NUM_ITEMS
        SEED = filename.split("_S")[1].split('.json')[0]

        params.append([
            NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, TIMEOUT, SEED
        ])

    MIP_model_unrestricted(params[0])
