# Clinical Trial Outcome Predictor — Research Program

You are an autonomous ML research agent. You will run experiments in a loop to improve a clinical trial outcome predictor. You operate without human supervision — do NOT pause to ask if you should continue. Loop until interrupted.

## SETUP

1. Agree on a run tag based on today's date (e.g. `mar18`)
2. Create a branch: `git checkout -b autoresearch/<tag>`
3. Read these files for context:
   - `program.md` (this file — your instructions)
   - `prepare.py` (frozen — data loading and evaluation function)
   - `train.py` (mutable — feature engineering, model, training)
4. Verify data exists: `ls data/trials_raw.csv data/val_ids.json`
5. Initialize `results.tsv` with header row only:
   ```
   commit	auc_roc	n_features	status	description
   ```
6. Run the baseline (unmodified `train.py`), evaluate, record in results.tsv
7. Begin the experiment loop

## CONSTRAINTS

- **Fixed 60-second time budget** for training (CPU-only, no GPU)
- **CANNOT** modify `prepare.py` (contains evaluation function)
- **CANNOT** modify `data/trials_raw.csv` or `data/val_ids.json`
- **CANNOT** add new pip dependencies (only numpy, pandas, scikit-learn are available)
- **CAN** modify anything in `train.py` — features, model, hyperparameters, architecture
- All else equal, simpler is better. 0.001 AUC improvement from deleting code beats 0.001 from adding complexity.

## GOAL

Maximize `auc_roc` on the held-out validation set.

Higher is better. Extract with: `grep "^auc_roc:" run.log`

## OUTPUT FORMAT

`train.py` prints grep-friendly output:
```
cv_auc_roc:        0.650000
n_features:        42
training_seconds:  3.2
model_type:        GradientBoostingClassifier
```

`prepare.py` (evaluation) prints:
```
auc_roc:           0.620000
p_at_80_recall:    0.550000
n_features:        42
model_type:        GradientBoostingClassifier
```

Extract the key metric: `grep "^auc_roc:" run.log`

## EXPERIMENT LOOP

```
LOOP FOREVER:
  1. Review results.tsv and git log to see what's been tried
  2. Formulate a hypothesis (ONE change at a time)
  3. Modify train.py
  4. git add train.py && git commit -m "<description of change>"
  5. Run: python train.py > run.log 2>&1
  6. Run: python prepare.py >> run.log 2>&1
  7. Extract: grep "^auc_roc:\|^n_features:" run.log
  8. If grep empty → CRASH: tail -n 50 run.log, debug
  9. Record in results.tsv (DO NOT commit results.tsv)
  10. If auc_roc improved → keep the commit, continue
  11. If auc_roc same or worse → git reset --hard HEAD~1
  12. Go to 1
```

## RESULTS.TSV FORMAT

Tab-separated. Do NOT use commas (they break descriptions).

```
commit	auc_roc	n_features	status	description
a1b2c3d	0.620000	82	keep	baseline
b2c3d4e	0.635000	45	keep	LASSO feature selection reduces to 45 features
c3d4e5f	0.630000	45	discard	switch to random forest
d4e5f6g	0.000000	0	crash	XGBoost import error
```

- Column 1: short git hash (7 chars)
- Column 2: auc_roc (6 decimals, 0.000000 for crashes)
- Column 3: n_features
- Column 4: `keep`, `discard`, or `crash`
- Column 5: short description (no tabs or newlines)

## WHAT TO TRY

The dataset has ~85 raw features from 18 MCP biomedical data sources:

**Data sources and what they provide:**
- ClinicalTrials.gov: trial design, phase, enrollment, endpoints, sponsors
- OpenTargets: genetic evidence scores (genetic, somatic, literature, animal, known_drug, pathway)
- ChEMBL: compound bioactivity, selectivity, IC50, mechanism of action count
- DrugBank: drug interactions, targets, enzymes, transporters, half-life, molecular weight
- BindingDB: binding affinity (Ki, Kd), measurement count
- ClinPGx: pharmacogenomic guidelines, CYP substrate count
- FDA: regulatory designations (breakthrough, fast track, orphan), adverse events
- PubMed + OpenAlex + bioRxiv: publication counts, citation velocity, preprints
- Medicare + Medicaid: healthcare spend on indication
- Reactome + STRING-db: pathway count, PPI network degree, betweenness
- GTEx: tissue expression specificity
- gnomAD: loss-of-function intolerance (pLI, LOEUF)
- ClinVar: pathogenic variant count
- GWAS Catalog: hit count, best p-value
- DepMap: cancer gene essentiality
- cBioPortal: tumor mutation frequency
- HPO + Monarch: disease phenotype count, associated gene count
- EMA + EU Filings: European regulatory signals

**Ideas (non-exhaustive — try your own):**
- Feature selection: mutual information, LASSO, recursive elimination
- Feature interactions: genetic_evidence × phase, selectivity × indication
- Log transforms for skewed features (IC50, enrollment, publication counts)
- Missing value strategies: indicator variables, KNN imputation
- Categorical encoding: target encoding, one-hot for indication_area
- Model types: LogisticRegression, RandomForest, XGBoost (if fast enough), SVM
- Ensemble methods: stacking, voting, blending
- Regularization tuning
- Feature clustering to reduce multicollinearity

## ERROR HANDLING

- If `train.py` crashes: read the error, fix it in train.py, try again
- If training takes >60s: reduce model complexity or feature count
- If AUC is stuck after 5+ experiments: try a fundamentally different approach
- Log all crashes to results.tsv with status=`crash` and auc_roc=0.000000
- After fixing a crash, do NOT amend — make a new commit

## AUTONOMY

Do NOT pause to ask the human if you should continue.
Do NOT ask "should I keep going?" or "shall I try another approach?"
Just keep looping. The human will interrupt you when they want you to stop.
