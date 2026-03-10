# Patient Population Sizing and Clinical Translation Recipes

Executable code templates for patient population estimation, biomarker prevalence, addressable market sizing, and clinical translation readiness.
Each recipe is production-ready Python with inline parameter documentation.

> **Parent skill**: [SKILL.md](SKILL.md) — full clinical trial analyst pipeline with MCP tools.
> **See also**: [biomarker-discovery](../biomarker-discovery/SKILL.md) for biomarker validation, [drug-target-analyst](../drug-target-analyst/SKILL.md) for target assessment.

---

## Recipe 1: Patient Population Calculation

Calculate addressable patient population from epidemiology data with geographic adjustments.

```python
import pandas as pd

def calculate_patient_population(
    annual_incidence,
    subtype_fraction,
    response_rate,
    geographic_regions=None,
):
    """
    Calculate addressable patient population for a drug program.

    Parameters
    ----------
    annual_incidence : dict
        Annual new cases per region: {"US": 200000, "EU5": 350000, "Japan": 80000}
    subtype_fraction : float
        Fraction of cases with target molecular subtype (0-1)
        e.g., 0.15 for EGFR-mutant NSCLC
    response_rate : float
        Expected response rate to treatment (0-1)
        e.g., 0.40 for 40% ORR
    geographic_regions : list, optional
        Which regions to include (default: all)

    Returns
    -------
    dict with population estimates by region and total
    """
    if geographic_regions:
        incidence = {k: v for k, v in annual_incidence.items() if k in geographic_regions}
    else:
        incidence = annual_incidence

    results = {}
    total_incidence = 0
    total_subtype = 0
    total_responders = 0

    for region, cases in incidence.items():
        subtype_cases = int(cases * subtype_fraction)
        responders = int(subtype_cases * response_rate)

        results[region] = {
            "annual_incidence": cases,
            "subtype_cases": subtype_cases,
            "expected_responders": responders,
        }

        total_incidence += cases
        total_subtype += subtype_cases
        total_responders += responders

    summary = {
        "total_annual_incidence": total_incidence,
        "subtype_fraction": subtype_fraction,
        "total_subtype_cases": total_subtype,
        "response_rate": response_rate,
        "total_expected_responders": total_responders,
        "by_region": results,
    }

    print(f"Patient Population Estimate")
    print(f"Subtype fraction: {subtype_fraction:.1%}")
    print(f"Expected response rate: {response_rate:.1%}\n")
    print(f"{'Region':<12} {'Incidence':>12} {'Subtype':>12} {'Responders':>12}")
    print("-" * 50)
    for region, data in results.items():
        print(f"{region:<12} {data['annual_incidence']:>12,} {data['subtype_cases']:>12,} {data['expected_responders']:>12,}")
    print("-" * 50)
    print(f"{'TOTAL':<12} {total_incidence:>12,} {total_subtype:>12,} {total_responders:>12,}")

    return summary


# Example: EGFR-mutant NSCLC
result = calculate_patient_population(
    annual_incidence={
        "US": 236_740,
        "EU5": 313_000,
        "Japan": 127_000,
        "China": 787_000,
        "RoW": 500_000,
    },
    subtype_fraction=0.15,    # EGFR mutation prevalence (Western; higher in Asia)
    response_rate=0.40,       # Expected ORR
    geographic_regions=["US", "EU5", "Japan"],
)
```

**Key Parameters:**
- `annual_incidence`: New cases per year by geographic region (from GLOBOCAN, SEER, or national cancer registries)
- `subtype_fraction`: Molecular subtype prevalence (from TCGA, clinical trial biomarker data)
- `response_rate`: Expected treatment response rate (from preclinical data or analogous clinical programs)

**Expected Output:**
- Population breakdown by region: total incidence, subtype-eligible cases, expected responders

---

## Recipe 2: Biomarker Prevalence Estimation from TCGA/cBioPortal

Estimate mutation frequency across cancer types using cBioPortal data.

