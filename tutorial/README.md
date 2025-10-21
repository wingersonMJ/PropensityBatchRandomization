# Use example

```python
# Data 
file_path = 'example_data.csv'
df = pd.read_excel(file_path)
```

Run the random assignments function. In this example, `subjectID` and `nVisits` are defined as 'id' and 'nVisits' in my dataset. The batchSize constraint is set to 34 samples per batch, with 4 batches in total:
```python
assignments = randomAssignments(
                    data = df, 
                    subjectID = 'id', 
                    nVisits = 'nVisits', 
                    seed = 1989,
                    nIter = 100,
                    batchSize = 34, 
                    nBatches = 3)
```

Define factors for balancing:
```python
covariates = ['location', 'intervention_group', 'time_to_enrollment', 'sex']
```  

Run the propensity_scores function:
```python
data, metrics = propensity_scores(
                        data = df, 
                        subject_id = 'id',
                        covariates = covariates, 
                        randomized_assignments = assignments)
```

## Summary statistics:
A simple comparison of covariates across batches can be performed. This will return p-values for comparisons across covariates:
```python
summary = TableOne(
    data, 
    columns= covariates,
    categorical= ['location', 'intervention_group', 'sex'],
    continuous= ['time_to_enrollment'], 
    groupby='Batch_Assignment',
    pval=True,
    decimals=2)
print(summary.tabulate(tablefmt = "fancy_grid"))
```

**Below is an example output from the TableOne library:**
|                               |    | Missing   | Overall    | 1          | 2          | 3          | 4          | P-Value   |
|-------------------------------|----|-----------|------------|------------|------------|------------|------------|-----------|
| n                             |    |           | 50         | 17         | 15         | 17         | 1          |           |
| location, n (%)               | 0  |           | 28 (56.0)  | 9 (52.9)   | 9 (60.0)   | 10 (58.8)  |            | 0.685     |
|                               | 1  |           | 22 (44.0)  | 8 (47.1)   | 6 (40.0)   | 7 (41.2)   | 1 (100.0)  |           |
| intervention_group, n (%)     | 0  |           | 29 (58.0)  | 9 (52.9)   | 9 (60.0)   | 11 (64.7)  |            | 0.594     |
|                               | 1  |           | 21 (42.0)  | 8 (47.1)   | 6 (40.0)   | 6 (35.3)   | 1 (100.0)  |           |
| time_to_enrollment, mean (SD) |    | 0         | 12.4 (4.7) | 12.6 (4.6) | 12.5 (5.3) | 12.2 (4.7) | 12.0 (0.0) | 0.996     |
| sex, n (%)                    | 0  |           | 26 (52.0)  | 8 (47.1)   | 8 (53.3)   | 10 (58.8)  |            | 0.665     |
|                               | 1  |           | 24 (48.0)  | 9 (52.9)   | 7 (46.7)   | 7 (41.2)   | 1 (100.0)  |           |

*Note:* Batch_Assignment will include nBatches + 1 groups. For example, if you specify 3 batches, you will get 4, where batch #4 captures any leftover samples. This group does not follow the batchSize constraint. This is helpful when your total sample size exceeds batchSize * nBatches.