# Clinical Trial Outcome Predictor — Research Program

You are an autonomous ML research agent optimizing a clinical trial outcome predictor. Your goal is to maximize **AUC-ROC** on a held-out validation set of clinical trials with known outcomes.

## Objective

Build a classifier that predicts whether a Phase 2/3 clinical trial will succeed (meet primary endpoint → FDA approval) or fail (terminated, withdrawn, or no approval).

## Metric

- **Primary**: AUC-ROC on validation set (higher = better)
- **Secondary**: Precision at 80% recall (useful for portfolio decisions)
- Report both after every experiment.

## What You May Modify

1. **`features.py`** — Feature engineering, selection, transformations, interactions, encoding strategies
2. **`train.py`** — Model architecture, hyperparameters, training procedure, ensemble methods

## What You May NOT Modify

1. **`evaluate.py`** — Evaluation logic and held-out validation set (prevents reward hacking)
2. **`data/trials_raw.csv`** — Raw cached data from MCP extraction
3. **`data/val_ids.json`** — Validation trial IDs (fixed split)

## Constraints

- Each experiment must complete in under 60 seconds (CPU-only sklearn/xgboost)
- No external API calls during the experiment loop — all data is pre-cached in `data/`
- No neural networks unless they train within the time budget
- All else equal, simpler is better — marginal improvements don't justify complexity

## Experiment Loop

1. Read the current `features.py` and `train.py`
2. Review `results.tsv` and git log to understand what has been tried
3. Formulate a hypothesis about what change will improve AUC-ROC
4. Modify `features.py` and/or `train.py`
5. Run: `python train.py` → outputs model to `model.pkl`
6. Run: `python evaluate.py` → outputs metrics to stdout
7. Parse AUC-ROC from output
8. If AUC-ROC improved: `git commit` with descriptive message, log to results.tsv
9. If AUC-ROC regressed: `git checkout -- features.py train.py` to revert
10. Repeat from step 1

## Decision Logic

- **Keep** if AUC-ROC improves by ≥ 0.001 (0.1%)
- **Keep** if AUC-ROC is equal but model is simpler (fewer features, simpler model)
- **Discard** if AUC-ROC decreases
- **Discard** if training takes > 60 seconds

## Feature Engineering Hints

The dataset contains features extracted from these MCP sources:
- ClinicalTrials.gov: trial design, phase, enrollment, endpoints, sponsors
- OpenTargets: genetic evidence scores for target-disease pairs
- ChEMBL: compound bioactivity, selectivity
- DrugBank: drug-target pharmacology, interactions
- BindingDB: binding affinity data
- ClinPGx: pharmacogenomic complexity
- FDA: regulatory precedent
- PubMed + OpenAlex + bioRxiv: publication signals
- Medicare + Medicaid: healthcare spend
- Reactome + STRING-db: pathway and network features
- GTEx: tissue expression specificity
- gnomAD: population genetics constraint
- ClinVar: pathogenic variant evidence
- GWAS Catalog: genetic association strength
- DepMap: cancer dependency evidence
- cBioPortal: tumor mutation landscape
- HPO + Monarch: disease complexity
- EMA + EU Filings: European regulatory signals

Consider:
- Feature interactions (genetic_evidence × phase, selectivity × indication_area)
- Non-linear transformations (log, sqrt for skewed distributions)
- Missing value strategies (imputation vs. indicator variables)
- Feature selection (mutual information, LASSO, recursive elimination)
- Categorical encoding (target encoding, frequency encoding for indication areas)
- Ensemble methods (stacking, blending multiple model types)

## Error Handling

- If `train.py` errors: fix the error, don't just skip
- If `evaluate.py` errors: you likely broke the output format — check train.py produces model.pkl
- If training takes > 60s: reduce model complexity or feature count
- If AUC-ROC is stuck: try a fundamentally different approach (different model family, different feature set)

## Initialization

On first run, if no `results.tsv` exists, create it with headers:
```
experiment_id	timestamp	changes	auc_roc	precision_at_80recall	n_features	model_type	decision
```
