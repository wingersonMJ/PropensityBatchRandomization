import pandas as pd
from propensitybatchrandomization import propensity_scores
from propensitybatchrandomization import randomAssignments 
from tableone import TableOne # fun tool for quick tables

# read in example data
df = pd.read_csv(".\\tutorial\\example_data.csv")

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
                        nBatches = 3
                        )

# evaluate propensity scores for those batch assignments and select iteration...
# ... with lowest (i.e., best) score. Save that iteration. 
data, metrics = propensity_scores(
                        data = df, 
                        subject_id = 'id',
                        covariates = covariates, 
                        randomized_assignments = assignments
                        )

# check that it worked and that classes are balanced between batches!
# TableOne can give some easy tables for comparisons
summary = TableOne(
    data, 
    columns = covariates,
    categorical = ['location', 'intervention_group', 'sex'],
    continuous = ['time_to_enrollment'], 
    groupby = 'Batch_Assignment',
    pval = True,
    decimals = 2)
print(summary.tabulate(tablefmt = "fancy_grid"))


# Summary w/out leftovers
# the randomAssignments function automatically gives a leftover group if needed
# you can remove that by filtering the data to not include the last batch
data_filtered = data[data['Batch_Assignment'] != 4] # nBatches+1
summary2 = TableOne(
    data_filtered, 
    columns= covariates,
    categorical= ['location', 'intervention_group', 'sex'],
    continuous= ['time_to_enrollment'], 
    groupby='Batch_Assignment',
    pval=True,
    decimals=2)
print(summary2.tabulate(tablefmt = "fancy_grid"))
