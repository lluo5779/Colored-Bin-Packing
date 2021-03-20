import random
import numpy as np
from itertools import combinations
from utils import solution_checker
import time

random.seed(123)

NUM_COLORS = 4
NUM_ITEMS = 50
BIN_SIZE = 10
DISCREPANCY = 0
# MAX_COLORS_IN_BIN = 40

# [Color][Item]
# ITEM_SIZES = [ np.random.choice(np.arange(2,6), p = [0.4, 0.3, 0.2, 0.1]) for item in range(NUM_ITEMS) ]



ITEM_SIZES = [random.randint(1, BIN_SIZE) for item in range(NUM_ITEMS)]
COLORS = [random.randint(0,NUM_COLORS-1) for item in ITEM_SIZES]
# COLORS = [0, 1,2,0, 0,3,0 ,1,3,2] * 2

lb = sum(ITEM_SIZES) / BIN_SIZE
NUM_BINS = int(lb - 0.0001) + 1


param = NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, 2
NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, Timelimit = param
params = param
##

from z3 import *
st = time.time()

status = -1
while status == -1:
    print("Proving model with {} bins".format(NUM_BINS))
    X = [[Bool("x_{}_{}".format(item, bin)) for bin in range(NUM_BINS)] for item in range(NUM_ITEMS)]
    IS = [[Int("size_{}_{}".format(item, bin)) for bin in range(NUM_BINS)] for item in range(NUM_ITEMS)]


    s = Solver()
    s.set(unsat_core=True)
    def at_most_one(literals, name=""):
        c = []
        for pair in combinations(literals, 2):
            a,b = pair[0], pair[1]
            c += [Or(Not(a), Not(b))]
        return And(c)


    # At least one assignment across bins
    for item in range(NUM_ITEMS):
        s.assert_and_track(
            Or(X[item]), "at_least_one_{}".format(item)
        )

    for item in range(NUM_ITEMS):
        s.assert_and_track(
            at_most_one(X[item]), "at_most_one_{}".format(item)
        )

    for item in range(NUM_ITEMS):
        for bin in range(NUM_BINS):
            s.assert_and_track(
                Or(Not(X[item][bin]), IS[item][bin] == ITEM_SIZES[item]), 'linking_x_IS_val_{}_{}'.format(item, bin)
            )
            s.assert_and_track(
                Or(X[item][bin], IS[item][bin] == 0), 'linking_x_IS_nil_{}_{}'.format(item, bin)
            )

    for bin in range(NUM_BINS):
        s.assert_and_track(
            sum(IS[item][bin] for item in range(NUM_ITEMS)) <= BIN_SIZE, 'bin_load_{}'.format(bin)
        )

    for bin in range(NUM_BINS):
        for item1 in range(NUM_ITEMS):
            for item2 in range(item1+1, NUM_ITEMS):
                if COLORS[item1] == COLORS[item2]:
                    s.assert_and_track(
                        If(
                            And([X[item1][bin], X[item2][bin]]),
                            Or([X[i][bin] for i in range(item1+1, item2+1) if COLORS[i] != COLORS[item1]]),
                            Not(And([X[item1][bin], X[item2][bin]]))
                        )
                        , "if_colors_same_{}_{}_{}".format(item1, item2, bin)
                    )

    status = s.check().r
    msol = s.model()
    # print(msol)
    print(s.unsat_core())
    if status == -1:
        print("UNSAT: ", NUM_BINS)
        print("Time Elapsed: ", round(time.time() - st,  3))
        NUM_BINS = NUM_BINS + 1

print("At optimal: ", NUM_BINS)
print("Time Finished: ", round(time.time() - st,  3))
##
items_assigned = []
bins_assigned = [0 for item in range(NUM_ITEMS)]

for bin in range(NUM_BINS):
    isa =[]

    for item in range(NUM_ITEMS):
        s = msol[X[item][bin]]
        if s:
            isa.append(item)#(item, msol[IS[item][bin]]))
            bins_assigned[item] += bin
    if len(isa):
        items_assigned.append(isa)
print(items_assigned)
# (p_i + w_i <= p_i') or ((X_ij and NOT X_i'j) OR (NOT X_ij and X_i'j))
# for item in range(NUM_BINS):

solution_checker(bins_assigned, COLORS, ITEM_SIZES, BIN_SIZE)