```python
import requests
import pandas as pd

def estimate_biomarker_prevalence(gene_symbol, cancer_types=None):
    """
    Estimate mutation prevalence from cBioPortal pan-cancer data.

    Parameters
    ----------
    gene_symbol : str
        Gene symbol (e.g., "BRAF", "KRAS", "EGFR")
    cancer_types : list, optional
        Specific cancer type IDs to query (default: major cancer types)

    Returns
    -------
    DataFrame with mutation frequency per cancer type
    """
    base_url = "https://www.cbioportal.org/api"

    if cancer_types is None:
        # Major TCGA pan-cancer study IDs
        cancer_types = [
            "luad_tcga_pan_can_atlas_2018",   # Lung adenocarcinoma
            "lusc_tcga_pan_can_atlas_2018",   # Lung squamous
            "brca_tcga_pan_can_atlas_2018",   # Breast
            "coadread_tcga_pan_can_atlas_2018",  # Colorectal
            "skcm_tcga_pan_can_atlas_2018",   # Melanoma
            "paad_tcga_pan_can_atlas_2018",   # Pancreatic
            "ucec_tcga_pan_can_atlas_2018",   # Endometrial
            "blca_tcga_pan_can_atlas_2018",   # Bladder
            "hnsc_tcga_pan_can_atlas_2018",   # Head and neck
            "thca_tcga_pan_can_atlas_2018",   # Thyroid
            "ov_tcga_pan_can_atlas_2018",     # Ovarian
            "stad_tcga_pan_can_atlas_2018",   # Gastric
            "lihc_tcga_pan_can_atlas_2018",   # Liver
            "prad_tcga_pan_can_atlas_2018",   # Prostate
        ]

    results = []

    for study_id in cancer_types:
        try:
            # Get molecular profile ID
            profile_id = f"{study_id}_mutations"

            # Query mutation count for gene
            url = f"{base_url}/molecular-profiles/{profile_id}/genes/{gene_symbol}/mutations"
            params = {"projection": "SUMMARY"}
            resp = requests.get(url, params=params, timeout=10)

            if resp.status_code != 200:
                continue

            mutations = resp.json()
            n_mutant_samples = len(set(m.get("sampleId") for m in mutations))

            # Get total samples in study
            samples_url = f"{base_url}/studies/{study_id}/samples"
            samples_resp = requests.get(samples_url, params={"projection": "SUMMARY"}, timeout=10)
            n_total = len(samples_resp.json()) if samples_resp.ok else 0

            if n_total > 0:
                prevalence = n_mutant_samples / n_total
                cancer_name = study_id.split("_tcga")[0].upper()

                results.append({
                    "cancer_type": cancer_name,
                    "study_id": study_id,
                    "n_mutant": n_mutant_samples,
                    "n_total": n_total,
                    "prevalence": round(prevalence, 4),
                    "prevalence_pct": f"{prevalence:.1%}",
                })
        except Exception as e:
            continue

    results_df = pd.DataFrame(results).sort_values("prevalence", ascending=False).reset_index(drop=True)

    print(f"Biomarker Prevalence: {gene_symbol} mutations")
    print(f"Source: cBioPortal / TCGA PanCancer Atlas\n")
    if not results_df.empty:
        print(results_df[["cancer_type", "n_mutant", "n_total", "prevalence_pct"]].to_string(index=False))
    else:
        print("No mutation data found")

    return results_df


# Example
# result = estimate_biomarker_prevalence("BRAF")
```

**Key Parameters:**
- `gene_symbol`: Gene to query for mutation frequency
- `cancer_types`: cBioPortal study IDs (defaults to TCGA PanCancer Atlas studies)
- Reports mutation prevalence as fraction and percentage

**Expected Output:**
- Per-cancer-type mutation prevalence with sample counts, sorted by frequency

---

## Recipe 3: Addressable Patient Pool

Combine prevalence, line of therapy, and geographic reach into addressable patient estimate.

```python
import pandas as pd

def calculate_addressable_pool(
    annual_incidence,
    biomarker_rate,
    line_of_therapy_fraction,
    geographic_reach,
    market_penetration=1.0,
):
    """
    Calculate the addressable patient pool for a targeted therapy.

    Parameters
    ----------
    annual_incidence : int
        Total annual incidence for the indication (global or regional)
    biomarker_rate : float
        Fraction with required biomarker (0-1)
    line_of_therapy_fraction : float
        Fraction reaching the target line of therapy (0-1)
        e.g., 0.60 for 2L (60% of patients receive 2nd line treatment)
    geographic_reach : float
        Fraction of global market accessible (0-1)
        e.g., 0.40 for US + EU5 markets only
    market_penetration : float
        Expected market share at peak (0-1, default 1.0 for sizing only)

    Returns
    -------
    dict with addressable pool at each funnel stage
    """
    stages = [
        ("Total annual incidence", annual_incidence, 1.0),
        ("Biomarker-positive", annual_incidence * biomarker_rate, biomarker_rate),
        ("Reaching target line of therapy", annual_incidence * biomarker_rate * line_of_therapy_fraction,
         line_of_therapy_fraction),
        ("Geographic reach", annual_incidence * biomarker_rate * line_of_therapy_fraction * geographic_reach,
         geographic_reach),
        ("With market penetration", annual_incidence * biomarker_rate * line_of_therapy_fraction * geographic_reach * market_penetration,
         market_penetration),
    ]

    addressable = int(stages[-1][1])

    print(f"Addressable Patient Pool Funnel")
    print(f"{'Stage':<35} {'Patients':>12} {'Factor':>10}")
    print("-" * 60)
    for name, count, factor in stages:
        print(f"{name:<35} {int(count):>12,} {factor:>10.1%}")
    print("-" * 60)
    print(f"\nAddressable pool: {addressable:,} patients/year")

    return {
        "annual_incidence": annual_incidence,
        "biomarker_rate": biomarker_rate,
        "line_of_therapy_fraction": line_of_therapy_fraction,
        "geographic_reach": geographic_reach,
        "market_penetration": market_penetration,
        "addressable_patients": addressable,
        "funnel_stages": {name: int(count) for name, count, _ in stages},
    }


# Example: EGFR TKI in 2L NSCLC
result = calculate_addressable_pool(
    annual_incidence=2_000_000,      # Global NSCLC incidence
    biomarker_rate=0.15,             # EGFR mutation rate (global average)
    line_of_therapy_fraction=0.60,   # 60% reach 2nd line
    geographic_reach=0.40,           # US + EU5 + Japan
    market_penetration=0.25,         # Expected 25% market share
)
```

