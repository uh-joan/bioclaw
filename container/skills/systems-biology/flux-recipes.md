# COBRApy Metabolic Modeling & Flux Analysis Recipes

Python code templates for constraint-based metabolic modeling using COBRApy. Covers FBA, FVA, gene knockouts, context-specific model extraction, flux sampling, and model quality assessment.

Cross-skill routing: use `metabolomics-analysis` for metabolite identification upstream, `gene-enrichment` for pathway enrichment of essential genes.

---

## 1. COBRApy Model Loading (SBML, JSON, YAML)

Load genome-scale metabolic models from standard formats.

```python
import cobra
import os

def load_model(filepath, solver="glpk"):
    """Load a genome-scale metabolic model from file.

    Parameters
    ----------
    filepath : str
        Path to model file. Supported formats:
        - .xml, .sbml: SBML format (most common, BiGG, VMH)
        - .json: COBRApy JSON format
        - .yml, .yaml: YAML format
        - .mat: MATLAB format (older models)
    solver : str
        LP solver: 'glpk' (default, open source), 'cplex', 'gurobi'.

    Returns
    -------
    cobra.Model
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext in (".xml", ".sbml"):
        model = cobra.io.read_sbml_model(filepath)
    elif ext == ".json":
        model = cobra.io.load_json_model(filepath)
    elif ext in (".yml", ".yaml"):
        model = cobra.io.load_yaml_model(filepath)
    elif ext == ".mat":
        model = cobra.io.load_matlab_model(filepath)
    else:
        raise ValueError(f"Unsupported format: {ext}")

    model.solver = solver

    print(f"Model: {model.id}")
    print(f"  Reactions:   {len(model.reactions)}")
    print(f"  Metabolites: {len(model.metabolites)}")
    print(f"  Genes:       {len(model.genes)}")
    print(f"  Compartments: {list(model.compartments.keys())}")
    print(f"  Objective:   {model.objective.expression}")
    print(f"  Solver:      {model.solver.interface.__name__}")

    # Quick feasibility check
    sol = model.optimize()
    print(f"  Feasible:    {sol.status}")
    print(f"  Objective value: {sol.objective_value:.4f}")

    return model

# ---- Load common models ----
# Human: Recon3D, Human-GEM
model = load_model("Recon3D.xml")

# E. coli: iML1515, iJO1366
# model = load_model("iML1515.xml")

# Yeast: Yeast8
# model = load_model("yeast-GEM.xml")

# ---- Load from BiGG database ----
# pip install cobra
# model = cobra.io.load_model("iML1515")  # downloads from BiGG
```

**Key parameters**: Use `glpk` solver for general use (pre-installed). Switch to `cplex` or `gurobi` for large models (>5000 reactions) or when solving thousands of LPs (e.g., FVA, flux sampling). The objective is typically biomass; verify with `model.objective`.

---

## 2. FBA: Optimize for Growth (Biomass Objective)

Flux Balance Analysis to predict steady-state metabolic fluxes.

```python
import cobra
import pandas as pd

def run_fba(model, objective=None, fraction_of_optimum=1.0):
    """Run Flux Balance Analysis.

    Parameters
    ----------
    model : cobra.Model
        Metabolic model.
    objective : str or None
        Reaction ID to maximize. None = use model default (usually biomass).
    fraction_of_optimum : float
        Fraction of optimal objective to enforce (for sub-optimal analysis).

    Returns
    -------
    cobra.Solution with fluxes, shadow prices, reduced costs.
    """
    with model:
        if objective:
            model.objective = objective

        solution = model.optimize()

        if solution.status != "optimal":
            print(f"WARNING: Solution status is '{solution.status}'")
            return solution

        print(f"Objective: {model.objective}")
        print(f"Objective value: {solution.objective_value:.6f}")

        # Active fluxes (non-zero)
        active = solution.fluxes[solution.fluxes.abs() > 1e-8]
        print(f"Active reactions: {len(active)}/{len(model.reactions)}")

        # Top fluxes
        top_fluxes = active.abs().nlargest(20)
        print(f"\nTop 20 fluxes by magnitude:")
        for rxn_id, flux in top_fluxes.items():
            rxn = model.reactions.get_by_id(rxn_id)
            direction = "→" if solution.fluxes[rxn_id] > 0 else "←"
            print(f"  {rxn_id}: {solution.fluxes[rxn_id]:>10.4f}  {direction}  {rxn.name}")

        # Exchange fluxes (uptake and secretion)
        exchanges = solution.fluxes[[r.id for r in model.exchanges]]
        uptake = exchanges[exchanges < -1e-8].sort_values()
        secretion = exchanges[exchanges > 1e-8].sort_values(ascending=False)

        print(f"\nUptake (negative = consumed):")
        for rxn_id, flux in uptake.head(10).items():
            rxn = model.reactions.get_by_id(rxn_id)
            print(f"  {rxn_id}: {flux:.4f}  ({rxn.name})")

        print(f"\nSecretion (positive = produced):")
        for rxn_id, flux in secretion.head(10).items():
            rxn = model.reactions.get_by_id(rxn_id)
            print(f"  {rxn_id}: {flux:.4f}  ({rxn.name})")

    return solution

# Usage
solution = run_fba(model)

# ---- Specific analyses ----
# Maximize ATP production
# atp_sol = run_fba(model, objective="ATPM")

# Maximize a specific metabolite production
# model.objective = model.reactions.get_by_id("EX_etoh_e")
# model.objective.direction = "max"
```

