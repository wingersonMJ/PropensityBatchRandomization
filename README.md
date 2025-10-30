# Batch Randomization for Biological Samples in Longitudinal Data Analysis
Wingerson, MJ  
mat.wingerson@gmail.com  
[PyPI project link](https://pypi.org/project/propensitybatchrandomization/)

## Description
This package provides a structured tool for randomizing participant biological samples across plates or batches while numerically evaluating the balance of key participant covariates post-randomization. The goal is to mitigate batch effects commonly encountered in the analysis of biological samples.

**This project, developed with support from Patrick Carry and Carson Keeter, builds upon their existing [randomization scheme](https://github.com/carryp/PS-Batch-Effect) by including a longitudinal component.**

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [How It Works](#how-it-works)
   - [randomAssignment](#randomassignments)
   - [propensity_scores](#propensity_scores)

---

# Project Overview 

The collection of **biological samples**, such as blood plasma or serum, provides an objective means of measuring physiological responses to injury and rehabilitation. However, **sample processing, long-term storage, and analysis** introduce multiple opportunities for bias. One common issue, which can be mitigated with moderate pre-planning, is **batch effects**.

### What are batch effects?
Batch effects occur when samples processed in different batches produce systematically different results. Each batch analyzed using the Single Molecule Array (SIMOA) is subject to a certain degree of error or variability. In theory, the same sample could be analyzed in multiple batches and return slightly different values each time.

To minimize batch effects, three approaches are commonly used:
1. Plate calibrators help reduce measurement error for each plate.
2. Internal controls, either pooled or unpooled, are included on every plate to quantify differences between plates.
3. **Batch randomization** ensures that samples are assigned to different batches in a way that reduces the risk of disproportionate distribution of relevant participant characteristics (e.g., demographics, injury characteristics).

---

## Batch Randomization

A simple randomization scheme can be used to assign samples to different batches. *In theory*, simple randomization is effective when the number of batches and batch sizes are large. However, this rarely reflects real-world research on biological samples, where batch sizes are limited and the number of batches is small.

---

## Randomization and Propensity Score Checking

To address the issue of imbalanced randomization, we implement a three-step approach: 
1. Iteratively assign samples to batches using simple randomization.
2. Evaluate the success of the randomization using propensity scores.
3. Select the simple random assignment iteration with the best propensity scores. 

### What are propensity scores?
A **propensity score** represents the probability that a sample belongs to a particular batch, given known sample characteristics (e.g., age, biological sex). 
- High propensity scores indicate that batch assignment is not truly random, and that batch membership can be predicted using these characteristics.
- Low propensity scores suggest that the sample characteristics are well-balanced across batches, making batch assignment less predictable.

By iterating this process multiple times, we generate several potential randomization schemes, each with an associated propensity score. Researchers can then select a randomization scheme with the lowest propensity score, which optimally balances covariates across batches.

---

## Longitudinal Data as a Unique Challenge
Longitudinal studies — where samples are collected from the same participant across multiple time points — present an additional challenge: ideally, all samples from a single participant should be processed in the same batch to minimize within-subject variability.

### Key considerations:
- Samples from the same participant must remain within the same batch.
- The number of samples per participant (which may vary due to compliance or attrition) must be accounted for.
- The maximum batch size must not be exceeded.

---

## Example Plate Layout

Included below is an example plate layout containing calibrators, internal plate controls, and participant samples. This example plate layout is available to [download](https://github.com/wingersonMJ/batch_randomization/blob/main/SIMOA_plate_layout_examples.xlsx).

![Example Plate Layout](figs/example_plate_layout.png)

---

## Summary

Batch effects introduce bias when analyzing biological samples, but randomization strategies can help mitigate these issues. A two-step approach of randomizing samples to batches and then evaluating balance using propensity scores can improve the stability of batch assignments. Longitudinal study designs require additional considerations.

```python
# load package 
import propensitybatchrandomization as pbr
```

---

# How It Works  

Two functions are defined in the included source code: `randomAssignments` and `propensity_scores`.

---

## `randomAssignments`  

### Purpose:
Randomize participants to batches, given a batch size constraint, number of batches, and desired iterations.

### Expected Inputs:
- `data`: your dataset, expecting wide format and a column defining the subject identifier and a column defining the number of samples for that subject.  
- `subjectID`: the column for the subject identifier.
- `nVisits`: the column for the number of samples (or visits) for the subject.
- `seed`: set seed for repeatability.
- `nIter`: number of iterations to run.
- `batchSize`: maximum size for each batch.
- `nBatches`: number of batches desired.

### Key Operations:
For each iteration, generate a list of the subject identifier and the number of visits for that subject. Then, randomly shuffle that list:
```python
for _ in range(nIter): 
    subjects = data[[subjectID, nVisits]].itertuples(index=False, name=None)
    subjects = list(subjects) 
    random.shuffle(subjects)
```

For each subject and their number of visits, and for each batch, add subjects iteratively if their nVisits does not exceed the batch size limit:
```python
for subj, visits in subjects:
            for i in range(nBatches):
                if batch_totals[i] + visits <= batchSize:
                    batches[i][subj] = visits
                    batch_totals[i] += visits
                    break
```

---

## `propensity_scores`

### Propensity scores defined:
A propensity score is a conditional probability of belonging to a batch given a set of covariates. In other words, it is the probability of a subject belonging to a certain group based on known characteristics about that subject. For example, if boys are more likely to be in batch #1, and girls in batch #2, then a boy subject would have a high conditional probability of belonging to batch #1 given sex.

*Formula:*  
$e(X)=Pr(Z=j∣X)$  

$e(X)$ = propensity score given covariates $X$  
$Pr(Z=j∣X)$ = probability of belonging to a batch $j$ given covariates $X$  

In the context of this project, identifying batch randomizations with low overall propensity scores means that pre-determined subject characteristics are well-distributed across batches.  

### Expected inputs:  
- `data` = your dataset  
- `subject_id` = the column in your dataset that defines your subject identifier  
- `covariates` = a list of the covariates used for balancing  
- `randomized_assignments` = the output from the randomizedAssignment function above  

### Key operations:  
For each batch, create a binary variable to represent if the subject is in the batch or not:
```python
for batch in iteration:
    temp_data = data.copy()
    temp_data['batch'] = temp_data[subject_id].isin(batch).astype(int)
```

Use a logistic regression to predict the probability of belonging to a batch given covariates:
```python
model = LogisticRegression()
model.fit(temp_data[covariates], temp_data['batch'])
temp_data['propensity_score'] = model.predict_proba(temp_data[covariates])[:, 1]
```

Calculate the propensity score as the difference in the true value and the predicted probability for both in-batch and out-batch subjects:
```python
in_batch = temp_data.loc[temp_data['batch'] == 1, 'propensity_score']
out_batch = temp_data.loc[temp_data['batch'] == 0, 'propensity_score']

diff = abs(in_batch.mean() - out_batch.mean())
batch_diffs.append(diff) #store diff across all batches
          
avg_balance = np.mean(batch_diffs)
```

This returns a balancing metric (`batch_diffs`), which represents the propensity for in- vs out-batch membership given covariates. If covariates are properly balanced between batches, then the probability of being in-batch will be relatively equal to the probability of being out-batch. Therefore, the difference between these two scores will be very small (i.e., balanced).  

These balance scores are then averaged across all subjects and all batches.  

The function returns your original dataset, with an added column 'Batch_Assignment' for the randomized batch assignment for each subject based on which randomized iteration returned the lowest propensity score (i.e., most balanced):
```python
data['Batch_Assignment'] = None
    for batch_num, group in enumerate(best_batches, start=1):
        data.loc[data[subject_id].isin(group), 'Batch_Assignment'] = batch_num

     return data, metrics_df
 ```

---

## Flow of Data:

<img src="figs\flow_chart.jpg" size=600>