**Key Parameters:**
- Sequential funnel: incidence -> biomarker+ -> line of therapy -> geography -> market share
- Each factor multiplicatively reduces the addressable pool
- `line_of_therapy_fraction`: accounts for patients who progress or are too unfit for next line

**Expected Output:**
- Patient funnel with counts at each stage, final addressable pool estimate

---

## Recipe 4: Biomarker Readiness Scoring (0-100)

Composite readiness score with weighted components: clinical trials (35), active recruiting (20), PubMed (30), OpenAlex (15).

```python
import requests
import math
import pandas as pd

def score_biomarker_readiness(biomarker_name, disease_name=None):
    """
    Compute composite biomarker readiness score (0-100).

    Weights:
    - Clinical trials evidence: 35 points (phase-weighted)
    - Active recruiting trials: 20 points
    - PubMed literature: 30 points (log-scaled)
    - OpenAlex citations: 15 points (log-scaled)

    Parameters
    ----------
    biomarker_name : str
        Biomarker gene symbol or name
    disease_name : str, optional
        Disease context

    Returns
    -------
    dict with composite score, component scores, and readiness tier
    """
    search_term = f"{biomarker_name} biomarker"
    if disease_name:
        search_term += f" {disease_name}"

    # 1. Clinical Trials (35 pts max)
    try:
        ct_url = "https://clinicaltrials.gov/api/v2/studies"
        ct_resp = requests.get(ct_url, params={
            "query.term": search_term, "pageSize": 100, "format": "json"
        }, timeout=15)
        ct_data = ct_resp.json()
        studies = ct_data.get("studies", [])
        total_trials = ct_data.get("totalCount", 0)

        phase_points = {"PHASE1": 2, "PHASE2": 4, "PHASE3": 8, "PHASE4": 3}
        trial_score = 0
        recruiting = 0
        for s in studies:
            phases = s.get("protocolSection", {}).get("designModule", {}).get("phases", [])
            status = s.get("protocolSection", {}).get("statusModule", {}).get("overallStatus", "")
            for p in phases:
                trial_score += phase_points.get(p, 1)
            if status in ("RECRUITING", "ENROLLING_BY_INVITATION"):
                recruiting += 1
        trial_score = min(35, trial_score)
    except Exception:
        trial_score, recruiting, total_trials = 0, 0, 0

    # 2. Active Recruiting (20 pts max)
    recruiting_score = min(20, recruiting * 4)

    # 3. PubMed Literature (30 pts max)
    try:
        pm_resp = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={
            "db": "pubmed",
            "term": f"{biomarker_name}[Title/Abstract] AND biomarker[Title/Abstract]",
            "rettype": "count", "retmode": "json",
        }, timeout=10)
        pubmed_count = int(pm_resp.json().get("esearchresult", {}).get("count", 0))
        lit_score = min(30, int(5 * math.log2(pubmed_count + 1)))
    except Exception:
        pubmed_count, lit_score = 0, 0

    # 4. OpenAlex Citations (15 pts max)
    try:
        oa_resp = requests.get("https://api.openalex.org/works", params={
            "search": search_term, "per_page": 50,
        }, timeout=10)
        oa_works = oa_resp.json().get("results", [])
        total_cites = sum(w.get("cited_by_count", 0) for w in oa_works[:50])
        cite_score = min(15, int(3 * math.log2(total_cites + 1)))
    except Exception:
        total_cites, cite_score = 0, 0

    composite = trial_score + recruiting_score + lit_score + cite_score

    if composite >= 70:
        tier = "HIGH READINESS"
        description = "Validated biomarker with strong clinical and literature evidence"
    elif composite >= 40:
        tier = "MODERATE READINESS"
        description = "Emerging biomarker with growing evidence base"
    else:
        tier = "EARLY READINESS"
        description = "Exploratory biomarker, needs further validation"

    result = {
        "biomarker": biomarker_name,
        "disease": disease_name or "general",
        "composite_score": composite,
        "tier": tier,
        "description": description,
        "components": {
            "clinical_trials": {"score": trial_score, "max": 35, "total": total_trials},
            "active_recruiting": {"score": recruiting_score, "max": 20, "count": recruiting},
            "pubmed_literature": {"score": lit_score, "max": 30, "count": pubmed_count},
            "openalex_citations": {"score": cite_score, "max": 15, "total_citations": total_cites},
        },
    }

    print(f"\nBiomarker Readiness: {biomarker_name}")
    if disease_name:
        print(f"Disease: {disease_name}")
    print(f"Score: {composite}/100 — {tier}")
    print(f"  {description}\n")
    print(f"  Clinical trials:    {trial_score:2d}/35  ({total_trials} trials)")
    print(f"  Active recruiting:  {recruiting_score:2d}/20  ({recruiting} recruiting)")
    print(f"  PubMed literature:  {lit_score:2d}/30  ({pubmed_count} publications)")
    print(f"  OpenAlex citations: {cite_score:2d}/15  ({total_cites} citations)")

    return result


# Example
# result = score_biomarker_readiness("PD-L1", "non-small cell lung cancer")
```

**Key Parameters:**
- Weights: trials (35) + recruiting (20) + PubMed (30) + OpenAlex (15) = 100
- Trial scoring is phase-weighted: Phase 3 = 8 pts, Phase 2 = 4 pts, Phase 1 = 2 pts
- Literature and citation scores are log-scaled to handle well-studied biomarkers