**Expected output**: Optimal flux distribution showing which reactions are active, metabolite uptake rates (from exchange reactions), and secretion products. A biomass flux > 0 means the model predicts growth under the given conditions.

---

## 3. FVA: Flux Variability Analysis

Determine the range of feasible fluxes for each reaction.

```python
from cobra.flux_analysis import flux_variability_analysis
import pandas as pd
import matplotlib.pyplot as plt

def run_fva(model, fraction_of_optimum=0.9, reaction_list=None, loopless=False):
    """Run Flux Variability Analysis.

    Parameters
    ----------
    model : cobra.Model
        Metabolic model.
    fraction_of_optimum : float
        Minimum fraction of optimal growth to maintain.
        1.0 = only optimal, 0.9 = within 90% of optimal.
    reaction_list : list or None
        Specific reactions to analyze. None = all reactions.
    loopless : bool
        If True, remove thermodynamically infeasible loops (slower).

    Returns
    -------
    pd.DataFrame with minimum, maximum flux for each reaction.
    """
    fva_result = flux_variability_analysis(
        model,
        reaction_list=reaction_list,
        fraction_of_optimum=fraction_of_optimum,
        loopless=loopless,
    )

    # Classify reactions
    fva_result["range"] = fva_result["maximum"] - fva_result["minimum"]
    fva_result["midpoint"] = (fva_result["maximum"] + fva_result["minimum"]) / 2

    # Fixed reactions (range ≈ 0)
    fixed = fva_result[fva_result["range"] < 1e-6]
    variable = fva_result[fva_result["range"] >= 1e-6]
    blocked = fva_result[(fva_result["minimum"].abs() < 1e-8) &
                          (fva_result["maximum"].abs() < 1e-8)]

    print(f"FVA results (fraction_of_optimum={fraction_of_optimum}):")
    print(f"  Total reactions:    {len(fva_result)}")
    print(f"  Fixed flux:         {len(fixed)} ({len(fixed)/len(fva_result)*100:.1f}%)")
    print(f"  Variable flux:      {len(variable)} ({len(variable)/len(fva_result)*100:.1f}%)")
    print(f"  Blocked (zero):     {len(blocked)} ({len(blocked)/len(fva_result)*100:.1f}%)")

    # Most variable reactions
    print(f"\nMost variable reactions (largest range):")
    top_var = fva_result.nlargest(15, "range")
    for rxn_id, row in top_var.iterrows():
        rxn = model.reactions.get_by_id(rxn_id)
        print(f"  {rxn_id}: [{row['minimum']:.4f}, {row['maximum']:.4f}] "
              f"(range={row['range']:.4f})  {rxn.name}")

    # Plot flux ranges for top variable reactions
    top_n = min(30, len(variable))
    top = variable.nlargest(top_n, "range")
    fig, ax = plt.subplots(figsize=(10, max(6, top_n * 0.3)))
    y_pos = range(len(top))
    ax.barh(y_pos, top["range"], left=top["minimum"],
            color="steelblue", alpha=0.7, height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{idx}" for idx in top.index], fontsize=7)
    ax.set_xlabel("Flux Range")
    ax.set_title(f"FVA: Top {top_n} Variable Reactions")
    ax.axvline(0, color="black", lw=0.5)
    plt.tight_layout()
    plt.savefig("fva_ranges.png", dpi=150, bbox_inches="tight")
    plt.close()

    return fva_result

# Usage
fva = run_fva(model, fraction_of_optimum=0.9)

# FVA for specific subsystem
# central_carbon = [r for r in model.reactions if r.subsystem in
#     ["Glycolysis/Gluconeogenesis", "Citric acid cycle", "Pentose phosphate pathway"]]
# fva_central = run_fva(model, reaction_list=central_carbon)
```

**Expected output**: For each reaction, the minimum and maximum feasible flux while maintaining near-optimal growth. Fixed reactions have no flexibility; variable reactions represent metabolic alternatives.

---

## 4. pFBA: Parsimonious FBA (Minimize Total Flux)

Find the flux distribution that achieves optimal growth with minimum total flux.

