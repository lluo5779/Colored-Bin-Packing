import time
from multiprocessing import Pool, cpu_count
from os import listdir
from os.path import isfile, join
import multiprocessing as mp

import numpy as np
import json

if __name__ == '__main__':
    from GCP_unrestricted_packing_cp import CP_model_unrestricted
    from GCP_unrestricted_packing_mip import MIP_model_unrestricted

    from GCP_restricted_packing_cp import CP_model_restricted
    from GCP_restricted_packing_cp_subsequence import CP_model_subsequence_restricted
    from GCP_restricted_packing_mip import MIP_model_restricted

    TIMEOUT = 300

    PATH_INSTANCE = "./data/"
    onlyfiles = [f for f in listdir(PATH_INSTANCE) if isfile(join(PATH_INSTANCE, f)) and ".json" in f]

    print("Using FIXED PIW for coils")

    all_params = []
    this_params = []

    prev_NUM_ITEMS = 0
    for instance_i, filename in enumerate(onlyfiles):
        print(filename)
        with open("./data/" + filename, 'r') as f:
            data = json.load(f)

        NUM_COLORS = data['NUM_COLORS']
        NUM_ITEMS = data['NUM_ITEMS']
        BIN_SIZE = data['BIN_SIZE']
        DISCREPANCY = filename.split("_D")[1].split('_S')[0] #data['DISCREPANCY'] <- json store fractions for some reason
        ITEM_SIZES = data['ITEM_SIZES']
        COLORS = data['COLORS']

        NUM_BINS = NUM_ITEMS
        SEED = filename.split("_S")[1].split('.json')[0]

        if prev_NUM_ITEMS != NUM_ITEMS:
            prev_NUM_ITEMS = NUM_ITEMS
            if len(this_params):
                all_params.append(this_params)
            this_params = []

        this_params.append([
            NUM_COLORS, NUM_ITEMS, BIN_SIZE, DISCREPANCY, ITEM_SIZES, COLORS, NUM_BINS, TIMEOUT, SEED
        ])

    all_params.append(this_params)

    ts = time.time()
    # all_params = all_params[:1]
    # params = all_params[0]
    #
    # CP_model_restricted(params[8])
    # CP_model_subsequence_restricted(params[8])
    # MIP_model_restricted(params[8])
    # CP_model_unrestricted(params[8])
    # MIP_model_unrestricted(params[8])

    cc = 1
    for params in all_params:
        try:
            with mp.Pool(processes=mp.cpu_count() - cc) as pool:
                pool.map(CP_model_restricted, params)
        except:
            print("CP Binary Restricted - Failed with params", params)

        try:
            with mp.Pool(processes=mp.cpu_count() - cc) as pool:
                pool.map(CP_model_subsequence_restricted, params)
        except:
            print("CP Subseq Restricted - Failed with params", params)

        try:
            with mp.Pool(processes=mp.cpu_count() - cc) as pool:
                pool.map(MIP_model_restricted, params)
        except:
            print("MIP Restricted - Failed with params", params)

        try:
            with mp.Pool(processes=mp.cpu_count() - cc) as pool:
                pool.map(CP_model_unrestricted, params)
        except:
            print("CP Unrestricted - Failed with params", params)

        try:
            with mp.Pool(processes=mp.cpu_count() - cc) as pool:
                pool.map(MIP_model_unrestricted, params)
        except:
            print("MIP Uestricted - Failed with params", params)

    print('Time in parallel:', time.time() - ts)