**Expected Output:**
- Composite score (0-100), readiness tier (High/Moderate/Early), component breakdown

---

## Recipe 5: Readiness Tier Classification

Batch-classify multiple biomarkers into readiness tiers for portfolio-level prioritization.

```python
import pandas as pd

def classify_readiness_tiers(biomarker_scores):
    """
    Classify biomarkers into readiness tiers.

    Parameters
    ----------
    biomarker_scores : list of dict
        Each dict has: {"biomarker": str, "score": int}

    Returns
    -------
    DataFrame with tier assignments and priority ranking
    """
    TIER_THRESHOLDS = [
        (70, 100, "HIGH", "Validated — ready for pivotal trial biomarker strategy"),
        (40, 69, "MODERATE", "Emerging — suitable for exploratory endpoint or enrichment"),
        (0, 39, "EARLY", "Discovery-stage — needs analytical and clinical validation"),
    ]

    results = []
    for entry in biomarker_scores:
        score = entry["score"]
        for low, high, tier, description in TIER_THRESHOLDS:
            if low <= score <= high:
                results.append({
                    "biomarker": entry["biomarker"],
                    "score": score,
                    "tier": tier,
                    "description": description,
                    "priority": 1 if tier == "HIGH" else 2 if tier == "MODERATE" else 3,
                })
                break

    df = pd.DataFrame(results).sort_values(["priority", "score"], ascending=[True, False]).reset_index(drop=True)

    print(f"Biomarker Readiness Tiers")
    print(f"{'Biomarker':<20} {'Score':>6} {'Tier':<10} {'Description'}")
    print("-" * 80)
    for _, row in df.iterrows():
        print(f"{row['biomarker']:<20} {row['score']:>6} {row['tier']:<10} {row['description']}")

    return df


# Example
tiers = classify_readiness_tiers([
    {"biomarker": "PD-L1", "score": 85},
    {"biomarker": "TMB", "score": 62},
    {"biomarker": "ctDNA", "score": 55},
    {"biomarker": "Novel_Gene_X", "score": 18},
    {"biomarker": "MSI", "score": 78},
    {"biomarker": "HRD_score", "score": 45},
])
```

**Key Parameters:**
- Tier thresholds: High (>=70), Moderate (40-69), Early (<40)
- Priority ranking: High=1, Moderate=2, Early=3 for portfolio sorting

**Expected Output:**
- Sorted table of biomarkers with tier assignments, descriptions, and priority rankings

---

## Recipe 6: TCGA Expression Stratification

Stratify patients by gene expression level (high/low) using HPA gene FPKM data and assess prognostic associations.

```python
import numpy as np
import pandas as pd

def stratify_by_expression(expression_values, survival_times, events,
                            sample_ids, gene_name, cutoff_method="median"):
    """
    Stratify patients by gene expression and assess prognostic value.

    Parameters
    ----------
    expression_values : array-like
        Gene expression values (FPKM or TPM)
    survival_times : array-like
        Overall survival time (months)
    events : array-like
        Event indicator (1=death, 0=censored)
    sample_ids : list
        Sample identifiers
    gene_name : str
        Gene symbol for display
    cutoff_method : str
        "median", "tertile", or "quartile"

    Returns
    -------
    dict with stratification results and survival statistics
    """
    expr = np.asarray(expression_values, dtype=float)
    time = np.asarray(survival_times, dtype=float)
    event = np.asarray(events, dtype=int)

    # Remove missing
    mask = ~(np.isnan(expr) | np.isnan(time) | np.isnan(event))
    expr, time, event = expr[mask], time[mask], event[mask]

    if cutoff_method == "median":
        cutoff = np.median(expr)
        high = expr >= cutoff
        groups = {"High": high, "Low": ~high}
    elif cutoff_method == "tertile":
        t1, t2 = np.percentile(expr, [33.3, 66.7])
        groups = {
            "High": expr >= t2,
            "Medium": (expr >= t1) & (expr < t2),
            "Low": expr < t1,
        }
    elif cutoff_method == "quartile":
        q1, q2, q3 = np.percentile(expr, [25, 50, 75])
        groups = {
            "Q4 (highest)": expr >= q3,
            "Q3": (expr >= q2) & (expr < q3),
            "Q2": (expr >= q1) & (expr < q2),
            "Q1 (lowest)": expr < q1,
        }

    results = {}
    for name, mask_g in groups.items():
        n = mask_g.sum()
        n_events = event[mask_g].sum()
        median_surv = np.median(time[mask_g][event[mask_g] == 1]) if n_events > 0 else np.nan
        median_expr = np.median(expr[mask_g])

        results[name] = {
            "n_patients": int(n),
            "n_events": int(n_events),
            "event_rate": round(n_events / n, 3) if n > 0 else 0,
            "median_survival_months": round(median_surv, 1) if not np.isnan(median_surv) else "NR",
            "median_expression": round(median_expr, 2),
        }

    # Log-rank test (High vs Low for median split)
    logrank_p = None
    try:
        from lifelines.statistics import logrank_test
        if "High" in groups and "Low" in groups:
            lr = logrank_test(
                time[groups["High"]], time[groups["Low"]],
                event[groups["High"]], event[groups["Low"]],
            )
            logrank_p = lr.p_value
    except ImportError:
        pass

    print(f"\n{gene_name} Expression Stratification ({cutoff_method} split)")
    print(f"{'Group':<15} {'N':>6} {'Events':>8} {'Rate':>8} {'Med. Surv (mo)':>15} {'Med. Expr':>10}")
    print("-" * 65)
    for name, data in results.items():
        print(f"{name:<15} {data['n_patients']:>6} {data['n_events']:>8} "
              f"{data['event_rate']:>8.1%} {str(data['median_survival_months']):>15} "
              f"{data['median_expression']:>10.2f}")
    if logrank_p is not None:
        print(f"\nLog-rank p-value: {logrank_p:.4f}")
        if logrank_p < 0.05:
            print(f"PROGNOSTIC — {gene_name} expression significantly stratifies survival")

    return {"gene": gene_name, "groups": results, "logrank_p": logrank_p}


# Example usage (requires clinical data)
# result = stratify_by_expression(
#     expression_values=fpkm_values,
#     survival_times=os_months,
#     events=os_status,
#     sample_ids=patient_ids,
#     gene_name="EGFR",
# )
```

