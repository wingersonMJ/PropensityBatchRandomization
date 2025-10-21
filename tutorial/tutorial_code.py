import pandas as pd
from propensitybatchrandomization import propensity_scores
from propensitybatchrandomization import randomAssignments 

# read in example data
df = pd.read_csv("example_data.csv")

# define covariates
covariates = ['location', 'intervention_group', 'time_to_enrollment', 'sex']  

# Convert to categoricals 
df['location'] = df['location'].astype('category')
df['intervention_group'] = df['intervention_group'].astype('category')
df['sex'] = df['sex'].astype('category')

# randomly assign subjeccts to batches
assignments = randomAssignments(
                        data = df,
                        subjectID = 'id', # column name that contains the subject ID's
                        nVisits = 'nVisits', # column name that contains the number of visits for each subject (make a column of 1's if cross-sectional)
                        seed = 1989,
                        nIter = 1000, # need lots of iterations for good coverage if working with smaller sample size.
                        batchSize = 34,
                        nBatches = 4
                        )

# evaluate propensity scores for those batch assignments and select iteration...
# ... with lowest (i.e., best) score. Save that iteration. 
data, metrics = propensity_scores(
                        data = df, 
                        subject_id = 'id',
                        covariates = covariates, 
                        randomized_assignments = assignments
                        )
