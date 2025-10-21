import pandas as pd
import time
import numpy as np
from collections import defaultdict
from sklearn.linear_model import LogisticRegression

def propensity_scores(
        data, 
        subject_id, 
        covariates, 
        randomized_assignments
        ):
    """
    Calculates propensity scores using logistic regression for each iteration of random assignment. 

    Args:
        data = A dataframe containing the subject ID and all covariates, expects wide format. 
        subject_id = The column name for subject ID, expects string. 
        covariates = The column name(s) for covariates to use for propensity score basing, expects a list of strings.
        randomized_assignments = A dictionary of subject ID's, batch assignments, and iterations. Can be obtained using randomAssignment().

    Returns:
        data, metrics_df
        data = A dataframe with batch assignments for only the iteration with the lowest (best) propensity score. 
        metrics_df = A dataframe summarizing propensity scores across all iterations of random assignment. 
    """
    
    start_time = time.time()
    assignments_list = []
    for i in randomized_assignments:
        listed_subjectID = [] 
        for batch in i:
            subject_ids = list(batch.keys())
            listed_subjectID.append(subject_ids)
        assignments_list.append(listed_subjectID)

    # propensity score metrics
    metrics = []
    for i, iteration in enumerate(assignments_list, start=1):
        batch_diffs = []
        for batch in iteration:
            temp_data = data.copy()
            temp_data['batch'] = temp_data[subject_id].isin(batch).astype(int)
            
            # Logistic Regression
            model = LogisticRegression()
            model.fit(temp_data[covariates], temp_data['batch'])
            temp_data['propensity_score'] = model.predict_proba(temp_data[covariates])[:, 1]
            
            # Difference btwn in-group and out-group propensity scores
            in_batch = temp_data.loc[temp_data['batch'] == 1, 'propensity_score']
            out_batch = temp_data.loc[temp_data['batch'] == 0, 'propensity_score']
            diff = abs(in_batch.mean() - out_batch.mean())
            batch_diffs.append(diff)
        
        # Average balance (in-group vs out-group) for the iteration
        avg_balance = np.mean(batch_diffs) # want as low as possible
        metrics.append((i, avg_balance))
    
    metrics_df = pd.DataFrame(metrics, columns=['Iteration', 'avg_balance'])
    
    lowest_balance = metrics_df.sort_values('avg_balance').iloc[0]['Iteration'] - 1
    lowest_balance_score = metrics_df.sort_values('avg_balance').iloc[0]['avg_balance']
    best_batches = assignments_list[int(lowest_balance)]
    
    # Add batch num to original dataset
    data['Batch_Assignment'] = None
    for batch_num, group in enumerate(best_batches, start=1):
        data.loc[data[subject_id].isin(group), 'Batch_Assignment'] = batch_num
    
    end_time = time.time()
    print(f'Ran in {((end_time - start_time)/60):.1f} minutes')
    print(f'Lowest balance score: {lowest_balance_score:.4f}')

    return data, metrics_df