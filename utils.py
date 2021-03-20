import numpy as np
import json
import os

def solution_checker(Xs, params, problem_type):
    NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, Timelimit, SEED = params
    try:
        Xs = np.array(Xs)
        NUM_ITEMS = len(ITEM_SIZES)

        BINS = np.unique(Xs)

        for bin in BINS:
            items_in_bin = np.where(Xs == bin)[0]
            print("items", items_in_bin)
            cap_used = sum([ITEM_SIZES[i] for i in items_in_bin])
            print("itemsizes", [ITEM_SIZES[i] for i in items_in_bin])
            print('itemcolors', [COLORS[i] for i in items_in_bin])
            prev_color = COLORS[items_in_bin[0]]
            # cap_used = 0
            for i, item in enumerate(items_in_bin[1:]):
                this_color = COLORS[item]
                if "unrestricted" not in problem_type:
                    assert prev_color != this_color, "*** Error: Colors of adjacent items {}, {} are same {}".format(items_in_bin[1:][i-1], items_in_bin[1:][i], Xs[items_in_bin[1:][i-1]: items_in_bin[1:][i]+1])
                prev_color = this_color

                # cap_used += ITEM_SIZES[item]
            print(cap_used)
            assert cap_used <= BIN_SIZE, "*** Error: Bin {} exceeded capacity by {}".format(bin, BIN_SIZE - cap_used)

        print("*** FINISHED all tests")
        return True
    except Exception as err:
        print(err)
        write_to_global_failed(params, problem_type, is_bad_solution=True)
        return False


def write_to_global_failed(params, problem_type, is_bad_solution):
    NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, Timelimit, SEED = params
    filename = "./results/results_failed.json"
    results_ = {
        "NUM_COLORS":[],
        "NUM_ITEMS":[],
        "BIN_SIZE":[],
        'SEED':[],
        "DISCREPANCY":[],
        "TYPE":[],
        "IS_BAD":[],
        "SEED": []
        }

    if os.path.exists(filename):
        with open(filename, "r", encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = results_

    with open(filename, "w+", encoding='utf-8') as f:
        results['NUM_COLORS'].append(NUM_COLORS)
        results['NUM_ITEMS'].append(NUM_ITEMS)
        results['BIN_SIZE'].append(BIN_SIZE)
        results['DISCREPANCY'].append(DISCREPANCY)
        results['TYPE'].append(problem_type)
        results['IS_BAD'].append(is_bad_solution)
        results['SEED'].append(SEED)

        print(results)
        json.dump(results, f, ensure_ascii=False, indent=4)

        print("*** Model {} with Params {}: Failed to solve {} ***".format(problem_type, (NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, SEED), is_bad_solution))

def write_to_global_cp(msol, mdl, problem_type):
    filename = "./results/results_cp_{}.json".format(problem_type)
    results_ = {
        "NUM_COLORS":[],
        "NUM_ITEMS":[],
        "BIN_SIZE":[],
        "DISCREPANCY":[],
        'SEED':[],

        "OBJ_VAL":[],
        "OBJ_BOUND":[],
        "OBJ_GAP":[],

        "NUM_VARS":[],
        "NUM_CONSTRS":[],

        "SOLVE_TIME":[],
        "STATUS":[],
    }
    if os.path.exists(filename):
        with open(filename, "r", encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = results_

    with open(filename, "w+", encoding='utf-8') as f:
        results['NUM_COLORS'].append(mdl._myInstance[0])
        results['NUM_ITEMS'].append(mdl._myInstance[1])
        results['BIN_SIZE'].append(mdl._myInstance[2])
        results['DISCREPANCY'].append(mdl._myInstance[3])
        results['SEED'].append(mdl._myInstance[4])

        results['OBJ_VAL'].append(msol.get_objective_values()[0])
        results['OBJ_GAP'].append(msol.get_objective_gaps()[0])
        results['OBJ_BOUND'].append(msol.get_objective_bounds()[0])
        results['NUM_VARS'].append(msol.get_info("NumberOfModelVariables"))
        results['NUM_CONSTRS'].append(msol.get_info("NumberOfConstraints"))
        results['SOLVE_TIME'].append(msol.get_solve_time())
        results['STATUS'].append(msol.get_solve_status())

        print(results)

        json.dump(results, f, ensure_ascii=False, indent=4)

    print("*** Model {} with Params {}: results saved to {} ***".format("CP", mdl._myInstance, filename))


def write_to_global_mip(msol, mdl, problem_type):
    filename = "./results/results_mip_{}.json".format(problem_type)
    results_ = {
        "NUM_COLORS":[],
        "NUM_ITEMS":[],
        "BIN_SIZE":[],
        "DISCREPANCY":[],
        'SEED':[],

        "OBJ_VAL":[],
        "OBJ_BOUND":[],
        "OBJ_GAP":[],

        "NUM_VARS":[],
        "NUM_CONSTRS":[],

        "SOLVE_TIME":[],
        "STATUS":[],
    }
    if os.path.exists(filename):
        with open(filename, "r", encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = results_

    with open(filename, "w+", encoding='utf-8') as f:
        results['NUM_COLORS'].append(mdl._myInstance[0])
        results['NUM_ITEMS'].append(mdl._myInstance[1])
        results['BIN_SIZE'].append(mdl._myInstance[2])
        results['DISCREPANCY'].append(mdl._myInstance[3])
        results['SEED'].append(mdl._myInstance[4])

        results['OBJ_VAL'].append(msol.get_objective_value())
        results['OBJ_GAP'].append(msol.solve_details.gap)
        results['OBJ_BOUND'].append(msol.solve_details.best_bound)
        results['NUM_VARS'].append(mdl.number_of_variables)
        results['NUM_CONSTRS'].append(mdl.number_of_constraints)

        results['SOLVE_TIME'].append(msol.solve_details.time)
        results['STATUS'].append(msol.solve_details.status)

        print(results)

        json.dump(results, f, ensure_ascii=False, indent=4)

    print("*** Model {} with Params {}: results saved to {} ***".format("MIP", mdl._myInstance, filename))