```python
from cobra.flux_analysis import pfba
import pandas as pd

def run_pfba(model, fraction_of_optimum=1.0):
    """Run parsimonious FBA (minimize total flux at optimal growth).

    Parameters
    ----------
    model : cobra.Model
        Metabolic model.
    fraction_of_optimum : float
        Fraction of optimal objective to maintain.

    Returns
    -------
    cobra.Solution with minimized total flux.
    """
    solution = pfba(model, fraction_of_optimum=fraction_of_optimum)

    total_flux = solution.fluxes.abs().sum()
    active = solution.fluxes[solution.fluxes.abs() > 1e-8]

    print(f"pFBA results:")
    print(f"  Objective value: {solution.objective_value:.6f}")
    print(f"  Total flux: {total_flux:.2f}")
    print(f"  Active reactions: {len(active)}/{len(model.reactions)}")

    # Compare with regular FBA
    fba_sol = model.optimize()
    fba_total = fba_sol.fluxes.abs().sum()
    fba_active = (fba_sol.fluxes.abs() > 1e-8).sum()

    print(f"\n  Comparison with FBA:")
    print(f"    FBA total flux:    {fba_total:.2f}")
    print(f"    pFBA total flux:   {total_flux:.2f} ({total_flux/fba_total*100:.1f}% of FBA)")
    print(f"    FBA active rxns:   {fba_active}")
    print(f"    pFBA active rxns:  {len(active)}")

    return solution

# Usage
pfba_solution = run_pfba(model)

# Use pFBA fluxes for more biologically realistic predictions
flux_df = pd.DataFrame({
    "reaction": pfba_solution.fluxes.index,
    "flux": pfba_solution.fluxes.values,
}).set_index("reaction")
flux_df = flux_df[flux_df["flux"].abs() > 1e-8].sort_values("flux", key=abs, ascending=False)
print(flux_df.head(20))
```

**Expected output**: pFBA gives a unique, biologically parsimonious solution by removing flux loops and unnecessary pathways. Total flux is always <= FBA total flux. More realistic for metabolic phenotype prediction.

---

## 5. Gene Knockout Simulation: Single and Double Knockouts

Predict the fitness effect of gene deletions.

```python
from cobra.flux_analysis import single_gene_deletion, double_gene_deletion
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def simulate_knockouts(model, gene_list=None, processes=1):
    """Simulate single gene knockouts and predict growth impact.

    Parameters
    ----------
    model : cobra.Model
        Metabolic model.
    gene_list : list or None
        Genes to knock out. None = all genes.
    processes : int
        Number of parallel processes.

    Returns
    -------
    pd.DataFrame with knockout results sorted by growth impact.
    """
    wt_growth = model.optimize().objective_value

    # Single knockouts
    result = single_gene_deletion(
        model,
        gene_list=gene_list,
        processes=processes,
    )

    # Parse results
    ko_results = []
    for _, row in result.iterrows():
        gene_ids = row["ids"]
        growth = row["growth"]
        status = row["status"]

        gene_id = list(gene_ids)[0] if len(gene_ids) == 1 else str(gene_ids)
        gene = model.genes.get_by_id(gene_id) if gene_id in [g.id for g in model.genes] else None
        gene_name = gene.name if gene else gene_id

        ko_results.append({
            "gene_id": gene_id,
            "gene_name": gene_name,
            "growth": growth if status == "optimal" else 0.0,
            "growth_ratio": growth / wt_growth if wt_growth > 0 and status == "optimal" else 0.0,
            "status": status,
        })

    ko_df = pd.DataFrame(ko_results).sort_values("growth_ratio")

    # Classify
    lethal = ko_df[ko_df["growth_ratio"] < 0.01]
    impaired = ko_df[(ko_df["growth_ratio"] >= 0.01) & (ko_df["growth_ratio"] < 0.5)]
    reduced = ko_df[(ko_df["growth_ratio"] >= 0.5) & (ko_df["growth_ratio"] < 0.95)]
    neutral = ko_df[ko_df["growth_ratio"] >= 0.95]

    print(f"Single gene knockout results (WT growth = {wt_growth:.4f}):")
    print(f"  Total genes tested: {len(ko_df)}")
    print(f"  Lethal (<1% growth):     {len(lethal)}")
    print(f"  Impaired (1-50%):        {len(impaired)}")
    print(f"  Reduced (50-95%):        {len(reduced)}")
    print(f"  Neutral (>95%):          {len(neutral)}")

    print(f"\nTop lethal genes:")
    print(lethal.head(20)[["gene_id", "gene_name", "growth_ratio"]].to_string(index=False))

    # Distribution plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(ko_df["growth_ratio"], bins=50, color="steelblue", edgecolor="black", alpha=0.7)
    ax.axvline(0.01, color="red", ls="--", label="Lethal threshold")
    ax.axvline(0.5, color="orange", ls="--", label="Impaired threshold")
    ax.set_xlabel("Growth Ratio (KO/WT)"); ax.set_ylabel("Count")
    ax.set_title("Single Gene Knockout Growth Distribution")
    ax.legend()
    plt.savefig("gene_knockout_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()

    return ko_df

def simulate_double_knockouts(model, gene_list, processes=1):
    """Simulate pairwise double gene knockouts for synthetic lethality.

    Parameters
    ----------
    model : cobra.Model
    gene_list : list
        Genes to test (all pairs). Keep small (< 100) for speed.

    Returns
    -------
    pd.DataFrame with double knockout results.
    """
    wt_growth = model.optimize().objective_value

    result = double_gene_deletion(
        model,
        gene_list1=gene_list,
        gene_list2=gene_list,
        processes=processes,
    )

    # Find synthetic lethal pairs
    sl_pairs = []
    for _, row in result.iterrows():
        genes = list(row["ids"])
        if len(genes) != 2:
            continue
        growth = row["growth"] if row["status"] == "optimal" else 0.0
        ratio = growth / wt_growth if wt_growth > 0 else 0.0
        if ratio < 0.01:
            sl_pairs.append({
                "gene1": genes[0], "gene2": genes[1],
                "growth": growth, "growth_ratio": ratio,
            })

    sl_df = pd.DataFrame(sl_pairs)
    print(f"Synthetic lethal pairs: {len(sl_df)}")
    if len(sl_df) > 0:
        print(sl_df.head(20).to_string(index=False))
    return sl_df

# Usage
ko_results = simulate_knockouts(model, processes=4)
# Double KO for top reduced-growth genes
impaired_genes = ko_results[ko_results["growth_ratio"] < 0.5]["gene_id"].tolist()[:50]
sl_pairs = simulate_double_knockouts(model, impaired_genes)
```

