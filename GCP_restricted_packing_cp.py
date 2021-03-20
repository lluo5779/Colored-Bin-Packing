import random
import numpy as np
from utils import *


from docplex.cp.model import CpoModel
from docplex.cp.model import *
##
def CP_model_restricted(params):
    ##
    NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, Timelimit, SEED = params

    print("*** Running CP Binary Restricted with instance NUM_COLORS{} NUM_ITEMS{} BIN_SIZE {} DISCREPANCY {} SEED {}".format(NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY,SEED))

    mdl = CpoModel()

    X = [mdl.integer_var(min=0, max=NUM_BINS) for item in range(NUM_ITEMS)]

    CP = mdl.integer_var_list(NUM_BINS, min = 0, max=BIN_SIZE)

    for bin in range(NUM_BINS-1):
        mdl.add(
            CP[bin] >= CP[bin+1]
        )

    mdl.add(
        pack(
            CP, [X[item] for item in range(NUM_ITEMS)], ITEM_SIZES
        )
    )


    # CC = [mdl.integer_var_list(NUM_COLORS, min=0, max=BIN_SIZE) for bin in range(NUM_BINS)]
    #
    # for color in range(NUM_COLORS):
    #     mdl.add(
    #         distribute(
    #             [CC[bin][color] for bin in range(NUM_BINS)],
    #             [X[item] for item in range(NUM_ITEMS) if COLORS[item] == color],
    #             [bin for bin in range(NUM_BINS)]
    #         )
    #     )
    #
    # for bin in range(NUM_BINS):
    #
    #     TC = mdl.sum(CC[bin])
    #     MC = mdl.max(CC[bin])
        # mdl.add_kpi(TC, name="TC_{}".format(bin))
        # mdl.add_kpi(MC, name="MC_{}".format(bin))

        # mdl.add(
        #     (TC+mdl.mod(TC, 2))/2  >= MC
        #
        # )
        # mdl.add(
        #     (TC - mdl.mod(TC, NUM_COLORS))/NUM_COLORS >= MC
        # )

        # mdl.add(
        #     mdl.sum(
        #         CC[bin][color] > 0 for color in range(NUM_COLORS)
        #     ) <= MAX_COLORS_IN_BIN
        # )

    for item in range(NUM_ITEMS):
        for item2 in range(item+1, NUM_ITEMS):
            if COLORS[item] == COLORS[item2]:
                mdl.add(
                    mdl.if_then(
                        X[item] == X[item2],
                        mdl.any(
                            [
                                X[i] == X[item] for i in range(item+1, item2+1) if COLORS[i] != COLORS[item]
                            ]
                        )
                        # mdl.count([mdl.element(COLORS, i) for i in range(item, item2+1)], abs(COLORS[item] -1)) > 0
                    )
                )

    # mdl.add(
    #     mdl.minimize(count_different(X))
    # )

    # bins_used = mdl.sum(CP[bin] > 0 for bin in range(NUM_BINS))
    # mdl.add(
    #     mdl.minimize(
    #         bins_used
    #     )
    # )

    mdl.add(
        mdl.minimize(
            mdl.max(X) + 1
        )
    )

    try:
        msol = mdl.solve(TimeLimit = Timelimit)
        mdl._myInstance = (NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, SEED)

        print(ITEM_SIZES)
        print(COLORS)

        if msol:
            print([msol[X[item]] for item in range(NUM_ITEMS)])
            Xs = np.array([msol[X[i]] for i in range(NUM_ITEMS)])
            if solution_checker(Xs, params, 'restricted_cp_binary'):
                write_to_global_cp(msol, mdl, 'restricted_binary')

    except Exception as err:
        print(err)
        write_to_global_failed(params, 'restricted_cp_binary', is_bad_solution=False)


if __name__ == "__main__":

    random.seed(123)

    NUM_COLORS = 4
    NUM_ITEMS = 30
    BIN_SIZE = 10
    DISCREPANCY = 0
    # MAX_COLORS_IN_BIN = 40

    # [Color][Item]
    # ITEM_SIZES = [ np.random.choice(np.arange(2,6), p = [0.4, 0.3, 0.2, 0.1]) for item in range(NUM_ITEMS) ]



    ITEM_SIZES = [random.randint(1, BIN_SIZE) for item in range(NUM_ITEMS)]
    COLORS = [random.randint(0,NUM_COLORS-1) for item in ITEM_SIZES]
    # COLORS = [0, 1,2,0, 0,3,0 ,1,3,2] * 2
    NUM_BINS = NUM_ITEMS
    param = NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, 2
    CP_model_restricted(param)
