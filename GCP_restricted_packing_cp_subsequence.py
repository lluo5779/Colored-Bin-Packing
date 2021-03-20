import random
import numpy as np
from utils import *

import docplex.cp.utils_visu as visu

from docplex.cp.model import CpoModel
from docplex.cp.model import *
##
def CP_model_subsequence_restricted(params):
##
    NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, Timelimit, SEED = params


    print("*** Running CP Subseq Restricted with instance NUM_COLORS{} NUM_ITEMS{} BIN_SIZE {} DISCREPANCY {} SEED {}".format(
        NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, SEED))

    mdl = CpoModel()

    ITEMS = [mdl.interval_var(start=[0, sum(ITEM_SIZES)], size=ITEM_SIZES[item], optional=False, name="item_"+str(item)) for item in range(NUM_ITEMS)]
    ITEMS_TO_BINS = [[mdl.interval_var(start=(0, BIN_SIZE-min(ITEM_SIZES)), end=(min(ITEM_SIZES), BIN_SIZE), size=ITEM_SIZES[item], optional=True, name="item{}InBin{}".format(item, bin)) for bin in range(NUM_BINS)] for item in range(NUM_ITEMS)]

    ITEMS_S = mdl.sequence_var(ITEMS, types=COLORS, name="itemSequence")
    BIN_S = [mdl.sequence_var([ITEMS_TO_BINS[item][bin] for item in range(NUM_ITEMS)], types=[COLORS[item] for item in range(NUM_ITEMS)], name="bin{}Sequence".format(bin)) for bin in range(NUM_BINS)]

    # COLORS_S = [[mdl.sequence_var(ITEMS[item][bin] for item in range(NUM_ITEMS) if COLORS[item] == color)] for color in range(NUM_COLORS)]
    BINS_USED = [mdl.binary_var() for bin in range(NUM_BINS)]


    for item in range(NUM_ITEMS):
        # for bin in range(NUM_BINS):
        #     mdl.add_kpi(
        #         mdl.presence_of(ITEMS_TO_BINS[item][bin]),
        #         "item_"+str(item)+" "+str(bin)
        #     )
        mdl.add(
            mdl.sum(
                [mdl.presence_of(
                    ITEMS_TO_BINS[item][bin])
                    for bin in range(NUM_BINS)]
                ) == 1
        )

    # for item in range(NUM_ITEMS):
    #     mdl.add(
    #         mdl.alternative(ITEMS[item], [ITEMS_TO_BINS[item][bin] for bin in range(NUM_BINS)])
    #     )

    for bin in range(NUM_BINS):
        mdl.add(mdl.no_overlap(BIN_S[bin]))


    for item in range(NUM_ITEMS-1):
        mdl.add(
            mdl.end_before_start(ITEMS[item], ITEMS[item+1])
        )

    mdl.add(mdl.no_overlap(ITEMS_S))

    for bin in range(NUM_BINS):
        mdl.add(
            mdl.same_common_subsequence(
                ITEMS_S,
                BIN_S[bin],
            )
        )

    for item in range(NUM_ITEMS):
        for bin in range(NUM_BINS):
            # if (item, bin) in [(17,5), (20, 5), (29, 5)]:
            #     mdl.add_kpi(mdl.type_of_next(BIN_S[bin], ITEMS_TO_BINS[item][bin], lastValue=-1, absentValue=-1), name="typeofnext{}_{}".format(item, bin))
            #
            #     mdl.add_kpi(mdl.type_of_prev(BIN_S[bin], ITEMS_TO_BINS[item][bin], firstValue=-1, absentValue=-1), name="typeofprev{}_{}".format(item, bin))

            mdl.add(
                COLORS[item] != mdl.type_of_next(BIN_S[bin], ITEMS_TO_BINS[item][bin], lastValue=-1, absentValue=-1)
            )

            mdl.add(
                COLORS[item] != mdl.type_of_prev(BIN_S[bin], ITEMS_TO_BINS[item][bin], firstValue=-1, absentValue=-1)
            )

    for bin in range(NUM_BINS):
        mdl.add(
            BINS_USED[bin] ==  mdl.any([
                mdl.presence_of(ITEMS_TO_BINS[item][bin]) for item in range(NUM_ITEMS)
            ])
        )
    for bin in range(NUM_BINS-1):
        mdl.add(
            BINS_USED[bin] >= BINS_USED[bin+1]
        )

    mdl.add(
        mdl.minimize(
            mdl.sum(
                BINS_USED
            )
        )
    )

    # mdl.add(
    #         mdl.sum(
    #             BINS_USED
    #         ) < 48
    # )

    try:

        msol = mdl.solve(TimeLimit = Timelimit)
        mdl._myInstance = (NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, SEED)

        if msol:

            ITEMS_TO_BINS_S = []
            for bin in range(NUM_BINS):
                b_ = []
                for item in range(NUM_ITEMS):
                    s = msol[ITEMS_TO_BINS[item][bin]]
                    if s:
                        b_.append(s)
                ITEMS_TO_BINS_S.append(b_)
            # return mdl

            seq = msol.get_var_solution(BIN_S[0])

            print(ITEM_SIZES)
            print("CL: ",COLORS)

            Xs = []
            for item in range(NUM_ITEMS):
                for bin in range(NUM_BINS):
                    s = msol[ITEMS_TO_BINS[item][bin]]
                    if s:
                        # print(s)
                        Xs.append(bin)
            print("Xs: ", Xs)

            Xs = np.array(Xs)
            if solution_checker(Xs, params, "restricted_cp_subsequence"):
                write_to_global_cp(msol, mdl, 'restricted_subsequence')

    except Exception as err:
        print(err)
        write_to_global_failed(params, 'restricted_cp_subsequence', is_bad_solution=False)

    # return mdl, msol
##
##

##



if __name__ == "__main__":

    random.seed(123)

    NUM_COLORS = 2
    NUM_ITEMS = 50
    BIN_SIZE = 100
    DISCREPANCY = 0
    # MAX_COLORS_IN_BIN = 40

    # [Color][Item]
    # ITEM_SIZES = [ np.random.choice(np.arange(2,6), p = [0.4, 0.3, 0.2, 0.1]) for item in range(NUM_ITEMS) ]



    ITEM_SIZES = [random.randint(1, BIN_SIZE) for item in range(NUM_ITEMS)]
    COLORS = [random.randint(0,NUM_COLORS-1) for item in ITEM_SIZES]
    # COLORS = [0, 1,2,0, 0,3,0 ,1,3,2] * 2
    NUM_BINS = NUM_ITEMS
    params = NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, 10
    mdl = CP_model_subsequence_restricted(params)