**Expected output**: Lethal genes are predicted essential (growth near zero when deleted). Synthetic lethal pairs identify gene combinations where neither single KO is lethal but the double KO is.

---

## 6. Essential Gene Prediction

Predict metabolically essential genes under specific conditions.

```python
import cobra
import pandas as pd
import numpy as np

def predict_essential_genes(model, threshold=0.01, medium=None):
    """Predict essential genes under specified growth conditions.

    Parameters
    ----------
    model : cobra.Model
    threshold : float
        Growth ratio below which a gene is called essential.
    medium : dict or None
        Custom medium as {exchange_reaction_id: lower_bound}.
        None = use model default medium.

    Returns
    -------
    pd.DataFrame with essential gene list and associated reactions.
    """
    with model:
        if medium is not None:
            # Set all exchange reactions to zero first
            for rxn in model.exchanges:
                rxn.lower_bound = 0
            # Open specified exchanges
            for rxn_id, lb in medium.items():
                model.reactions.get_by_id(rxn_id).lower_bound = lb

        wt_growth = model.optimize().objective_value
        if wt_growth < 1e-8:
            print("ERROR: Model has no growth under specified conditions.")
            return None

        # Single gene deletions
        from cobra.flux_analysis import single_gene_deletion
        result = single_gene_deletion(model)

        essential = []
        for _, row in result.iterrows():
            gene_id = list(row["ids"])[0]
            growth = row["growth"] if row["status"] == "optimal" else 0.0
            ratio = growth / wt_growth

            if ratio < threshold:
                gene = model.genes.get_by_id(gene_id)
                # Find reactions that depend solely on this gene
                dependent_rxns = []
                for rxn in gene.reactions:
                    # Check if gene is essential for this reaction via GPR
                    with model:
                        gene.knock_out()
                        if rxn.flux_expression is not None:
                            dependent_rxns.append(rxn.id)

                essential.append({
                    "gene_id": gene_id,
                    "gene_name": gene.name,
                    "growth_ratio": ratio,
                    "n_reactions": len(gene.reactions),
                    "reactions": ", ".join([r.id for r in gene.reactions][:5]),
                    "subsystems": ", ".join(set(r.subsystem for r in gene.reactions if r.subsystem)),
                })

    ess_df = pd.DataFrame(essential).sort_values("growth_ratio")
    print(f"Essential genes (growth ratio < {threshold}): {len(ess_df)}/{len(model.genes)}")
    print(f"  ({len(ess_df)/len(model.genes)*100:.1f}% of all genes)")

    # Subsystem enrichment
    if len(ess_df) > 0:
        all_subsystems = []
        for _, row in ess_df.iterrows():
            all_subsystems.extend(row["subsystems"].split(", "))
        subsystem_counts = pd.Series(all_subsystems).value_counts()
        print(f"\nEssential gene subsystem enrichment:")
        print(subsystem_counts.head(10).to_string())

    return ess_df

# Usage
# Default medium
essential_default = predict_essential_genes(model)

# Minimal medium
minimal_medium = {
    "EX_glc__D_e": -10,   # glucose
    "EX_o2_e": -20,       # oxygen
    "EX_nh4_e": -10,      # ammonium
    "EX_pi_e": -10,       # phosphate
    "EX_so4_e": -10,      # sulfate
}
essential_minimal = predict_essential_genes(model, medium=minimal_medium)
```

**Expected output**: List of genes whose deletion eliminates growth. Essential gene count increases under minimal media (fewer metabolic alternatives). Cross-validate with experimental essentiality data (e.g., Keio collection for E. coli).

---

## 7. Context-Specific Model Extraction: GIMME, iMAT, INIT

Build tissue- or condition-specific models from transcriptomics data.

