def randomAssignment(
        data, 
        subjectID, 
        nVisits, 
        seed,
        nIter,
        batchSize, 
        nBatches
        ):

    t1 = time.time()
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

    t2 = time.time()
    print(f'Ran {nIter} iterations in {t2-t1:.1f} seconds\n')
    print(f'Total samples to analyze: {data[nVisits].sum()}\n')
    print(f'Total subjects to analyze: {len(data)}\n')
    print(f'Printing iteration #1: {randomized_assignments[0]}\n')

    return randomized_assignments