**Key Parameters:**
- `cutoff_method`: "median" (2 groups), "tertile" (3 groups), or "quartile" (4 groups)
- Survival data from TCGA clinical annotations
- Log-rank test for significance of expression-survival association

**Expected Output:**
- Group-level statistics (N, events, event rate, median survival, median expression), log-rank p-value

---

## Recipe 7: Indication Prioritization Matrix

Score and rank indications for a drug program using multiple criteria.

```python
import pandas as pd
import numpy as np

def prioritize_indications(indications):
    """
    Rank indications by composite priority score.

    Parameters
    ----------
    indications : list of dict
        Each dict has:
        - name: indication name
        - unmet_need: 0-1 (1 = highest unmet need)
        - population_size: estimated addressable patients
        - competitive_landscape: 0-1 (1 = least competition)
        - biomarker_readiness: 0-1 (1 = most ready)
        - preclinical_evidence: 0-1 (1 = strongest evidence)

    Returns
    -------
    DataFrame with composite scores and rankings
    """
    weights = {
        "unmet_need": 0.30,
        "population_size": 0.20,
        "competitive_landscape": 0.20,
        "biomarker_readiness": 0.15,
        "preclinical_evidence": 0.15,
    }

    results = []
    for ind in indications:
        # Normalize population size to 0-1 (log-scaled)
        max_pop = max(i["population_size"] for i in indications)
        pop_norm = np.log10(ind["population_size"] + 1) / np.log10(max_pop + 1)

        scores = {
            "unmet_need": ind["unmet_need"],
            "population_size": pop_norm,
            "competitive_landscape": ind["competitive_landscape"],
            "biomarker_readiness": ind["biomarker_readiness"],
            "preclinical_evidence": ind["preclinical_evidence"],
        }

        composite = sum(scores[k] * weights[k] for k in weights)

        results.append({
            "indication": ind["name"],
            "composite_score": round(composite, 3),
            "addressable_patients": ind["population_size"],
            **{f"score_{k}": round(v, 2) for k, v in scores.items()},
        })

    df = pd.DataFrame(results).sort_values("composite_score", ascending=False).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)

    print(f"Indication Prioritization Matrix")
    print(f"Weights: {', '.join(f'{k}={v:.0%}' for k, v in weights.items())}\n")
    print(df[["rank", "indication", "composite_score", "addressable_patients"]].to_string(index=False))

    return df


# Example
df = prioritize_indications([
    {"name": "NSCLC (EGFR-mut, 2L)", "unmet_need": 0.7, "population_size": 45000,
     "competitive_landscape": 0.3, "biomarker_readiness": 0.9, "preclinical_evidence": 0.8},
    {"name": "Pancreatic (KRAS-mut)", "unmet_need": 0.95, "population_size": 55000,
     "competitive_landscape": 0.8, "biomarker_readiness": 0.6, "preclinical_evidence": 0.5},
    {"name": "AML (FLT3-ITD)", "unmet_need": 0.8, "population_size": 8000,
     "competitive_landscape": 0.5, "biomarker_readiness": 0.85, "preclinical_evidence": 0.7},
    {"name": "Breast (HR+/HER2-)", "unmet_need": 0.5, "population_size": 200000,
     "competitive_landscape": 0.2, "biomarker_readiness": 0.95, "preclinical_evidence": 0.6},
])
```

**Key Parameters:**
- Weights are adjustable (default: unmet need 30%, population 20%, competition 20%, biomarker 15%, preclinical 15%)
- Population size is log-normalized to prevent large indications from dominating
- All input scores are 0-1, with 1 being most favorable

**Expected Output:**
- Ranked indications with composite scores, addressable patient counts, and component scores

---

## Recipe 8: Response Rate Estimation from PRISM/DepMap

Estimate drug response rates by cancer lineage using PRISM drug sensitivity data.