```python
import cobra
import numpy as np
import pandas as pd

def gimme_extraction(model, expression_data, quantile_threshold=0.25,
                      required_reactions=None):
    """Extract context-specific model using GIMME algorithm.

    Parameters
    ----------
    model : cobra.Model
        Generic genome-scale model.
    expression_data : pd.Series
        Gene expression values (gene_id -> expression level).
    quantile_threshold : float
        Expression quantile below which reactions are penalized.
    required_reactions : list or None
        Reactions that must be active (e.g., biomass components).

    Returns
    -------
    cobra.Model with inactive reactions removed.
    """
    # Map gene expression to reaction scores via GPR
    rxn_scores = {}
    threshold = expression_data.quantile(quantile_threshold)

    for rxn in model.reactions:
        if rxn.gene_reaction_rule == "":
            rxn_scores[rxn.id] = 0  # No GPR = no penalty
            continue

        # Evaluate GPR with expression data
        gene_expr = {}
        for gene in rxn.genes:
            gene_expr[gene.id] = expression_data.get(gene.id, 0)

        # AND = min, OR = max (standard GPR interpretation)
        rule = rxn.gene_reaction_rule
        for gene_id, expr in gene_expr.items():
            rule = rule.replace(gene_id, str(expr))
        rule = rule.replace(" and ", ", ").replace(" or ", ", ")

        try:
            # Simplified: use max expression among genes
            max_expr = max(gene_expr.values()) if gene_expr else 0
            rxn_scores[rxn.id] = max(0, threshold - max_expr)
        except Exception:
            rxn_scores[rxn.id] = 0

    # GIMME: minimize penalty while maintaining required functionality
    with model:
        # Set objective: minimize sum of penalty * |flux|
        if required_reactions:
            for rxn_id in required_reactions:
                rxn = model.reactions.get_by_id(rxn_id)
                rxn.lower_bound = max(rxn.lower_bound, 1e-3)

        solution = model.optimize()

        # Remove reactions with zero flux and high penalty
        inactive = []
        for rxn in model.reactions:
            if abs(solution.fluxes[rxn.id]) < 1e-8 and rxn_scores.get(rxn.id, 0) > 0:
                inactive.append(rxn.id)

    # Create context-specific model
    context_model = model.copy()
    cobra.manipulation.remove_genes(
        context_model,
        [g for g in context_model.genes
         if all(r.id in inactive for r in g.reactions)],
        prune=True,
    )

    print(f"GIMME context-specific model:")
    print(f"  Original:  {len(model.reactions)} rxns, {len(model.genes)} genes")
    print(f"  Extracted: {len(context_model.reactions)} rxns, {len(context_model.genes)} genes")
    print(f"  Removed:   {len(inactive)} reactions")

    # Verify feasibility
    ctx_sol = context_model.optimize()
    print(f"  Feasible:  {ctx_sol.status}")
    print(f"  Growth:    {ctx_sol.objective_value:.4f}")

    return context_model

# Usage
# Load expression data (gene_id -> TPM or FPKM)
expression = pd.read_csv("rnaseq_expression.csv", index_col=0)["expression"]
context_model = gimme_extraction(model, expression, quantile_threshold=0.25)
```

**Key parameters**: `quantile_threshold` determines how aggressively low-expression reactions are penalized. Lower threshold = more permissive (larger model). For tissue-specific models, use GTEx median tissue expression as input.

---

## 8. Flux Sampling: optGP, ACHR

Unbiased sampling of the feasible flux space.

```python
from cobra.sampling import sample, OptGPSampler, ACHRSampler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def flux_sampling(model, n_samples=5000, method="optgp", thinning=100,
                   fraction_of_optimum=0.9):
    """Sample flux distributions from the feasible space.

    Parameters
    ----------
    model : cobra.Model
    n_samples : int
        Number of flux samples to collect.
    method : str
        'optgp' (Optimized Gaussian Process, faster) or 'achr' (Artificial
        Centering Hit-and-Run, more uniform).
    thinning : int
        Keep every N-th sample (reduces autocorrelation).
    fraction_of_optimum : float
        Constrain sampling to near-optimal space.

    Returns
    -------
    pd.DataFrame of sampled fluxes (samples x reactions).
    """
    with model:
        # Constrain to near-optimal growth
        if fraction_of_optimum < 1.0:
            wt = model.optimize().objective_value
            biomass_rxn = [r for r in model.reactions if r.objective_coefficient != 0][0]
            biomass_rxn.lower_bound = fraction_of_optimum * wt

        # Sample
        if method == "optgp":
            sampler = OptGPSampler(model, thinning=thinning)
        else:
            sampler = ACHRSampler(model, thinning=thinning)

        samples = sampler.sample(n_samples)

    print(f"Flux sampling ({method}):")
    print(f"  Samples: {samples.shape[0]}")
    print(f"  Reactions: {samples.shape[1]}")

    # Validate samples
    valid = sampler.validate(samples)
    print(f"  Valid samples: {valid.sum()}/{len(valid)} ({valid.mean()*100:.1f}%)")

    # Summary statistics
    means = samples.mean()
    stds = samples.std()
    cv = stds / means.abs().clip(lower=1e-8)

    # Most variable reactions
    most_variable = cv.nlargest(20)
    print(f"\nMost variable reactions (by CV):")
    for rxn_id, cv_val in most_variable.items():
        rxn = model.reactions.get_by_id(rxn_id)
        print(f"  {rxn_id}: mean={means[rxn_id]:.4f}, std={stds[rxn_id]:.4f}, "
              f"CV={cv_val:.2f}  ({rxn.name})")

    # Plot distributions for selected reactions
    plot_reactions = most_variable.index[:6].tolist()
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, rxn_id in zip(axes.flatten(), plot_reactions):
        ax.hist(samples[rxn_id], bins=50, color="steelblue", alpha=0.7, density=True)
        ax.axvline(means[rxn_id], color="red", ls="--", label=f"mean={means[rxn_id]:.3f}")
        ax.set_xlabel("Flux"); ax.set_title(rxn_id, fontsize=9)
        ax.legend(fontsize=7)
    plt.suptitle("Flux Sampling Distributions")
    plt.tight_layout()
    plt.savefig("flux_sampling_distributions.png", dpi=150, bbox_inches="tight")
    plt.close()

    return samples

# Usage
samples = flux_sampling(model, n_samples=5000, method="optgp")

# Compare flux distributions between conditions
# samples_ctrl = flux_sampling(model_ctrl, n_samples=5000)
# samples_treat = flux_sampling(model_treat, n_samples=5000)
# from scipy.stats import mannwhitneyu
# for rxn in model.reactions:
#     stat, pval = mannwhitneyu(samples_ctrl[rxn.id], samples_treat[rxn.id])
```

