import random
import pandas as pd
import time
import numpy as np
from collections import defaultdict

def randomAssignments(
        data, 
        subjectID, 
        nVisits, 
        nIter,
        batchSize, 
        nBatches,
        seed = 1989
        ):
    
    """
    Randomizes samples to batches, given batch size constraints and input data.

    Args:
        data = input data, expected to be wide format with columns for SubjectID and nVisits.
        subjectID = column name for subject ID, expects string.
        nVisits = column name for the number of subject visits/samples, expects string.
        seed = random seed number.
        nIter = number of iterations to run, expects integer.
        batchSize = size of each batch. 
        nBatches = number of batches.
    
    Returns:
        A dictionary containing each iteration of the randomized assignments.
    """

    start_time = time.time()
    randomized_assignments = []
    random.seed(seed)

    for _ in range(nIter): 
        subjects = data[[subjectID, nVisits]].itertuples(index=False, name=None)
        subjects = list(subjects) 
        random.shuffle(subjects) 

        batches = [defaultdict(int) for _ in range(nBatches)]
        batch_totals = np.zeros(nBatches, dtype=int)  

        for subj, visits in subjects:
            for i in range(nBatches):
                if batch_totals[i] + visits <= batchSize:
                    batches[i][subj] = visits
                    batch_totals[i] += visits
                    break
        
        assigned_subjects = set()
        for batch in batches:
            assigned_subjects.update(batch.keys())

        leftover = {}
        for subject, visits in subjects:
            if subject not in assigned_subjects:
                leftover[subject] = visits
        if leftover:
            batches.append(leftover)

        randomized_assignments.append(batches)

    end_time = time.time()
    print(f'Ran {nIter} iterations in {(end_time - start_time):.1f} seconds\n')
    print(f'Total samples to analyze: {data[nVisits].sum()}\n')
    print(f'Total subjects to analyze: {len(data)}\n')
    print(f'Printing iteration #1: {randomized_assignments[0]}\n')

    return randomized_assignments