```python
import pandas as pd
import numpy as np

def estimate_response_rate(prism_df, drug_name, lineage_col="lineage",
                            sensitive_threshold=-0.5):
    """
    Estimate response rates by cancer lineage from PRISM drug screen data.

    Parameters
    ----------
    prism_df : DataFrame
        PRISM secondary screen data. Rows = cell lines with metadata.
        Must have columns: lineage_col, and drug_name (LFC values).
    drug_name : str
        Drug/compound column name in PRISM data
    lineage_col : str
        Column with cancer lineage labels
    sensitive_threshold : float
        LFC threshold for sensitivity (default: -0.5 = >30% growth inhibition)

    Returns
    -------
    DataFrame with response rate per lineage
    """
    if drug_name not in prism_df.columns:
        raise ValueError(f"Drug '{drug_name}' not found in data")

    data = prism_df[[lineage_col, drug_name]].dropna()

    results = []
    for lineage, group in data.groupby(lineage_col):
        n_total = len(group)
        if n_total < 3:
            continue

        n_sensitive = (group[drug_name] < sensitive_threshold).sum()
        response_rate = n_sensitive / n_total
        median_lfc = group[drug_name].median()

        results.append({
            "lineage": lineage,
            "n_cell_lines": n_total,
            "n_sensitive": int(n_sensitive),
            "response_rate": round(response_rate, 3),
            "median_LFC": round(median_lfc, 4),
            "classification": (
                "HIGHLY SENSITIVE" if response_rate >= 0.5
                else "MODERATELY SENSITIVE" if response_rate >= 0.2
                else "RESISTANT"
            ),
        })

    results_df = pd.DataFrame(results).sort_values("response_rate", ascending=False).reset_index(drop=True)

    print(f"Response Rate by Lineage: {drug_name}")
    print(f"Sensitivity threshold: LFC < {sensitive_threshold}\n")
    print(results_df.to_string(index=False))

    return results_df


# Example usage (requires PRISM data from depmap.org)
# prism = pd.read_csv("secondary-screen-dose-response-curve-parameters.csv")
# results = estimate_response_rate(prism, "BRD-K12345678-001-01-1")
```

**Key Parameters:**
- `sensitive_threshold=-0.5`: LFC below this indicates drug sensitivity (>30% growth inhibition)
- Groups by cancer lineage for indication-specific response estimates
- Classification: HIGHLY SENSITIVE (>=50%), MODERATELY SENSITIVE (>=20%), RESISTANT (<20%)

**Expected Output:**
- Per-lineage response rates, sensitivity classification, median LFC values

---

## Recipe 9: Trial Endpoint Benchmarking

Benchmark trial endpoints (OS, PFS, ORR, DOR) across similar trials by phase.

```python
import pandas as pd
import numpy as np

def benchmark_endpoints(trials_data):
    """
    Benchmark clinical trial endpoints across similar trials.

    Parameters
    ----------
    trials_data : list of dict
        Each dict has:
        - nct_id: trial NCT ID
        - phase: trial phase (1, 2, 3)
        - drug: drug name
        - indication: disease/indication
        - os_months: median OS (or None)
        - pfs_months: median PFS (or None)
        - orr_pct: ORR percentage (or None)
        - dor_months: median DOR (or None)

    Returns
    -------
    dict with endpoint summaries by phase
    """
    df = pd.DataFrame(trials_data)

    endpoint_cols = ["os_months", "pfs_months", "orr_pct", "dor_months"]
    endpoint_labels = {
        "os_months": "Overall Survival (months)",
        "pfs_months": "Progression-Free Survival (months)",
        "orr_pct": "Objective Response Rate (%)",
        "dor_months": "Duration of Response (months)",
    }

    results = {}
    for phase in sorted(df["phase"].unique()):
        phase_df = df[df["phase"] == phase]
        phase_results = {"n_trials": len(phase_df)}

        for col in endpoint_cols:
            values = phase_df[col].dropna()
            if len(values) >= 2:
                phase_results[endpoint_labels[col]] = {
                    "n_reported": len(values),
                    "median": round(values.median(), 1),
                    "mean": round(values.mean(), 1),
                    "range": f"{values.min():.1f}-{values.max():.1f}",
                    "p25": round(values.quantile(0.25), 1),
                    "p75": round(values.quantile(0.75), 1),
                }

        results[f"Phase {phase}"] = phase_results

    print(f"Endpoint Benchmarks Across Similar Trials")
    print(f"Total trials: {len(df)}\n")
    for phase, data in results.items():
        print(f"\n{phase} (n={data['n_trials']} trials)")
        print("-" * 70)
        for endpoint, stats in data.items():
            if endpoint == "n_trials":
                continue
            print(f"  {endpoint}")
            print(f"    Median: {stats['median']}  (range: {stats['range']}, IQR: {stats['p25']}-{stats['p75']})")
            print(f"    Reported in {stats['n_reported']}/{data['n_trials']} trials")

    return results


# Example: benchmark EGFR TKI trials in NSCLC
results = benchmark_endpoints([
    {"nct_id": "NCT01234567", "phase": 3, "drug": "Drug A", "indication": "NSCLC",
     "os_months": 28.5, "pfs_months": 12.3, "orr_pct": 62, "dor_months": 11.1},
    {"nct_id": "NCT02345678", "phase": 3, "drug": "Drug B", "indication": "NSCLC",
     "os_months": 31.2, "pfs_months": 14.7, "orr_pct": 71, "dor_months": 13.5},
    {"nct_id": "NCT03456789", "phase": 2, "drug": "Drug C", "indication": "NSCLC",
     "os_months": None, "pfs_months": 10.1, "orr_pct": 55, "dor_months": 8.2},
    {"nct_id": "NCT04567890", "phase": 2, "drug": "Drug D", "indication": "NSCLC",
     "os_months": None, "pfs_months": 11.8, "orr_pct": 58, "dor_months": 9.7},
])
```