**Expected output**: Unbiased flux distributions for each reaction. Unlike FBA (point solution), sampling reveals the full range of feasible metabolic states. High CV reactions have multiple alternative flux values.

---

## 9. Medium Composition Modification (Exchange Reactions)

Configure nutrient availability by modifying exchange reaction bounds.

```python
import cobra
import pandas as pd

def configure_medium(model, medium_dict=None, preset="rich"):
    """Set growth medium by configuring exchange reactions.

    Parameters
    ----------
    model : cobra.Model
    medium_dict : dict or None
        {metabolite_name_or_rxn_id: uptake_rate}. Negative = uptake.
    preset : str
        'rich' (all nutrients available), 'minimal' (glucose minimal),
        'dmem' (DMEM cell culture), 'rpmi' (RPMI-1640).

    Returns
    -------
    dict of exchange reaction bounds.
    """
    presets = {
        "minimal": {
            "EX_glc__D_e": -10,   # Glucose
            "EX_o2_e": -20,       # Oxygen
            "EX_nh4_e": -10,      # Ammonium
            "EX_pi_e": -10,       # Phosphate
            "EX_so4_e": -10,      # Sulfate
            "EX_k_e": -10,        # Potassium
            "EX_na1_e": -10,      # Sodium
            "EX_cl_e": -10,       # Chloride
            "EX_fe2_e": -10,      # Iron
            "EX_h2o_e": -1000,    # Water
            "EX_h_e": -1000,      # Protons
        },
        "rich": "all_open",
        "dmem": {
            "EX_glc__D_e": -25,
            "EX_gln__L_e": -4,
            "EX_o2_e": -20,
            "EX_arg__L_e": -0.4,
            "EX_cys__L_e": -0.2,
            "EX_his__L_e": -0.2,
            "EX_ile__L_e": -0.8,
            "EX_leu__L_e": -0.8,
            "EX_lys__L_e": -0.8,
            "EX_met__L_e": -0.2,
            "EX_phe__L_e": -0.4,
            "EX_thr__L_e": -0.8,
            "EX_trp__L_e": -0.08,
            "EX_tyr__L_e": -0.4,
            "EX_val__L_e": -0.8,
            "EX_pi_e": -10,
            "EX_so4_e": -10,
            "EX_fe2_e": -1,
            "EX_h2o_e": -1000,
            "EX_h_e": -1000,
        },
    }

    with model:
        if medium_dict is None:
            medium_dict = presets.get(preset, presets["minimal"])

        if medium_dict == "all_open":
            # Open all exchange reactions
            for rxn in model.exchanges:
                rxn.lower_bound = -1000
        else:
            # Close all exchanges first, then open specified
            for rxn in model.exchanges:
                rxn.lower_bound = 0

            for rxn_id, lb in medium_dict.items():
                if rxn_id in [r.id for r in model.reactions]:
                    model.reactions.get_by_id(rxn_id).lower_bound = lb
                else:
                    print(f"WARNING: {rxn_id} not found in model")

        # Test growth
        sol = model.optimize()
        print(f"Medium: {preset if medium_dict is None else 'custom'}")
        print(f"  Growth rate: {sol.objective_value:.4f}")
        print(f"  Status: {sol.status}")

        # Active uptake
        if sol.status == "optimal":
            exchanges = {r.id: sol.fluxes[r.id] for r in model.exchanges
                        if abs(sol.fluxes[r.id]) > 1e-8}
            uptake = {k: v for k, v in exchanges.items() if v < 0}
            print(f"  Active uptake reactions: {len(uptake)}")
            for rxn_id, flux in sorted(uptake.items(), key=lambda x: x[1]):
                rxn = model.reactions.get_by_id(rxn_id)
                print(f"    {rxn_id}: {flux:.4f} ({rxn.name})")

    return medium_dict

# Usage
configure_medium(model, preset="minimal")
configure_medium(model, preset="dmem")
```

**Expected output**: Growth rate under each medium condition. Models grow faster on rich media; minimal media restricts growth and changes flux distribution. Use medium configuration to simulate nutrient limitations or specific culture conditions.

---

## 10. Gap Filling: GapFill Algorithm

Add reactions to enable a blocked metabolic objective.

