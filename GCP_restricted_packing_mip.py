import random
import numpy as np
from utils import *
import os

##
from docplex.mp.model import Model


def MIP_model_restricted(params):
    NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, Timelimit, SEED = params

    print("*** Running MIP restricted instance NUM_COLORS{} NUM_ITEMS{} BIN_SIZE {} DISCREPANCY {} SEED {}".format(NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY,SEED))

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

    # # Something weird here
    for bin in range(NUM_BINS):
        for item in range(NUM_ITEMS):
            for item2 in range(item + 1, NUM_ITEMS):
                if COLORS[item] == COLORS[item2]:
                    # print("WTF ", item, item2, COLORS[item], COLORS[item2], bin)
                    mdl.add_constraint(
                        mdl.sum(X[i][bin] for i in range(item + 1, item2) if COLORS[i] != COLORS[item]) >= (
                                    X[item][bin] + X[item2][bin] - 1),
                        ctname='special'
                    )

    for bin in range(NUM_BINS - 1):
        mdl.add_constraint(
            bin_used[bin] >= bin_used[bin + 1]
        )

    for bin in range(NUM_BINS):
        for item in range(NUM_ITEMS):
            mdl.add_constraint(
                bin_used[bin] >= X[item][bin]
            )

    mdl.minimize(mdl.sum(bin_used))

    try:
        mdl.set_time_limit(Timelimit)
        msol = mdl.solve(log_output=True)

        print(msol)
        print(mdl.solve_details)

        Xs = []
        for item in range(NUM_ITEMS):
            for bin in range(NUM_BINS):
                if msol[X[item][bin]]:
                    Xs.append(bin)
                    break

        mdl._myInstance = (NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, SEED)

        if solution_checker(Xs, params, 'restricted_mip'):
            write_to_global_mip(msol, mdl, 'restricted')
    except Exception as err:
        print(err)
        write_to_global_failed(params, 'restricted_mip', is_bad_solution=False)

        # print(COLORS)
        # print(ITEM_SIZES)


##
if __name__ == "__main__":
    random.seed(123)

    NUM_COLORS = 20
    NUM_ITEMS = 20
    BIN_SIZE = 10

    MAX_COLORS_IN_BIN = 40

    # [Color][Item]
    # ITEM_SIZES = [ np.random.choice(np.arange(2,6), p = [0.4, 0.3, 0.2, 0.1]) for item in range(NUM_ITEMS) ]

    ITEM_SIZES = [random.randint(1, BIN_SIZE) for item in range(NUM_ITEMS)]
    COLORS = [random.randint(0, NUM_COLORS - 1) for item in ITEM_SIZES]
    COLORS[:5] = [0, 1, 2, 0, 0]

    NUM_BINS = NUM_ITEMS

    MIP_model_restricted(NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, 10)