**Key Parameters:**
- Input trials data manually curated from ClinicalTrials.gov results and publications
- Reports median, range, and IQR for each endpoint by trial phase
- Use to set realistic endpoint targets for new trial design

**Expected Output:**
- Endpoint benchmarks (median, range, IQR) stratified by trial phase

---

## Recipe 10: Competitive Positioning

Map competitive landscape using ClinicalTrials.gov active trials, ChEMBL pipeline, and Open Targets drug evidence.

```python
import requests
import pandas as pd

def map_competitive_landscape(condition, intervention_class=None):
    """
    Map competitive landscape for an indication from ClinicalTrials.gov.

    Parameters
    ----------
    condition : str
        Disease/condition to search
    intervention_class : str, optional
        Drug class filter (e.g., "PROTAC", "checkpoint inhibitor")

    Returns
    -------
    dict with competitive landscape summary
    """
    base_url = "https://clinicaltrials.gov/api/v2/studies"

    # Search active trials
    params = {
        "query.cond": condition,
        "filter.overallStatus": "RECRUITING,ACTIVE_NOT_RECRUITING,ENROLLING_BY_INVITATION",
        "pageSize": 100,
        "format": "json",
    }
    if intervention_class:
        params["query.intr"] = intervention_class

    try:
        resp = requests.get(base_url, params=params, timeout=15)
        data = resp.json()
        studies = data.get("studies", [])
        total_active = data.get("totalCount", 0)
    except Exception:
        studies = []
        total_active = 0

    # Parse trials by phase
    phase_map = {}
    sponsors = {}
    for study in studies:
        protocol = study.get("protocolSection", {})
        design = protocol.get("designModule", {})
        sponsor = protocol.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", "Unknown")
        nct_id = protocol.get("identificationModule", {}).get("nctId", "")
        title = protocol.get("identificationModule", {}).get("briefTitle", "")
        phases = design.get("phases", ["N/A"])

        for phase in phases:
            if phase not in phase_map:
                phase_map[phase] = []
            phase_map[phase].append({
                "nct_id": nct_id,
                "sponsor": sponsor,
                "title": title[:80],
            })

        sponsors[sponsor] = sponsors.get(sponsor, 0) + 1

    # Top sponsors
    top_sponsors = sorted(sponsors.items(), key=lambda x: -x[1])[:10]

    print(f"Competitive Landscape: {condition}")
    if intervention_class:
        print(f"Filtered by: {intervention_class}")
    print(f"Total active trials: {total_active}\n")

    print(f"By Phase:")
    for phase in ["PHASE3", "PHASE2", "PHASE1", "EARLY_PHASE1", "N/A"]:
        if phase in phase_map:
            print(f"  {phase}: {len(phase_map[phase])} trials")

    print(f"\nTop Sponsors:")
    for sponsor, count in top_sponsors[:5]:
        print(f"  {sponsor}: {count} trials")

    if "PHASE3" in phase_map:
        print(f"\nPhase 3 Trials:")
        for trial in phase_map["PHASE3"][:10]:
            print(f"  {trial['nct_id']}: {trial['title']} ({trial['sponsor']})")

    return {
        "condition": condition,
        "total_active_trials": total_active,
        "by_phase": {p: len(t) for p, t in phase_map.items()},
        "top_sponsors": dict(top_sponsors),
        "phase3_trials": phase_map.get("PHASE3", []),
    }


# Example
# result = map_competitive_landscape("non-small cell lung cancer", "EGFR")
```

**Key Parameters:**
- Searches ClinicalTrials.gov for active/recruiting trials in the indication
- Optional `intervention_class` filter for specific drug types
- Reports phase distribution and top sponsors

**Expected Output:**
- Active trial count by phase, top sponsors, Phase 3 trial details

---

## Recipe 11: Market Sizing

Estimate peak revenue potential for a drug program.