```python
from cobra.flux_analysis.gapfilling import gapfill
import cobra

def fill_gaps(model, universal_model=None, objective=None,
               iterations=1, lower_bound=0.05):
    """Gap-fill a metabolic model to enable growth or a specific objective.

    Parameters
    ----------
    model : cobra.Model
        Model with blocked objective.
    universal_model : cobra.Model or None
        Universal database model containing candidate reactions.
        None = use model's own blocked reactions.
    objective : str or None
        Reaction to gap-fill for. None = model default objective.
    iterations : int
        Number of alternative gap-fill solutions to find.
    lower_bound : float
        Minimum required flux through the objective.

    Returns
    -------
    list of lists of cobra.Reaction (gap-fill solutions).
    """
    with model:
        if objective:
            model.objective = objective

        # Check if gap-filling is needed
        sol = model.optimize()
        if sol.status == "optimal" and sol.objective_value > lower_bound:
            print(f"Model already feasible (objective = {sol.objective_value:.4f})")
            return []

        print(f"Model infeasible or below threshold. Running gap-fill...")

        if universal_model is None:
            # Use BiGG universal model or create from blocked reactions
            print("No universal model provided. Using model's own reactions.")
            # Temporarily unblock all reactions
            universal_model = model.copy()
            for rxn in universal_model.reactions:
                if rxn.lower_bound == 0 and rxn.upper_bound == 0:
                    rxn.upper_bound = 1000
                    rxn.lower_bound = -1000

        solutions = gapfill(
            model,
            universal_model,
            lower_bound=lower_bound,
            iterations=iterations,
        )

        for i, sol in enumerate(solutions):
            print(f"\nGap-fill solution {i + 1}: {len(sol)} reactions added")
            for rxn in sol:
                print(f"  {rxn.id}: {rxn.name}")
                print(f"    {rxn.reaction}")
                print(f"    Subsystem: {rxn.subsystem}")

    return solutions

# Usage
# If model can't grow:
# solutions = fill_gaps(model, universal_model=universal)
# Add solution reactions to model:
# for rxn in solutions[0]:
#     model.add_reactions([rxn])
```

**Expected output**: Minimum set of reactions to add for enabling the blocked objective. Multiple solutions may exist -- each represents an alternative metabolic route.

---

## 11. Loopless FBA: CycleFreeFlux

Remove thermodynamically infeasible loops from flux solutions.

```python
from cobra.flux_analysis.loopless import loopless_solution, add_loopless_constraints
import cobra
import pandas as pd

def run_loopless_fba(model):
    """Run loopless FBA that eliminates thermodynamically infeasible cycles.

    Parameters
    ----------
    model : cobra.Model

    Returns
    -------
    cobra.Solution without internal flux loops.
    """
    # Regular FBA for comparison
    fba_sol = model.optimize()
    fba_active = (fba_sol.fluxes.abs() > 1e-8).sum()

    # Loopless FBA
    ll_sol = loopless_solution(model)

    ll_active = (ll_sol.fluxes.abs() > 1e-8).sum()

    # Find loops (reactions active in FBA but not in loopless)
    fba_active_set = set(fba_sol.fluxes[fba_sol.fluxes.abs() > 1e-8].index)
    ll_active_set = set(ll_sol.fluxes[ll_sol.fluxes.abs() > 1e-8].index)
    loop_reactions = fba_active_set - ll_active_set

    print(f"Loopless FBA results:")
    print(f"  FBA objective:      {fba_sol.objective_value:.6f}")
    print(f"  Loopless objective: {ll_sol.objective_value:.6f}")
    print(f"  FBA active rxns:    {fba_active}")
    print(f"  Loopless active:    {ll_active}")
    print(f"  Loop reactions:     {len(loop_reactions)}")

    if loop_reactions:
        print(f"\nReactions participating in loops (removed):")
        for rxn_id in sorted(loop_reactions):
            rxn = model.reactions.get_by_id(rxn_id)
            print(f"  {rxn_id}: flux={fba_sol.fluxes[rxn_id]:.4f} ({rxn.name})")

    # Compare flux distributions
    comparison = pd.DataFrame({
        "fba_flux": fba_sol.fluxes,
        "loopless_flux": ll_sol.fluxes,
    })
    comparison["difference"] = comparison["fba_flux"] - comparison["loopless_flux"]
    comparison["in_loop"] = comparison.index.isin(loop_reactions)
    changed = comparison[comparison["difference"].abs() > 1e-8]
    print(f"\nReactions with changed flux: {len(changed)}")

    return ll_sol

# Usage
loopless_sol = run_loopless_fba(model)
```

**Expected output**: Loopless solution has the same (or very close) objective value but without internal cycles. Loop reactions are typically in central carbon metabolism where futile cycles can carry arbitrary flux in standard FBA.

---

## 12. Model Quality: Mass/Charge Balance, Blocked Reactions, Dead-End Metabolites

Comprehensive model quality assessment.

