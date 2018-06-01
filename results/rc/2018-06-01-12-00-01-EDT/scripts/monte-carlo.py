from __future__ import print_function

import os
import time
import random
import json
import socket

# from azureml.contrib.daskonbatch import DaskHelper
from joblib import Parallel, delayed

# Estimation function
def compute_pi(nb_it):
    return (4.0 * sum(1 for _ in range(nb_it) if random.random()**2.0 + random.random()**2.0 < 1.0) / nb_it,
            socket.gethostbyname(socket.gethostname()),
            os.getpid())


if __name__ == '__main__':
    
#     dh = DaskHelper()
#     dh._preregister()
    
    parallel_runs = 30
    samples_per_run = 10**6

    print("Computing {:,} simulations with {:,} samples per run...".format(parallel_runs, samples_per_run))

    # Run compute_pi in parallel
    start_time = time.time()
    results = Parallel(n_jobs=-1)(delayed(compute_pi)(samples_per_run) for _ in range(parallel_runs))
    elapsed_time = time.time() - start_time

    estimates, hostnames, process_ids = [], [], []
    for estimate, hostname, process_id in results:
        estimates.append(estimate)
        hostnames.append(hostname)
        process_ids.append(process_id)
#         print(hostname)
#         print(process_id)
    
    print('Unique hostnames: ', set(hostnames))
    print('Unique process IDs: ', set(process_ids))
    
    print("")
    print("Estimates of pi:")
    print("")
    print(estimates)

    print("")
    print("Elapsed time: {:g} seconds".format(elapsed_time))

    estimate = sum(estimates) / len(estimates)

    print("")
    print("Average pi estimate: {:,}".format(estimate))