```python
import pandas as pd

def estimate_market_size(
    addressable_patients,
    treatment_duration_months,
    price_per_cycle,
    cycle_length_days=28,
    market_share,
    peak_year=5,
    ramp_years=3,
):
    """
    Estimate peak annual revenue for a drug program.

    Parameters
    ----------
    addressable_patients : int
        Annual addressable patient pool
    treatment_duration_months : float
        Average treatment duration in months
    price_per_cycle : float
        Price per treatment cycle (USD)
    cycle_length_days : int
        Days per cycle (default: 28)
    market_share : float
        Expected peak market share (0-1)
    peak_year : int
        Year of peak sales post-launch
    ramp_years : int
        Years to reach peak market share

    Returns
    -------
    dict with revenue estimates and ramp projection
    """
    cycles_per_patient = treatment_duration_months / (cycle_length_days / 30.44)
    revenue_per_patient = cycles_per_patient * price_per_cycle

    peak_patients = int(addressable_patients * market_share)
    peak_revenue = peak_patients * revenue_per_patient

    # Revenue ramp
    ramp = []
    for year in range(1, peak_year + 2):
        if year <= ramp_years:
            share = market_share * (year / ramp_years)
        else:
            share = market_share
        patients = int(addressable_patients * share)
        revenue = patients * revenue_per_patient
        ramp.append({
            "year": year,
            "market_share": round(share, 3),
            "treated_patients": patients,
            "annual_revenue_usd": round(revenue, 0),
        })

    print(f"Market Size Estimate")
    print(f"Addressable patients: {addressable_patients:,}")
    print(f"Treatment: {treatment_duration_months} months @ ${price_per_cycle:,.0f}/cycle ({cycle_length_days}d)")
    print(f"Revenue per patient: ${revenue_per_patient:,.0f}")
    print(f"Peak market share: {market_share:.0%}\n")
    print(f"{'Year':<6} {'Share':>8} {'Patients':>10} {'Revenue (M$)':>14}")
    print("-" * 40)
    for r in ramp:
        print(f"{r['year']:<6} {r['market_share']:>8.1%} {r['treated_patients']:>10,} "
              f"{r['annual_revenue_usd']/1e6:>14,.1f}")

    print(f"\nPeak annual revenue: ${peak_revenue/1e6:,.1f}M (Year {peak_year})")

    return {
        "addressable_patients": addressable_patients,
        "revenue_per_patient": round(revenue_per_patient, 0),
        "peak_patients": peak_patients,
        "peak_revenue_usd": round(peak_revenue, 0),
        "peak_revenue_M": round(peak_revenue / 1e6, 1),
        "ramp": ramp,
    }


# Example: oncology drug
result = estimate_market_size(
    addressable_patients=25_000,
    treatment_duration_months=8,
    price_per_cycle=15_000,
    cycle_length_days=21,
    market_share=0.20,
    peak_year=5,
    ramp_years=3,
)
```

**Key Parameters:**
- `price_per_cycle`: WAC or net price per treatment cycle
- `treatment_duration_months`: Average time on therapy (from trial data or analogues)
- `market_share`: Realistic peak share (consider competitive landscape)
- Revenue ramp assumes linear growth over `ramp_years`

**Expected Output:**
- Revenue per patient, peak annual revenue, year-by-year ramp projection

---

## Recipe 12: Subtype Stratification with Incidence Rates

Break down disease incidence by molecular subtypes with prevalence data.

```python
import pandas as pd

def stratify_subtypes(disease_name, total_incidence, subtypes):
    """
    Stratify disease incidence by molecular subtypes.

    Parameters
    ----------
    disease_name : str
        Disease name
    total_incidence : int
        Total annual incidence (regional or global)
    subtypes : list of dict
        Each dict has:
        - name: subtype name (e.g., "HR+/HER2-")
        - fraction: prevalence fraction (0-1)
        - standard_of_care: current SOC
        - unmet_need: qualitative assessment

    Returns
    -------
    DataFrame with subtype breakdown
    """
    results = []
    total_fraction = 0

    for sub in subtypes:
        incidence = int(total_incidence * sub["fraction"])
        total_fraction += sub["fraction"]

        results.append({
            "subtype": sub["name"],
            "fraction": sub["fraction"],
            "annual_incidence": incidence,
            "standard_of_care": sub.get("standard_of_care", "N/A"),
            "unmet_need": sub.get("unmet_need", "N/A"),
        })

    # Check fractions sum to ~1
    if abs(total_fraction - 1.0) > 0.05:
        results.append({
            "subtype": "Other/unclassified",
            "fraction": round(1.0 - total_fraction, 3),
            "annual_incidence": int(total_incidence * (1.0 - total_fraction)),
            "standard_of_care": "Variable",
            "unmet_need": "Variable",
        })

    df = pd.DataFrame(results)

    print(f"Molecular Subtype Stratification: {disease_name}")
    print(f"Total annual incidence: {total_incidence:,}\n")
    print(f"{'Subtype':<25} {'Fraction':>10} {'Incidence':>12} {'Unmet Need':<15}")
    print("-" * 65)
    for _, row in df.iterrows():
        print(f"{row['subtype']:<25} {row['fraction']:>10.1%} {row['annual_incidence']:>12,} {row['unmet_need']:<15}")

    return df


# Example: breast cancer molecular subtypes
df = stratify_subtypes(
    disease_name="Breast Cancer (US)",
    total_incidence=310_720,
    subtypes=[
        {"name": "HR+/HER2-", "fraction": 0.68, "standard_of_care": "CDK4/6i + ET",
         "unmet_need": "Moderate — CDK4/6i resistance"},
        {"name": "HER2+", "fraction": 0.15, "standard_of_care": "Trastuzumab + chemo",
         "unmet_need": "Low-Moderate — ADC options expanding"},
        {"name": "Triple-negative (TNBC)", "fraction": 0.12, "standard_of_care": "Chemo +/- IO",
         "unmet_need": "HIGH — limited targeted options"},
        {"name": "HR+/HER2-low", "fraction": 0.05, "standard_of_care": "T-DXd emerging",
         "unmet_need": "Moderate — new ADC category"},
    ],
)
```

**Key Parameters:**
- `total_incidence`: From cancer registries (SEER, GLOBOCAN)
- `subtypes`: Molecular subtype prevalence from TCGA, clinical cohort studies, or NCCN guidelines
- Automatically detects if fractions don't sum to 1.0 and adds "Other" category

**Expected Output:**
- Subtype-level incidence breakdown with SOC and unmet need assessment