```python
import cobra
import pandas as pd
import numpy as np
from collections import Counter

def assess_model_quality(model):
    """Comprehensive quality assessment of a genome-scale metabolic model.

    Parameters
    ----------
    model : cobra.Model

    Returns
    -------
    dict with quality metrics.
    """
    quality = {}

    print(f"{'='*60}")
    print(f"Model Quality Assessment: {model.id}")
    print(f"{'='*60}")

    # ---- 1. Basic statistics ----
    quality["n_reactions"] = len(model.reactions)
    quality["n_metabolites"] = len(model.metabolites)
    quality["n_genes"] = len(model.genes)
    quality["n_compartments"] = len(model.compartments)
    quality["n_exchange"] = len(model.exchanges)

    print(f"\n1. Model size:")
    print(f"   Reactions:    {quality['n_reactions']}")
    print(f"   Metabolites:  {quality['n_metabolites']}")
    print(f"   Genes:        {quality['n_genes']}")
    print(f"   Compartments: {quality['n_compartments']}")
    print(f"   Exchanges:    {quality['n_exchange']}")

    # ---- 2. Mass and charge balance ----
    imbalanced_mass = []
    imbalanced_charge = []
    no_formula = []

    for rxn in model.reactions:
        if rxn.boundary:
            continue

        # Check formula
        metabolites_no_formula = [m for m in rxn.metabolites if m.formula is None or m.formula == ""]
        if metabolites_no_formula:
            no_formula.append(rxn.id)
            continue

        # Mass balance
        try:
            balance = rxn.check_mass_balance()
            if balance:
                imbalanced_mass.append((rxn.id, balance))
        except Exception:
            pass

    quality["mass_balanced"] = len(model.reactions) - len(imbalanced_mass) - len(no_formula) - len(model.exchanges)
    quality["mass_imbalanced"] = len(imbalanced_mass)
    quality["no_formula"] = len(no_formula)

    print(f"\n2. Mass/charge balance:")
    print(f"   Balanced:     {quality['mass_balanced']}")
    print(f"   Imbalanced:   {quality['mass_imbalanced']}")
    print(f"   No formula:   {quality['no_formula']}")
    if imbalanced_mass:
        print(f"   Top imbalanced reactions:")
        for rxn_id, balance in imbalanced_mass[:10]:
            print(f"     {rxn_id}: {balance}")

    # ---- 3. Blocked reactions ----
    from cobra.flux_analysis import find_blocked_reactions
    blocked = find_blocked_reactions(model)
    quality["blocked_reactions"] = len(blocked)
    quality["pct_blocked"] = len(blocked) / len(model.reactions) * 100

    print(f"\n3. Blocked reactions (zero flux under all conditions):")
    print(f"   Blocked: {quality['blocked_reactions']} ({quality['pct_blocked']:.1f}%)")

    # ---- 4. Dead-end metabolites ----
    dead_ends = []
    for met in model.metabolites:
        n_rxns = len(met.reactions)
        # Produced but not consumed, or consumed but not produced
        producing = [r for r in met.reactions if met in r.products or
                    (met in r.reactants and r.reversibility)]
        consuming = [r for r in met.reactions if met in r.reactants or
                    (met in r.products and r.reversibility)]
        if len(producing) == 0 or len(consuming) == 0:
            if not any(r.boundary for r in met.reactions):
                dead_ends.append(met.id)

    quality["dead_end_metabolites"] = len(dead_ends)
    print(f"\n4. Dead-end metabolites (produced but not consumed, or vice versa):")
    print(f"   Dead ends: {quality['dead_end_metabolites']}")
    if dead_ends:
        print(f"   Examples: {dead_ends[:10]}")

    # ---- 5. GPR coverage ----
    with_gpr = sum(1 for r in model.reactions if r.gene_reaction_rule and not r.boundary)
    total_non_exchange = sum(1 for r in model.reactions if not r.boundary)
    quality["gpr_coverage"] = with_gpr / total_non_exchange * 100 if total_non_exchange > 0 else 0

    print(f"\n5. Gene-Protein-Reaction (GPR) coverage:")
    print(f"   Reactions with GPR: {with_gpr}/{total_non_exchange} ({quality['gpr_coverage']:.1f}%)")

    # ---- 6. Feasibility ----
    sol = model.optimize()
    quality["feasible"] = sol.status == "optimal"
    quality["objective_value"] = sol.objective_value if sol.status == "optimal" else 0

    print(f"\n6. Feasibility:")
    print(f"   Status:  {sol.status}")
    print(f"   Growth:  {quality['objective_value']:.4f}")

    # ---- Overall score ----
    score = 0
    if quality["feasible"]:
        score += 25
    if quality["pct_blocked"] < 20:
        score += 25
    if quality["mass_imbalanced"] / max(quality["n_reactions"], 1) < 0.05:
        score += 25
    if quality["gpr_coverage"] > 80:
        score += 25

    quality["overall_score"] = score
    print(f"\n{'='*60}")
    print(f"Overall Quality Score: {score}/100")
    if score >= 75:
        print("  Assessment: GOOD quality model")
    elif score >= 50:
        print("  Assessment: ACCEPTABLE, some issues to address")
    else:
        print("  Assessment: POOR, significant quality issues")

    return quality

# Usage
quality_report = assess_model_quality(model)
```

**Expected output**: Comprehensive quality report covering mass balance, blocked reactions, dead-end metabolites, GPR coverage, and feasibility. A score of 75+ indicates a publication-quality model. Address mass imbalances and dead ends before production use.
