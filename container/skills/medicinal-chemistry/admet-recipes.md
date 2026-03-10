# ADMET Prediction & Toxicity Scoring Pipeline Recipes

Executable code templates for ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity) prediction, structural alert filtering, toxicity scoring, and composite drug candidate ranking.

> **Parent skill**: [SKILL.md](SKILL.md) -- full medicinal chemistry pipeline with MCP tools.
> **See also**: [ml-recipes.md](ml-recipes.md) -- ML model training (DeepChem, ChemBERTa, GROVER, multi-task learning). Recipe 11 in ml-recipes.md provides a basic rule-based ADMET function; the recipes here are more comprehensive and production-focused.
> **See also**: [recipes.md](recipes.md) -- RDKit basics (Lipinski, fingerprints, conformers, scaffolds, PAINS filter in Recipe 10).

---

## 1. Structured ADMET Prediction Pipeline: Absorption -> Distribution -> Metabolism -> Excretion -> Toxicity

Full five-stage ADMET assessment using RDKit descriptors, empirical rules, and classification models.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski, rdMolDescriptors
import pandas as pd
import numpy as np

def full_admet_pipeline(smiles_list, names=None):
    """Run structured ADMET prediction across all five stages.

    Parameters
    ----------
    smiles_list : list of str
        SMILES strings for compounds to evaluate.
    names : list of str or None
        Compound names (optional).

    Returns
    -------
    pd.DataFrame with ADMET predictions for each compound.
    """
    if names is None:
        names = [f"Compound_{i+1}" for i in range(len(smiles_list))]

    results = []

    for smi, name in zip(smiles_list, names):
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            results.append({'name': name, 'smiles': smi, 'valid': False})
            continue

        # Core descriptors
        mw = Descriptors.MolWt(mol)
        logp = Crippen.MolLogP(mol)
        tpsa = Descriptors.TPSA(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        rot_bonds = Descriptors.NumRotatableBonds(mol)
        aromatic_rings = Descriptors.NumAromaticRings(mol)
        heavy_atoms = Descriptors.HeavyAtomCount(mol)
        fsp3 = rdMolDescriptors.CalcFractionCSP3(mol)
        n_rings = Descriptors.RingCount(mol)

        r = {'name': name, 'smiles': smi, 'valid': True,
             'MW': round(mw, 1), 'LogP': round(logp, 2), 'TPSA': round(tpsa, 1),
             'HBD': hbd, 'HBA': hba, 'RotBonds': rot_bonds, 'Fsp3': round(fsp3, 2)}

        # ---- STAGE 1: ABSORPTION ----
        # Lipinski Rule of Five
        lipinski_v = sum([mw > 500, logp > 5, hbd > 5, hba > 10])
        r['lipinski_violations'] = lipinski_v
        r['lipinski_pass'] = lipinski_v <= 1

        # Veber oral bioavailability
        r['veber_pass'] = tpsa <= 140 and rot_bonds <= 10

        # Egan egg model (absorption prediction)
        if tpsa <= 131.6 and logp <= 5.88:
            r['absorption'] = 'HIGH'
        elif tpsa <= 150:
            r['absorption'] = 'MODERATE'
        else:
            r['absorption'] = 'LOW'

        # Caco-2 permeability estimate (TPSA-based)
        # Log Papp ~ -0.011 * TPSA + 0.3 (simplified Hou et al. model)
        log_papp = -0.011 * tpsa + 0.3
        r['caco2_log_papp'] = round(log_papp, 2)
        r['caco2_class'] = 'HIGH' if log_papp > -5.15 else 'LOW'

        # ---- STAGE 2: DISTRIBUTION ----
        # Blood-brain barrier (Clark rules)
        if tpsa <= 60 and logp >= 1.0 and mw <= 450:
            r['bbb'] = 'HIGH'
        elif tpsa <= 90 and logp >= 0:
            r['bbb'] = 'MODERATE'
        else:
            r['bbb'] = 'LOW'

        # Plasma protein binding (PPB) risk
        r['ppb_risk'] = 'HIGH' if logp > 4 else 'MODERATE' if logp > 2.5 else 'LOW'

        # Volume of distribution estimate
        # Vd tends to increase with LogP and decrease with PPB
        r['vd_class'] = 'HIGH' if logp > 3 and tpsa < 80 else 'LOW'

        # P-glycoprotein substrate likelihood
        r['pgp_substrate_risk'] = 'HIGH' if mw > 400 and hbd > 2 and tpsa > 75 else 'LOW'

        # ---- STAGE 3: METABOLISM ----
        # CYP3A4 substrate risk (major metabolic enzyme)
        r['cyp3a4_risk'] = 'HIGH' if (logp > 3 and aromatic_rings >= 2 and mw > 300) \
                           else 'MODERATE' if logp > 2 else 'LOW'

        # CYP2D6 substrate risk (basic nitrogen + lipophilic)
        basic_n = sum(1 for atom in mol.GetAtoms()
                      if atom.GetAtomicNum() == 7 and atom.GetFormalCharge() >= 0
                      and atom.GetTotalNumHs() > 0)
        r['cyp2d6_risk'] = 'HIGH' if (logp > 2 and basic_n > 0 and mw < 500) \
                           else 'MODERATE' if basic_n > 0 else 'LOW'

        # CYP2C9 substrate risk (acidic, lipophilic)
        acidic = sum(1 for atom in mol.GetAtoms()
                     if atom.GetAtomicNum() == 8 and atom.GetFormalCharge() <= 0)
        r['cyp2c9_risk'] = 'HIGH' if (logp > 2 and acidic > 2 and mw > 300) else 'LOW'

        # Metabolic stability estimate (rule-based)
        if logp > 4 or aromatic_rings >= 3:
            r['metabolic_stability'] = 'LOW (rapid metabolism expected)'
        elif logp < 0 and tpsa > 120:
            r['metabolic_stability'] = 'HIGH (but poor absorption)'
        else:
            r['metabolic_stability'] = 'MODERATE'

        # ---- STAGE 4: EXCRETION ----
        # Renal clearance
        r['renal_clearance'] = 'LIKELY' if (mw < 400 and logp < 1 and tpsa > 40) else 'UNLIKELY'

        # Half-life estimate category
        if logp > 4 and mw > 500:
            r['halflife_class'] = 'LONG (high PPB, slow metabolism)'
        elif logp < 1 and mw < 300:
            r['halflife_class'] = 'SHORT (rapid renal clearance)'
        else:
            r['halflife_class'] = 'MODERATE'

        # ---- STAGE 5: TOXICITY ----
        # hERG risk
        r['herg_risk'] = 'HIGH' if (logp > 3.7 and basic_n > 0) \
                         else 'MODERATE' if logp > 3 else 'LOW'

        # Ames mutagenicity structural alert flags
        ames_alerts = 0
        ames_patterns = {
            'aromatic_amine': '[NH2]c1ccccc1',
            'nitro_aromatic': '[N+](=O)[O-]c1ccccc1',
            'epoxide': 'C1OC1',
            'aziridine': 'C1NC1',
            'hydrazine': 'NN',
            'alkyl_halide': '[CX4][F,Cl,Br,I]',
        }
        triggered_alerts = []
        for alert_name, smarts in ames_patterns.items():
            pat = Chem.MolFromSmarts(smarts)
            if pat and mol.HasSubstructMatch(pat):
                ames_alerts += 1
                triggered_alerts.append(alert_name)
        r['ames_alerts'] = ames_alerts
        r['ames_alert_names'] = ','.join(triggered_alerts) if triggered_alerts else 'none'
        r['ames_risk'] = 'HIGH' if ames_alerts >= 2 else 'MODERATE' if ames_alerts == 1 else 'LOW'

        results.append(r)

    df = pd.DataFrame(results)

    # Summary
    print(f"ADMET Pipeline Results ({len(df)} compounds)")
    print("=" * 80)
    for _, row in df[df['valid'] == True].iterrows():
        print(f"\n{row['name']} ({row['smiles'][:40]}...)" if len(row['smiles']) > 40 else f"\n{row['name']} ({row['smiles']})")
        print(f"  Physicochemical: MW={row['MW']}  LogP={row['LogP']}  TPSA={row['TPSA']}  HBD={row['HBD']}  HBA={row['HBA']}")
        print(f"  ABSORPTION:  Lipinski={'PASS' if row['lipinski_pass'] else 'FAIL'}  Veber={'PASS' if row['veber_pass'] else 'FAIL'}  Oral={row['absorption']}")
        print(f"  DISTRIBUTION: BBB={row['bbb']}  PPB={row['ppb_risk']}  P-gp={row['pgp_substrate_risk']}")
        print(f"  METABOLISM:  CYP3A4={row['cyp3a4_risk']}  CYP2D6={row['cyp2d6_risk']}  Stability={row['metabolic_stability']}")
        print(f"  EXCRETION:   Renal={row['renal_clearance']}  Half-life={row['halflife_class']}")
        print(f"  TOXICITY:    hERG={row['herg_risk']}  Ames={row['ames_risk']} ({row['ames_alert_names']})")

    df.to_csv("admet_pipeline_results.csv", index=False)
    return df

# Example usage
compounds = [
    "CC(=O)Oc1ccccc1C(=O)O",                  # Aspirin
    "CC(C)Cc1ccc(CC(C)C(=O)O)cc1",            # Ibuprofen
    "CN1C(=O)N(C)c2[nH]cnc2C1=O",             # Caffeine
    "c1ccc(NC(=O)c2cc(Cl)ccc2F)cc1",          # Test compound
]
result = full_admet_pipeline(compounds, names=["Aspirin", "Ibuprofen", "Caffeine", "Test_Cpd"])
```

**Key parameters**: Five-stage pipeline: Absorption (Lipinski, Veber, Egan, Caco-2), Distribution (BBB, PPB, Vd, P-gp), Metabolism (CYP3A4/2D6/2C9, stability), Excretion (renal, half-life), Toxicity (hERG, Ames alerts). Each stage classifies risk as LOW/MODERATE/HIGH.

**Expected output**: Per-compound ADMET profile across all five stages with risk classifications and structural alert flags. CSV file for batch analysis.

---

## 2. pkCSM / admetSAR Web API Queries for ADMET Prediction

Query external ADMET prediction services programmatically for validated ML-based predictions.

```python
import requests
import pandas as pd
import time

def query_pkcsm(smiles, properties=None):
    """Query pkCSM web service for ADMET predictions.

    pkCSM (http://biosig.unimelb.edu.au/pkcsm/) provides graph-based
    ADMET predictions using cutoff scanning matrices.

    Parameters
    ----------
    smiles : str
        SMILES string.
    properties : list of str or None
        Specific properties to predict. None = all available.

    Returns
    -------
    dict with pkCSM predictions.
    """
    # pkCSM API endpoint (check current URL as it may change)
    url = "http://biosig.unimelb.edu.au/pkcsm/prediction"

    # Available pkCSM endpoints
    endpoints = {
        'absorption': ['caco2_permeability', 'intestinal_absorption', 'skin_permeability',
                       'pgp_substrate', 'pgp_inhibitor_I', 'pgp_inhibitor_II'],
        'distribution': ['vdss', 'fraction_unbound', 'bbb_permeability', 'cns_permeability'],
        'metabolism': ['cyp2d6_substrate', 'cyp3a4_substrate', 'cyp1a2_inhibitor',
                       'cyp2c19_inhibitor', 'cyp2c9_inhibitor', 'cyp2d6_inhibitor',
                       'cyp3a4_inhibitor'],
        'excretion': ['total_clearance', 'renal_oct2_substrate'],
        'toxicity': ['ames_toxicity', 'max_tolerated_dose', 'herg_inhibitor_I',
                     'herg_inhibitor_II', 'oral_rat_acute_toxicity_ld50',
                     'oral_rat_chronic_toxicity_loael', 'hepatotoxicity',
                     'skin_sensitisation', 'tetrahymena_pyriformis_toxicity',
                     'minnow_toxicity'],
    }

    print(f"pkCSM ADMET predictions for: {smiles}")
    print(f"\nAvailable prediction categories:")
    for category, props in endpoints.items():
        print(f"  {category.upper()}: {', '.join(props)}")

    # Note: pkCSM requires web form submission or API access
    # The following is a template for programmatic access
    print(f"\nTo query pkCSM programmatically:")
    print(f"  1. Visit http://biosig.unimelb.edu.au/pkcsm/prediction")
    print(f"  2. Enter SMILES: {smiles}")
    print(f"  3. Submit and parse HTML results")
    print(f"  OR use the pkCSM Python client if available")

    # Template for parsing results
    result = {
        'smiles': smiles,
        'source': 'pkCSM',
        'note': 'Submit SMILES to web interface or use API client',
    }

    return result

def query_admetsar(smiles):
    """Query admetSAR 2.0 for ADMET predictions.

    admetSAR (http://lmmd.ecust.edu.cn/admetsar2/) provides structure-activity
    relationship-based ADMET predictions.

    Parameters
    ----------
    smiles : str
        SMILES string.

    Returns
    -------
    dict with admetSAR predictions.
    """
    # admetSAR 2.0 endpoints
    properties = {
        'absorption': ['HIA', 'Caco2', 'Pgp_substrate', 'Pgp_inhibitor'],
        'distribution': ['BBB', 'PPB', 'Vd'],
        'metabolism': ['CYP1A2_inhibitor', 'CYP2C19_inhibitor', 'CYP2C9_inhibitor',
                       'CYP2D6_inhibitor', 'CYP3A4_inhibitor', 'CYP2D6_substrate',
                       'CYP3A4_substrate'],
        'excretion': ['clearance', 'half_life'],
        'toxicity': ['Ames', 'hERG', 'DILI', 'carcinogenicity', 'eye_corrosion',
                     'eye_irritation', 'respiratory_toxicity'],
    }

    print(f"admetSAR 2.0 predictions for: {smiles}")
    print(f"\nSubmit to: http://lmmd.ecust.edu.cn/admetsar2/")
    print(f"Available predictions:")
    for category, props in properties.items():
        print(f"  {category.upper()}: {', '.join(props)}")

    return {'smiles': smiles, 'source': 'admetSAR2'}

# Example
query_pkcsm("CC(=O)Oc1ccccc1C(=O)O")  # Aspirin
query_admetsar("CC(C)Cc1ccc(CC(C)C(=O)O)cc1")  # Ibuprofen
```

**Key parameters**: pkCSM uses graph-based signatures for predictions; admetSAR uses QSAR models. Both accept SMILES input. For batch processing, consider the ADMETlab 2.0 batch submission (Recipe 3).

**Expected output**: List of available ADMET prediction endpoints with submission instructions. For automated pipelines, parse HTML responses or use API clients when available.

---

## 3. ADMETlab 2.0: Batch SMILES Submission and Result Parsing

Submit batches of compounds to ADMETlab 2.0 and parse comprehensive ADMET results.

```python
import requests
import pandas as pd
import json
import time

def submit_admetlab2(smiles_list, names=None, output_file="admetlab2_results.csv"):
    """Submit SMILES batch to ADMETlab 2.0 and parse results.

    ADMETlab 2.0 (https://admetmesh.scbdd.com/) provides 77 ADMET endpoints
    covering physicochemical, absorption, distribution, metabolism, excretion,
    toxicity, and druglikeness properties.

    Parameters
    ----------
    smiles_list : list of str
        SMILES strings (max 100 per batch for web API).
    names : list of str or None
        Compound identifiers.
    output_file : str
        Output CSV file path.

    Returns
    -------
    pd.DataFrame with ADMETlab 2.0 predictions.
    """
    if names is None:
        names = [f"mol_{i}" for i in range(len(smiles_list))]

    # ADMETlab 2.0 API endpoint
    api_url = "https://admetmesh.scbdd.com/service/screening/cal"

    print(f"ADMETlab 2.0 Batch Submission")
    print(f"  Compounds: {len(smiles_list)}")
    print(f"  API: {api_url}")

    # Prepare payload
    smiles_text = "\n".join([f"{name}\t{smi}" for name, smi in zip(names, smiles_list)])

    try:
        response = requests.post(
            api_url,
            data={"smiles": smiles_text},
            timeout=120,
        )

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False)
            print(f"  Results saved to {output_file}")
            print(f"  Columns: {list(df.columns)[:10]}...")
            return df
        else:
            print(f"  API returned status {response.status_code}")
            print(f"  Falling back to manual submission instructions")
    except Exception as e:
        print(f"  API request failed: {e}")
        print(f"  Falling back to manual submission instructions")

    # Manual submission fallback
    print(f"\nManual ADMETlab 2.0 submission:")
    print(f"  1. Visit https://admetmesh.scbdd.com/service/screening/index")
    print(f"  2. Upload SMILES file (one SMILES per line, or name\\tSMILES)")
    print(f"  3. Select prediction endpoints (default: all 77)")
    print(f"  4. Download results as CSV")
    print(f"\n  Key ADMETlab 2.0 predictions (77 endpoints):")
    print(f"    Physicochemical: MW, LogP, LogD, LogS, pKa")
    print(f"    Absorption: Caco-2, MDCK, HIA, F(20%), F(30%), Pgp-sub, Pgp-inh")
    print(f"    Distribution: PPB, VDss, BBB, Fu")
    print(f"    Metabolism: CYP1A2/2C9/2C19/2D6/3A4 substrate + inhibitor")
    print(f"    Excretion: CL, T1/2")
    print(f"    Toxicity: hERG, AMES, DILI, LD50, Carcinogenicity, Skin sensitization")
    print(f"    Druglikeness: Lipinski, Ghose, Veber, Egan, Muegge, PAINS, Brenk")

    # Create SMILES file for upload
    with open("admetlab2_input.txt", 'w') as f:
        for name, smi in zip(names, smiles_list):
            f.write(f"{name}\t{smi}\n")
    print(f"\n  Input file saved: admetlab2_input.txt")

    return None

# Example
smiles = [
    "CC(=O)Oc1ccccc1C(=O)O",
    "CC(C)Cc1ccc(CC(C)C(=O)O)cc1",
    "CN1C(=O)N(C)c2[nH]cnc2C1=O",
]
submit_admetlab2(smiles, names=["Aspirin", "Ibuprofen", "Caffeine"])
```

**Key parameters**: ADMETlab 2.0 provides 77 ADMET endpoints in a single submission. Max 100 compounds per batch via API. Predictions include both classification (pass/fail) and regression (continuous values) endpoints.

**Expected output**: CSV file with 77 ADMET predictions per compound, covering all stages from physicochemical to toxicity and druglikeness filters.

---

## 4. Hepatotoxicity Prediction: DILIst Database Cross-Reference and Structural Alerts

Assess drug-induced liver injury (DILI) risk using structural alerts and database cross-reference.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen
import pandas as pd

def predict_hepatotoxicity(smiles, compound_name="compound"):
    """Predict hepatotoxicity risk using structural alerts and physicochemical properties.

    Cross-references known DILI-associated structural motifs from DILIst database.

    Parameters
    ----------
    smiles : str
        SMILES string.
    compound_name : str
        Compound identifier.

    Returns
    -------
    dict with hepatotoxicity risk assessment.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {'compound': compound_name, 'valid': False}

    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)

    # DILI-associated structural alerts
    dili_alerts = {
        'quinone': '[#6]1=[#6][#6](=[O])[#6]=[#6][#6]1=[O]',
        'hydrazine': 'NN',
        'acyl_halide': 'C(=O)[F,Cl,Br,I]',
        'michael_acceptor': '[#6]=[#6]-[#6]=[O]',
        'nitroaromatic': '[N+](=O)[O-]c',
        'thiourea': 'NC(=S)N',
        'epoxide': 'C1OC1',
        'acyl_glucuronide_risk': 'C(=O)O',  # Carboxylic acids form reactive glucuronides
        'hydroxamic_acid': 'C(=O)NO',
        'sulfonamide': 'S(=O)(=O)N',
        'nitro_aromatic': '[$(c[N+](=O)[O-])]',
        'aniline': 'c1ccccc1N',
        'thiol': '[SH]',
    }

    triggered = []
    for name, smarts in dili_alerts.items():
        pat = Chem.MolFromSmarts(smarts)
        if pat and mol.HasSubstructMatch(pat):
            matches = len(mol.GetSubstructMatches(pat))
            triggered.append({'alert': name, 'count': matches})

    # Lipophilicity-dependent DILI risk (daily dose * LogP)
    # High daily dose + high LogP correlates with DILI (Chen et al. 2013)
    lipophilic_risk = 'HIGH' if logp > 3 else 'MODERATE' if logp > 1 else 'LOW'

    # Reactive metabolite risk (based on structural features)
    reactive_met = sum(1 for t in triggered if t['alert'] in
                       ['quinone', 'michael_acceptor', 'epoxide', 'aniline', 'thiol'])

    # Overall DILI risk score
    n_alerts = len(triggered)
    if n_alerts >= 3 or reactive_met >= 2:
        dili_risk = 'HIGH'
    elif n_alerts >= 1 or (logp > 3 and mw > 400):
        dili_risk = 'MODERATE'
    else:
        dili_risk = 'LOW'

    result = {
        'compound': compound_name,
        'smiles': smiles,
        'MW': round(mw, 1),
        'LogP': round(logp, 2),
        'n_structural_alerts': n_alerts,
        'alerts': triggered,
        'lipophilic_risk': lipophilic_risk,
        'reactive_metabolite_risk': reactive_met,
        'dili_risk': dili_risk,
    }

    print(f"Hepatotoxicity Assessment: {compound_name}")
    print(f"  SMILES: {smiles}")
    print(f"  MW={mw:.1f}  LogP={logp:.2f}")
    print(f"  Structural alerts: {n_alerts}")
    for t in triggered:
        print(f"    - {t['alert']} (x{t['count']})")
    print(f"  Lipophilic risk: {lipophilic_risk}")
    print(f"  Reactive metabolite risk: {reactive_met} alert(s)")
    print(f"  Overall DILI risk: {dili_risk}")
    print(f"\n  DILIst cross-reference:")
    print(f"    Search compound at: https://www.ncbi.nlm.nih.gov/books/NBK547852/")
    print(f"    DILIrank database: https://www.fda.gov/science-research/liver-toxicity-knowledge-base-ltkb")

    return result

# Example
predict_hepatotoxicity("CC(=O)Nc1ccc(O)cc1", "Acetaminophen")
predict_hepatotoxicity("c1ccc(NC(=O)c2ccccc2Cl)cc1", "Test_compound")
```

**Key parameters**: DILI alerts include quinones, Michael acceptors, epoxides, and anilines (form reactive metabolites). LogP > 3 combined with high daily dose is a major DILI risk factor (Chen et al. 2013). Acyl glucuronide formation from carboxylic acids is a known DILI mechanism.

**Expected output**: Per-compound DILI risk assessment with triggered structural alerts, lipophilicity risk, reactive metabolite count, and overall risk classification.

---

## 5. hERG Channel Inhibition Risk Assessment

Predict hERG channel inhibition liability using molecular descriptors and structural features.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors
import numpy as np

def predict_herg_risk(smiles, compound_name="compound"):
    """Predict hERG channel inhibition risk from molecular structure.

    Uses descriptors correlated with hERG liability: LogP, basic nitrogen,
    molecular shape, and aromatic character.

    Parameters
    ----------
    smiles : str
        SMILES string.
    compound_name : str
        Compound identifier.

    Returns
    -------
    dict with hERG risk assessment and contributing factors.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {'compound': compound_name, 'valid': False}

    # Key descriptors for hERG prediction
    logp = Crippen.MolLogP(mol)
    mw = Descriptors.MolWt(mol)
    tpsa = Descriptors.TPSA(mol)
    aromatic_rings = Descriptors.NumAromaticRings(mol)
    n_rings = Descriptors.RingCount(mol)
    rot_bonds = Descriptors.NumRotatableBonds(mol)

    # Basic nitrogen count (protonatable at physiological pH)
    basic_n = 0
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 7:
            # Basic nitrogen: aliphatic amines, guanidines, amidines
            # Not basic: amides, sulfonamides, nitro, nitriles
            if atom.GetTotalNumHs() > 0 and atom.GetFormalCharge() >= 0:
                # Check if nitrogen is in amide
                is_amide = False
                for neighbor in atom.GetNeighbors():
                    if neighbor.GetAtomicNum() == 6:
                        for n_neighbor in neighbor.GetNeighbors():
                            if n_neighbor.GetAtomicNum() == 8 and \
                               mol.GetBondBetweenAtoms(neighbor.GetIdx(), n_neighbor.GetIdx()).GetBondTypeAsDouble() == 2:
                                is_amide = True
                if not is_amide:
                    basic_n += 1

    # hERG scoring model (simplified, based on Aronov 2005 and Cavalli 2002)
    score = 0
    risk_factors = []

    # LogP contribution (most important single descriptor)
    if logp > 4.5:
        score += 3
        risk_factors.append(f"High LogP ({logp:.2f} > 4.5)")
    elif logp > 3.7:
        score += 2
        risk_factors.append(f"Elevated LogP ({logp:.2f} > 3.7)")
    elif logp > 3.0:
        score += 1
        risk_factors.append(f"Moderate LogP ({logp:.2f} > 3.0)")

    # Basic nitrogen (cationic species block hERG channel)
    if basic_n >= 2:
        score += 3
        risk_factors.append(f"Multiple basic nitrogens ({basic_n})")
    elif basic_n == 1:
        score += 2
        risk_factors.append(f"Basic nitrogen present ({basic_n})")

    # Aromatic character (pi-stacking in channel vestibule)
    if aromatic_rings >= 3:
        score += 2
        risk_factors.append(f"Multiple aromatic rings ({aromatic_rings})")
    elif aromatic_rings >= 2:
        score += 1
        risk_factors.append(f"Two aromatic rings ({aromatic_rings})")

    # Molecular weight (optimal MW for hERG blockers: 300-550)
    if 300 <= mw <= 550:
        score += 1
        risk_factors.append(f"MW in hERG-prone range ({mw:.0f})")

    # Low TPSA (hydrophobic molecules penetrate membrane to reach channel)
    if tpsa < 40:
        score += 1
        risk_factors.append(f"Low TPSA ({tpsa:.1f} < 40)")

    # Structural patterns associated with hERG
    herg_patterns = {
        'piperidine': 'C1CCNCC1',
        'piperazine': 'C1CNCCN1',
        'basic_amine_linker': 'c1ccccc1CCN',
        'diphenylmethane': 'c1ccccc1Cc1ccccc1',
    }
    for pattern_name, smarts in herg_patterns.items():
        pat = Chem.MolFromSmarts(smarts)
        if pat and mol.HasSubstructMatch(pat):
            score += 1
            risk_factors.append(f"hERG-associated motif: {pattern_name}")

    # Risk classification
    if score >= 6:
        risk = 'HIGH'
        estimated_ic50 = '< 1 uM (likely)'
    elif score >= 4:
        risk = 'MODERATE'
        estimated_ic50 = '1-10 uM (possible)'
    elif score >= 2:
        risk = 'LOW-MODERATE'
        estimated_ic50 = '> 10 uM (less likely)'
    else:
        risk = 'LOW'
        estimated_ic50 = '> 30 uM (unlikely)'

    result = {
        'compound': compound_name,
        'smiles': smiles,
        'LogP': round(logp, 2),
        'MW': round(mw, 1),
        'basic_N': basic_n,
        'aromatic_rings': aromatic_rings,
        'TPSA': round(tpsa, 1),
        'herg_score': score,
        'herg_risk': risk,
        'estimated_ic50': estimated_ic50,
        'risk_factors': risk_factors,
    }

    print(f"hERG Risk Assessment: {compound_name}")
    print(f"  LogP={logp:.2f}  MW={mw:.0f}  Basic N={basic_n}  Aromatic rings={aromatic_rings}  TPSA={tpsa:.1f}")
    print(f"  hERG score: {score}/10")
    print(f"  Risk: {risk}")
    print(f"  Estimated IC50: {estimated_ic50}")
    if risk_factors:
        print(f"  Risk factors:")
        for rf in risk_factors:
            print(f"    - {rf}")
    print(f"\n  Mitigation strategies:")
    if logp > 3.7:
        print(f"    - Reduce LogP: add polar groups, reduce aromatic ring count")
    if basic_n > 0:
        print(f"    - Reduce basicity: replace basic N with amide, remove or shield amine")
    if aromatic_rings >= 3:
        print(f"    - Reduce aromaticity: saturate one ring, add sp3 centers (increase Fsp3)")

    return result

# Example
predict_herg_risk("c1ccc(NC(=O)c2cc(Cl)ccc2F)cc1", "Test_kinase_inhibitor")
predict_herg_risk("CC(=O)Oc1ccccc1C(=O)O", "Aspirin")
```

**Key parameters**: LogP > 3.7 + basic nitrogen is the strongest hERG predictor. Piperidine and piperazine rings are over-represented among hERG blockers. TPSA < 40 indicates high membrane permeability allowing channel access. Mitigation: reduce LogP, replace basic nitrogen, increase Fsp3.

**Expected output**: hERG risk score with contributing factors, estimated IC50 range, and specific mitigation strategies.

---

## 6. Mutagenicity / Ames Test Prediction

Predict Ames mutagenicity using structural alert detection and molecular context.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors
import pandas as pd

def predict_ames_mutagenicity(smiles, compound_name="compound"):
    """Predict Ames mutagenicity risk using structural alerts.

    Based on known mutagenic structural motifs from Derek Nexus,
    Benigni-Bossa rules, and FDA QSAR guidelines.

    Parameters
    ----------
    smiles : str
        SMILES string.
    compound_name : str
        Compound identifier.

    Returns
    -------
    dict with mutagenicity assessment.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {'compound': compound_name, 'valid': False}

    # Comprehensive mutagenic structural alerts
    alerts = {
        # Aromatic amines (metabolically activated to nitrenium ions)
        'primary_aromatic_amine': ('[NH2]c1ccccc1', 'HIGH',
            'Primary aromatic amines form reactive nitrenium ions via CYP activation'),
        'secondary_aromatic_amine': ('[NH1]([#6])c1ccccc1', 'MODERATE',
            'Secondary aromatic amines can be N-oxidized'),
        'aminobiphenyl': ('c1ccc(-c2ccc(N)cc2)cc1', 'HIGH',
            'Aminobiphenyls are potent mutagens (e.g., 4-aminobiphenyl)'),

        # Nitro compounds
        'nitroaromatic': ('[N+](=O)[O-]c', 'HIGH',
            'Nitroarenes reduced to reactive nitroso/hydroxylamine intermediates'),
        'aliphatic_nitro': ('[N+](=O)[O-][CX4]', 'MODERATE',
            'Aliphatic nitro compounds can be reduced to reactive species'),

        # Alkylating agents
        'epoxide': ('C1OC1', 'HIGH',
            'Epoxides alkylate DNA directly at guanine N7'),
        'aziridine': ('C1NC1', 'HIGH',
            'Aziridines are potent DNA alkylating agents'),
        'nitrogen_mustard': ('ClCCN(CCCl)', 'HIGH',
            'Nitrogen mustards crosslink DNA'),
        'alkyl_halide': ('[CH2][F,Cl,Br,I]', 'MODERATE',
            'Primary alkyl halides can alkylate DNA'),

        # Michael acceptors
        'alpha_beta_unsaturated_carbonyl': ('C=CC=O', 'MODERATE',
            'Michael acceptors react with nucleophilic DNA bases'),
        'acrylamide': ('C=CC(=O)N', 'MODERATE',
            'Acrylamide-like electrophiles'),

        # Hydrazines and azo compounds
        'hydrazine': ('NN', 'HIGH',
            'Hydrazines generate reactive diazomethane-like species'),
        'azo_compound': ('N=N', 'MODERATE',
            'Azo compounds can be reduced to aromatic amines'),

        # N-nitroso compounds
        'n_nitroso': ('N(=O)N', 'HIGH',
            'N-nitrosamines are potent mutagens and carcinogens'),

        # Polycyclic aromatic systems
        'bay_region_pah': ('c1cc2ccc3cccc4ccc(c1)c2c34', 'HIGH',
            'Bay region PAHs form reactive diol-epoxides'),

        # Aldehydes
        'aldehyde': ('[CH1](=O)', 'MODERATE',
            'Aldehydes form Schiff bases with DNA'),
    }

    triggered = []
    total_score = 0

    for name, (smarts, severity, description) in alerts.items():
        pat = Chem.MolFromSmarts(smarts)
        if pat and mol.HasSubstructMatch(pat):
            n_matches = len(mol.GetSubstructMatches(pat))
            severity_score = {'HIGH': 3, 'MODERATE': 2, 'LOW': 1}[severity]
            total_score += severity_score * n_matches
            triggered.append({
                'alert': name,
                'severity': severity,
                'count': n_matches,
                'description': description,
            })

    # Overall classification
    if total_score >= 6 or any(t['severity'] == 'HIGH' for t in triggered):
        prediction = 'MUTAGENIC (likely)'
        confidence = 'HIGH' if total_score >= 6 else 'MODERATE'
    elif total_score >= 2:
        prediction = 'EQUIVOCAL (possible)'
        confidence = 'LOW'
    else:
        prediction = 'NON-MUTAGENIC (likely)'
        confidence = 'MODERATE'

    result = {
        'compound': compound_name,
        'smiles': smiles,
        'n_alerts': len(triggered),
        'score': total_score,
        'prediction': prediction,
        'confidence': confidence,
        'alerts': triggered,
    }

    print(f"Ames Mutagenicity Prediction: {compound_name}")
    print(f"  Prediction: {prediction}")
    print(f"  Confidence: {confidence}")
    print(f"  Structural alerts: {len(triggered)} (score: {total_score})")
    for t in triggered:
        print(f"    [{t['severity']}] {t['alert']} (x{t['count']}): {t['description']}")
    if not triggered:
        print(f"    No mutagenic structural alerts detected")

    return result

# Example
predict_ames_mutagenicity("Nc1ccc(N)cc1", "p-Phenylenediamine")  # Known mutagen
predict_ames_mutagenicity("CC(=O)Oc1ccccc1C(=O)O", "Aspirin")    # Non-mutagen
```

**Key parameters**: Aromatic amines, nitroaromatics, and epoxides are the highest-risk mutagenic alerts. N-nitroso compounds (nitrosamines) are particularly concerning for pharmaceuticals. Severity scoring: HIGH alerts (3 points), MODERATE (2 points). Score >= 6 or any HIGH alert triggers mutagenic classification.

**Expected output**: Ames mutagenicity prediction with severity-ranked structural alerts and mechanistic descriptions.

---

## 7. Skin Sensitization Prediction: DPRA / KeratinoSens In Silico Models

Predict skin sensitization potential using reactivity-based structural alerts.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen

def predict_skin_sensitization(smiles, compound_name="compound"):
    """Predict skin sensitization potential based on protein reactivity.

    Models the adverse outcome pathway (AOP) for skin sensitization:
    1. Covalent binding to skin proteins (electrophilic reactivity)
    2. Keratinocyte activation
    3. Dendritic cell activation
    4. T-cell proliferation

    Parameters
    ----------
    smiles : str
        SMILES string.
    compound_name : str
        Compound identifier.

    Returns
    -------
    dict with skin sensitization risk assessment.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {'compound': compound_name, 'valid': False}

    logp = Crippen.MolLogP(mol)
    mw = Descriptors.MolWt(mol)

    # Protein-reactive structural alerts (DPRA reactivity domains)
    # Based on Roberts & Aptula mechanistic domains
    reactivity_alerts = {
        'michael_acceptor': ('C=CC(=O)', 'Michael addition to Cys/Lys'),
        'aldehyde': ('[CH1](=O)', 'Schiff base with Lys'),
        'activated_ester': ('C(=O)Oc1ccccc1', 'Acyl transfer to Lys/Cys'),
        'anhydride': ('C(=O)OC(=O)', 'Acylation of Lys'),
        'isocyanate': ('N=C=O', 'Reaction with Lys/Cys'),
        'isothiocyanate': ('N=C=S', 'Reaction with Cys'),
        'alpha_halo_carbonyl': ('C(=O)C[F,Cl,Br,I]', 'SN2 with Cys'),
        'epoxide': ('C1OC1', 'Ring opening with Cys/Lys'),
        'quinone': ('[#6]1=[#6][#6](=[O])[#6]=[#6][#6]1=[O]', 'Michael addition to Cys'),
        'sulfonyl_chloride': ('S(=O)(=O)Cl', 'Sulfonylation of Lys'),
        'acid_chloride': ('C(=O)Cl', 'Acylation of Lys'),
        'acrylate': ('C=CC(=O)O', 'Michael addition'),
        'diketone': ('C(=O)C(=O)', 'Condensation with Lys'),
    }

    triggered = []
    for name, (smarts, mechanism) in reactivity_alerts.items():
        pat = Chem.MolFromSmarts(smarts)
        if pat and mol.HasSubstructMatch(pat):
            triggered.append({'alert': name, 'mechanism': mechanism})

    # Skin penetration estimate (MW < 500 and LogP 1-3 optimal for skin absorption)
    skin_penetration = 'HIGH' if (mw < 500 and 1 <= logp <= 4) else \
                       'MODERATE' if (mw < 1000 and 0 <= logp <= 5) else 'LOW'

    # Overall risk
    n_reactive = len(triggered)
    if n_reactive >= 2 and skin_penetration != 'LOW':
        risk = 'STRONG SENSITIZER'
    elif n_reactive >= 1 and skin_penetration != 'LOW':
        risk = 'MODERATE SENSITIZER'
    elif n_reactive >= 1:
        risk = 'WEAK SENSITIZER (low penetration)'
    else:
        risk = 'NON-SENSITIZER (likely)'

    result = {
        'compound': compound_name,
        'smiles': smiles,
        'MW': round(mw, 1),
        'LogP': round(logp, 2),
        'skin_penetration': skin_penetration,
        'n_reactive_alerts': n_reactive,
        'alerts': triggered,
        'sensitization_risk': risk,
    }

    print(f"Skin Sensitization Prediction: {compound_name}")
    print(f"  MW={mw:.0f}  LogP={logp:.2f}  Skin penetration: {skin_penetration}")
    print(f"  Reactive alerts: {n_reactive}")
    for t in triggered:
        print(f"    - {t['alert']}: {t['mechanism']}")
    print(f"  Risk: {risk}")

    return result

# Example
predict_skin_sensitization("C=CC(=O)OC", "Methyl_acrylate")  # Known sensitizer
predict_skin_sensitization("CC(=O)Oc1ccccc1C(=O)O", "Aspirin")
```

**Key parameters**: Skin sensitization follows an AOP: electrophilic reactivity with proteins -> keratinocyte activation -> immune response. Michael acceptors, aldehydes, and epoxides are the most common reactive motifs. Skin penetration requires MW < 500 and LogP 1-4.

**Expected output**: Sensitization risk classification with reactive structural alerts and underlying protein-binding mechanisms.

---

## 8. PAINS (Pan-Assay Interference Compounds) Filtering

Filter compounds for assay interference using RDKit's built-in PAINS catalog.

```python
from rdkit import Chem
from rdkit.Chem import FilterCatalog, Descriptors
import pandas as pd

def pains_filter(smiles_list, names=None, verbose=True):
    """Filter compounds for PAINS (Pan-Assay Interference Compounds).

    PAINS substructures cause false positives in HTS assays through
    mechanisms including aggregation, redox cycling, metal chelation,
    and fluorescence interference.

    Parameters
    ----------
    smiles_list : list of str
        SMILES strings to filter.
    names : list of str or None
        Compound names.
    verbose : bool
        Print detailed alert information.

    Returns
    -------
    pd.DataFrame with PAINS filter results.
    """
    if names is None:
        names = [f"Compound_{i+1}" for i in range(len(smiles_list))]

    # Initialize PAINS filter catalogs (three levels from Baell & Holloway 2010)
    params_a = FilterCatalog.FilterCatalogParams()
    params_a.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_A)
    catalog_a = FilterCatalog.FilterCatalog(params_a)

    params_b = FilterCatalog.FilterCatalogParams()
    params_b.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_B)
    catalog_b = FilterCatalog.FilterCatalog(params_b)

    params_c = FilterCatalog.FilterCatalogParams()
    params_c.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_C)
    catalog_c = FilterCatalog.FilterCatalog(params_c)

    # Combined catalog
    params_all = FilterCatalog.FilterCatalogParams()
    params_all.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
    catalog_all = FilterCatalog.FilterCatalog(params_all)

    results = []
    for smi, name in zip(smiles_list, names):
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            results.append({'name': name, 'smiles': smi, 'valid': False, 'pains_pass': False})
            continue

        # Check all PAINS filters
        entry = catalog_all.GetFirstMatch(mol)
        all_matches = []
        for e in catalog_all.GetMatches(mol):
            all_matches.append(e.GetDescription())

        pains_pass = len(all_matches) == 0

        results.append({
            'name': name,
            'smiles': smi,
            'valid': True,
            'pains_pass': pains_pass,
            'n_pains_alerts': len(all_matches),
            'pains_alerts': '; '.join(all_matches) if all_matches else 'none',
        })

        if verbose and all_matches:
            print(f"  PAINS FAIL: {name}")
            for alert in all_matches:
                print(f"    Alert: {alert}")

    df = pd.DataFrame(results)

    print(f"\nPAINS Filter Summary:")
    print(f"  Total compounds: {len(df)}")
    print(f"  PASS: {df['pains_pass'].sum()}")
    print(f"  FAIL: {(~df['pains_pass']).sum()}")
    print(f"  Invalid SMILES: {(~df['valid']).sum()}")

    return df

# Example: known PAINS compounds
test_smiles = [
    "CC(=O)Oc1ccccc1C(=O)O",                      # Aspirin - should pass
    "O=C1CC(/N=N/c2ccccc2)C(=O)N1",                # Azo dye - PAINS
    "Oc1cc(O)c2c(c1)oc(-c1ccc(O)cc1)c(O)c2=O",   # Quercetin - catechol PAINS
    "c1ccc(NC(=O)c2ccccc2)cc1",                     # Benzanilide - should pass
    "O=c1cc(-c2ccccc2)oc2cc(O)cc(O)c12",           # Chrysin-like - potential PAINS
]
result = pains_filter(test_smiles, names=["Aspirin", "Azo_dye", "Quercetin", "Benzanilide", "Chrysin"])
```

**Key parameters**: PAINS_A (most common interference patterns), PAINS_B (additional alerts), PAINS_C (least common). RDKit includes all 480 PAINS substructure filters from Baell & Holloway 2010. PAINS compounds should be excluded from HTS hit lists unless there is strong orthogonal evidence.

**Expected output**: Per-compound PAINS filter results with specific alert descriptions. Summary of pass/fail counts.

---

## 9. Brenk Structural Alert Filtering

Filter compounds for unwanted substructures using the Brenk alert catalog.

```python
from rdkit import Chem
from rdkit.Chem import FilterCatalog
import pandas as pd

def brenk_filter(smiles_list, names=None):
    """Filter compounds using Brenk unwanted substructure alerts.

    Brenk et al. (2008) compiled 105 structural fragments associated with
    toxicity, reactivity, metabolic instability, or poor druglikeness.

    Parameters
    ----------
    smiles_list : list of str
        SMILES strings.
    names : list of str or None
        Compound names.

    Returns
    -------
    pd.DataFrame with filter results.
    """
    if names is None:
        names = [f"Compound_{i+1}" for i in range(len(smiles_list))]

    # Initialize Brenk filter catalog
    params = FilterCatalog.FilterCatalogParams()
    params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.BRENK)
    catalog = FilterCatalog.FilterCatalog(params)

    results = []
    for smi, name in zip(smiles_list, names):
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            results.append({'name': name, 'smiles': smi, 'valid': False, 'brenk_pass': False})
            continue

        matches = []
        for entry in catalog.GetMatches(mol):
            matches.append(entry.GetDescription())

        brenk_pass = len(matches) == 0

        results.append({
            'name': name,
            'smiles': smi,
            'valid': True,
            'brenk_pass': brenk_pass,
            'n_brenk_alerts': len(matches),
            'brenk_alerts': '; '.join(matches) if matches else 'none',
        })

    df = pd.DataFrame(results)

    print(f"Brenk Structural Alert Filter:")
    print(f"  Total: {len(df)} | PASS: {df['brenk_pass'].sum()} | FAIL: {(~df['brenk_pass']).sum()}")
    print(f"\nFailed compounds:")
    for _, row in df[df['brenk_pass'] == False].iterrows():
        if row['valid']:
            print(f"  {row['name']}: {row['brenk_alerts']}")

    return df

# Example
test = ["CC(=O)Oc1ccccc1C(=O)O", "O=[N+]([O-])c1ccccc1", "CSSC", "c1ccc(NC(=O)C)cc1"]
brenk_filter(test, names=["Aspirin", "Nitrobenzene", "Dimethyl_disulfide", "Acetanilide"])
```

**Key parameters**: Brenk catalog contains 105 unwanted substructures covering reactive groups (aldehydes, Michael acceptors), toxicophores (nitro aromatics, azo compounds), metabolic liabilities (thiols, epoxides), and promiscuous binders. Use in combination with PAINS for comprehensive filtering.

**Expected output**: Per-compound Brenk filter results with specific triggered alerts. Use alongside PAINS filter for a two-layer structural alert screen.

---

## 10. Drug-Likeness Composite Scoring: Lipinski + Veber + Ghose + Egan

Compute a composite drug-likeness score combining multiple rule sets.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors
import pandas as pd

def composite_druglikeness(smiles, compound_name="compound"):
    """Compute composite drug-likeness score from multiple rule sets.

    Evaluates Lipinski (Ro5), Veber, Ghose, and Egan rules, then
    computes a weighted composite score.

    Parameters
    ----------
    smiles : str
        SMILES string.
    compound_name : str
        Compound identifier.

    Returns
    -------
    dict with individual rule results and composite score.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {'compound': compound_name, 'valid': False}

    # Calculate all required descriptors
    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    rot_bonds = Descriptors.NumRotatableBonds(mol)
    mr = Crippen.MolMR(mol)  # Molar refractivity
    n_atoms = Descriptors.HeavyAtomCount(mol)
    n_rings = Descriptors.RingCount(mol)
    fsp3 = rdMolDescriptors.CalcFractionCSP3(mol)

    # ---- Lipinski Rule of Five (1997) ----
    lipinski_violations = sum([mw > 500, logp > 5, hbd > 5, hba > 10])
    lipinski_pass = lipinski_violations <= 1
    lipinski_score = max(0, 100 - lipinski_violations * 25)

    # ---- Veber Rules (2002) ----
    veber_violations = sum([tpsa > 140, rot_bonds > 10])
    veber_pass = veber_violations == 0
    veber_score = max(0, 100 - veber_violations * 50)

    # ---- Ghose Filter (1999) ----
    # -0.4 <= LogP <= 5.6, 160 <= MW <= 480, 40 <= MR <= 130, 20 <= atoms <= 70
    ghose_violations = sum([
        logp < -0.4 or logp > 5.6,
        mw < 160 or mw > 480,
        mr < 40 or mr > 130,
        n_atoms < 20 or n_atoms > 70,
    ])
    ghose_pass = ghose_violations == 0
    ghose_score = max(0, 100 - ghose_violations * 25)

    # ---- Egan Filter (2000) ----
    # LogP <= 5.88, TPSA <= 131.6
    egan_violations = sum([logp > 5.88, tpsa > 131.6])
    egan_pass = egan_violations == 0
    egan_score = max(0, 100 - egan_violations * 50)

    # ---- Muegge Filter (2001) ----
    # 200 <= MW <= 600, -2 <= LogP <= 5, TPSA <= 150, rings <= 7
    # rot_bonds <= 15, HBA <= 10, HBD <= 5
    muegge_violations = sum([
        mw < 200 or mw > 600,
        logp < -2 or logp > 5,
        tpsa > 150,
        n_rings > 7,
        rot_bonds > 15,
        hba > 10,
        hbd > 5,
    ])
    muegge_pass = muegge_violations <= 1
    muegge_score = max(0, 100 - muegge_violations * 15)

    # ---- Composite Score ----
    # Weighted: Lipinski (30%), Veber (25%), Egan (20%), Ghose (15%), Muegge (10%)
    composite = (lipinski_score * 0.30 + veber_score * 0.25 + egan_score * 0.20 +
                 ghose_score * 0.15 + muegge_score * 0.10)

    result = {
        'compound': compound_name,
        'smiles': smiles,
        'MW': round(mw, 1), 'LogP': round(logp, 2), 'TPSA': round(tpsa, 1),
        'HBD': hbd, 'HBA': hba, 'RotBonds': rot_bonds, 'Fsp3': round(fsp3, 2),
        'lipinski_pass': lipinski_pass, 'lipinski_score': lipinski_score,
        'veber_pass': veber_pass, 'veber_score': veber_score,
        'ghose_pass': ghose_pass, 'ghose_score': ghose_score,
        'egan_pass': egan_pass, 'egan_score': egan_score,
        'muegge_pass': muegge_pass, 'muegge_score': muegge_score,
        'composite_score': round(composite, 1),
    }

    print(f"Drug-Likeness Composite Score: {compound_name}")
    print(f"  MW={mw:.0f}  LogP={logp:.2f}  TPSA={tpsa:.0f}  HBD={hbd}  HBA={hba}  RotB={rot_bonds}  Fsp3={fsp3:.2f}")
    print(f"  {'Rule':<12} {'Pass':>5} {'Score':>6}")
    print(f"  {'-'*26}")
    for rule in ['lipinski', 'veber', 'ghose', 'egan', 'muegge']:
        p = "YES" if result[f'{rule}_pass'] else "NO"
        print(f"  {rule.capitalize():<12} {p:>5} {result[f'{rule}_score']:>5}/100")
    print(f"  {'Composite':<12} {'':>5} {composite:>5.0f}/100")

    category = "EXCELLENT" if composite >= 80 else "GOOD" if composite >= 60 else \
               "MODERATE" if composite >= 40 else "POOR"
    print(f"  Category: {category}")

    return result

# Example
composite_druglikeness("CC(=O)Oc1ccccc1C(=O)O", "Aspirin")
composite_druglikeness("CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34C", "Testosterone")
```

**Key parameters**: Five rule sets with different origins and stringency. Lipinski (oral absorption), Veber (bioavailability), Ghose (drug-like chemical space), Egan (passive absorption), Muegge (pharmacologically relevant space). Composite weighting reflects each rule's predictive importance.

**Expected output**: Individual pass/fail and scores for each rule set plus a weighted composite score (0-100) with category classification.

---

## 11. Composite Drug Candidate Ranking

Rank drug candidates across efficacy, ADMET, toxicity, and novelty dimensions.

```python
import pandas as pd
import numpy as np

def rank_drug_candidates(candidates, weights=None):
    """Rank drug candidates using weighted multi-parameter scoring.

    Parameters
    ----------
    candidates : list of dict
        Each dict must contain:
        - 'name': compound name
        - 'smiles': SMILES string
        - 'potency_nM': IC50/EC50 in nM (lower = better)
        - 'selectivity_ratio': ratio over closest off-target (higher = better)
        - 'lipinski_violations': 0-4
        - 'admet_flags': number of ADMET concerns (0-5)
        - 'toxicity_alerts': number of toxicity structural alerts (0-5)
        - 'novelty_score': 0-100 (Tanimoto distance from known drugs * 100)
    weights : dict or None
        Custom weights for each dimension.

    Returns
    -------
    pd.DataFrame with ranked candidates.
    """
    if weights is None:
        weights = {
            'efficacy': 0.35,      # Potency + selectivity
            'admet': 0.25,         # Drug-likeness + ADMET profile
            'safety': 0.25,        # Toxicity alerts + hERG + mutagenicity
            'novelty': 0.15,       # Chemical novelty (IP potential)
        }

    results = []
    for c in candidates:
        # Efficacy score (0-100)
        # Potency: <10 nM = 100, 10-100 nM = 80, 100-1000 nM = 60, >1000 nM = 40
        potency = c.get('potency_nM', 1000)
        if potency < 10:
            potency_score = 100
        elif potency < 100:
            potency_score = 80
        elif potency < 1000:
            potency_score = 60
        else:
            potency_score = 40

        selectivity = c.get('selectivity_ratio', 1)
        selectivity_score = min(100, selectivity * 10)  # 10x = 100

        efficacy_score = potency_score * 0.6 + selectivity_score * 0.4

        # ADMET score (0-100)
        lipinski_v = c.get('lipinski_violations', 0)
        admet_flags = c.get('admet_flags', 0)
        admet_score = max(0, 100 - lipinski_v * 15 - admet_flags * 15)

        # Safety score (0-100)
        tox_alerts = c.get('toxicity_alerts', 0)
        herg_penalty = c.get('herg_risk_score', 0) * 5
        safety_score = max(0, 100 - tox_alerts * 20 - herg_penalty)

        # Novelty score (0-100)
        novelty = c.get('novelty_score', 50)

        # Composite
        composite = (efficacy_score * weights['efficacy'] +
                     admet_score * weights['admet'] +
                     safety_score * weights['safety'] +
                     novelty * weights['novelty'])

        results.append({
            'name': c['name'],
            'smiles': c.get('smiles', ''),
            'potency_nM': potency,
            'efficacy_score': round(efficacy_score, 1),
            'admet_score': round(admet_score, 1),
            'safety_score': round(safety_score, 1),
            'novelty_score': round(novelty, 1),
            'composite': round(composite, 1),
        })

    df = pd.DataFrame(results).sort_values('composite', ascending=False)
    df['rank'] = range(1, len(df) + 1)

    print(f"Drug Candidate Ranking ({len(df)} compounds)")
    print(f"Weights: Efficacy={weights['efficacy']:.0%}  ADMET={weights['admet']:.0%}  "
          f"Safety={weights['safety']:.0%}  Novelty={weights['novelty']:.0%}")
    print(f"\n{'Rank':>4} {'Name':<20} {'Potency':>8} {'Efficacy':>8} {'ADMET':>6} "
          f"{'Safety':>7} {'Novel':>6} {'TOTAL':>6}")
    print("-" * 70)
    for _, row in df.iterrows():
        print(f"{row['rank']:>4} {row['name']:<20} {row['potency_nM']:>7.0f}nM "
              f"{row['efficacy_score']:>7.1f} {row['admet_score']:>5.0f} "
              f"{row['safety_score']:>6.0f} {row['novelty_score']:>5.0f} {row['composite']:>5.1f}")

    # Highlight top candidates
    top = df.head(3)
    print(f"\nTop 3 candidates:")
    for _, row in top.iterrows():
        print(f"  #{row['rank']}: {row['name']} (composite: {row['composite']:.1f})")

    df.to_csv("candidate_ranking.csv", index=False)
    return df

# Example
candidates = [
    {'name': 'Lead_A', 'potency_nM': 15, 'selectivity_ratio': 50,
     'lipinski_violations': 0, 'admet_flags': 1, 'toxicity_alerts': 0,
     'novelty_score': 80},
    {'name': 'Lead_B', 'potency_nM': 5, 'selectivity_ratio': 10,
     'lipinski_violations': 1, 'admet_flags': 2, 'toxicity_alerts': 1,
     'novelty_score': 60},
    {'name': 'Lead_C', 'potency_nM': 200, 'selectivity_ratio': 100,
     'lipinski_violations': 0, 'admet_flags': 0, 'toxicity_alerts': 0,
     'novelty_score': 90},
    {'name': 'Lead_D', 'potency_nM': 50, 'selectivity_ratio': 30,
     'lipinski_violations': 0, 'admet_flags': 1, 'toxicity_alerts': 0,
     'novelty_score': 70},
]
rank_drug_candidates(candidates)
```

**Key parameters**: Default weights: Efficacy 35%, ADMET 25%, Safety 25%, Novelty 15%. Adjust weights based on program stage (early discovery: weight novelty higher; late lead optimization: weight safety higher). Potency scoring: <10 nM is excellent, >1000 nM is poor.

**Expected output**: Ranked compound table with per-dimension scores and composite ranking. CSV output for portfolio review.

---

## 12. Safety Pharmacology Panel: Off-Target Activity Prediction

Predict off-target activity across ion channels, GPCRs, and transporters.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen
import pandas as pd

def safety_pharmacology_panel(smiles, compound_name="compound"):
    """Predict off-target activity risk across safety pharmacology targets.

    Covers major safety targets: ion channels (hERG, Nav1.5, Cav1.2),
    GPCRs (5-HT2B, adrenergic, muscarinic), and transporters (OATP, OCT2).

    Parameters
    ----------
    smiles : str
        SMILES string.
    compound_name : str
        Compound identifier.

    Returns
    -------
    dict with per-target risk assessment.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {'compound': compound_name, 'valid': False}

    logp = Crippen.MolLogP(mol)
    mw = Descriptors.MolWt(mol)
    tpsa = Descriptors.TPSA(mol)
    hbd = Descriptors.NumHDonors(mol)
    aromatic_rings = Descriptors.NumAromaticRings(mol)

    # Basic nitrogen count
    basic_n = sum(1 for atom in mol.GetAtoms()
                  if atom.GetAtomicNum() == 7 and atom.GetFormalCharge() >= 0
                  and atom.GetTotalNumHs() > 0
                  and not any(n.GetAtomicNum() == 8 and
                              mol.GetBondBetweenAtoms(atom.GetIdx(), n.GetIdx()) and
                              mol.GetBondBetweenAtoms(atom.GetIdx(), n.GetIdx()).GetBondTypeAsDouble() == 2
                              for n in atom.GetNeighbors() if n.GetAtomicNum() == 6
                              for n2 in n.GetNeighbors() if n2.GetAtomicNum() == 8))

    targets = {}

    # ---- ION CHANNELS ----
    # hERG (cardiac QT prolongation)
    herg_score = 0
    if logp > 3.7 and basic_n > 0: herg_score = 3
    elif logp > 3: herg_score = 2
    elif basic_n > 0: herg_score = 1
    targets['hERG (Kv11.1)'] = {
        'risk': 'HIGH' if herg_score >= 3 else 'MODERATE' if herg_score >= 2 else 'LOW',
        'concern': 'QT prolongation, Torsade de Pointes',
    }

    # Nav1.5 (cardiac sodium channel)
    nav_score = 1 if (logp > 3 and aromatic_rings >= 2) else 0
    targets['Nav1.5'] = {
        'risk': 'MODERATE' if nav_score >= 1 else 'LOW',
        'concern': 'Cardiac conduction abnormalities',
    }

    # Cav1.2 (L-type calcium channel)
    cav_score = 1 if (logp > 2.5 and mw > 300 and aromatic_rings >= 2) else 0
    targets['Cav1.2'] = {
        'risk': 'MODERATE' if cav_score >= 1 else 'LOW',
        'concern': 'Cardiac contractility, blood pressure',
    }

    # ---- GPCRs ----
    # 5-HT2B (serotonin receptor - cardiac valvulopathy)
    has_indole = mol.HasSubstructMatch(Chem.MolFromSmarts('c1cc2[nH]ccc2cc1')) if Chem.MolFromSmarts('c1cc2[nH]ccc2cc1') else False
    targets['5-HT2B'] = {
        'risk': 'MODERATE' if (basic_n > 0 and (has_indole or aromatic_rings >= 2)) else 'LOW',
        'concern': 'Cardiac valvulopathy (fen-phen)',
    }

    # Adrenergic receptors
    targets['Alpha-1 adrenergic'] = {
        'risk': 'MODERATE' if (basic_n > 0 and logp > 2 and aromatic_rings >= 1) else 'LOW',
        'concern': 'Hypotension, sedation',
    }

    # Muscarinic receptors
    targets['Muscarinic (M1-M5)'] = {
        'risk': 'MODERATE' if (basic_n > 0 and logp > 1 and tpsa < 60) else 'LOW',
        'concern': 'Dry mouth, constipation, cognitive impairment',
    }

    # Dopamine D2
    targets['Dopamine D2'] = {
        'risk': 'MODERATE' if (basic_n > 0 and aromatic_rings >= 2 and logp > 2) else 'LOW',
        'concern': 'Extrapyramidal effects, prolactin elevation',
    }

    # ---- TRANSPORTERS ----
    # P-glycoprotein
    targets['P-gp (MDR1)'] = {
        'risk': 'HIGH' if (mw > 400 and hbd > 2 and tpsa > 75) else 'LOW',
        'concern': 'Drug efflux, reduced oral absorption, DDI',
    }

    # OATP1B1/1B3 (hepatic uptake)
    targets['OATP1B1/1B3'] = {
        'risk': 'MODERATE' if (logp > 2 and mw > 400) else 'LOW',
        'concern': 'Hepatic uptake DDI (statin interaction)',
    }

    # OCT2 (renal)
    targets['OCT2'] = {
        'risk': 'MODERATE' if (basic_n > 0 and mw < 500) else 'LOW',
        'concern': 'Renal clearance DDI (metformin interaction)',
    }

    # Summary
    high_risk = [t for t, v in targets.items() if v['risk'] == 'HIGH']
    moderate_risk = [t for t, v in targets.items() if v['risk'] == 'MODERATE']

    print(f"Safety Pharmacology Panel: {compound_name}")
    print(f"  MW={mw:.0f}  LogP={logp:.2f}  TPSA={tpsa:.0f}  Basic N={basic_n}  Aromatic={aromatic_rings}")
    print(f"\n  {'Target':<25} {'Risk':>10} {'Concern'}")
    print(f"  {'-'*70}")
    for target, info in targets.items():
        color = info['risk']
        print(f"  {target:<25} {color:>10} {info['concern']}")

    print(f"\n  Summary: {len(high_risk)} HIGH risk, {len(moderate_risk)} MODERATE risk targets")
    if high_risk:
        print(f"  HIGH risk: {', '.join(high_risk)}")
    if moderate_risk:
        print(f"  MODERATE risk: {', '.join(moderate_risk)}")

    return {'compound': compound_name, 'targets': targets,
            'high_risk_count': len(high_risk), 'moderate_risk_count': len(moderate_risk)}

# Example
safety_pharmacology_panel("c1ccc(NC(=O)c2cc(Cl)ccc2F)cc1", "Test_compound")
safety_pharmacology_panel("CC(=O)Oc1ccccc1C(=O)O", "Aspirin")
```

**Key parameters**: Covers 10 key safety pharmacology targets across ion channels (hERG, Nav1.5, Cav1.2), GPCRs (5-HT2B, adrenergic, muscarinic, D2), and transporters (P-gp, OATP, OCT2). Risk driven primarily by LogP, basic nitrogen count, and aromatic character.

**Expected output**: Per-target risk assessment with clinical concern descriptions and summary of total HIGH/MODERATE risk targets.

---

## 13. Clearance Prediction: CYP450 Substrate/Inhibitor Assessment

Assess CYP450 metabolic liability across major isoforms.

```python
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors
import pandas as pd

def cyp450_assessment(smiles, compound_name="compound"):
    """Predict CYP450 substrate and inhibitor liability for major isoforms.

    Covers CYP3A4, CYP2D6, CYP2C9, CYP2C19, and CYP1A2.

    Parameters
    ----------
    smiles : str
        SMILES string.
    compound_name : str
        Compound identifier.

    Returns
    -------
    dict with per-isoform substrate and inhibitor risk.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {'compound': compound_name, 'valid': False}

    logp = Crippen.MolLogP(mol)
    mw = Descriptors.MolWt(mol)
    tpsa = Descriptors.TPSA(mol)
    aromatic_rings = Descriptors.NumAromaticRings(mol)
    n_rings = Descriptors.RingCount(mol)
    hba = Descriptors.NumHAcceptors(mol)
    rot_bonds = Descriptors.NumRotatableBonds(mol)

    # Basic nitrogen
    basic_n = sum(1 for atom in mol.GetAtoms()
                  if atom.GetAtomicNum() == 7 and atom.GetTotalNumHs() > 0
                  and atom.GetFormalCharge() >= 0)

    # Acidic groups (carboxylic acids)
    acid_pattern = Chem.MolFromSmarts('[CX3](=O)[OX2H1]')
    n_acids = len(mol.GetSubstructMatches(acid_pattern)) if acid_pattern else 0

    isoforms = {}

    # ---- CYP3A4 (metabolizes ~50% of drugs) ----
    # Substrates: large, lipophilic molecules
    sub_3a4 = 'HIGH' if (logp > 3 and mw > 300 and aromatic_rings >= 2) else \
              'MODERATE' if (logp > 2 and mw > 250) else 'LOW'
    inh_3a4 = 'HIGH' if (logp > 3.5 and aromatic_rings >= 2 and basic_n > 0) else \
              'MODERATE' if (logp > 2.5 and aromatic_rings >= 1) else 'LOW'
    isoforms['CYP3A4'] = {
        'substrate_risk': sub_3a4,
        'inhibitor_risk': inh_3a4,
        'fraction_metabolized': '~50% of all drugs',
        'clinical_impact': 'Major DDI enzyme; co-admin with ketoconazole, ritonavir',
    }

    # ---- CYP2D6 (metabolizes ~25% of drugs) ----
    # Substrates: basic, lipophilic, with planar aromatic and basic nitrogen 5-7 A apart
    sub_2d6 = 'HIGH' if (basic_n > 0 and logp > 1.5 and mw < 500) else \
              'MODERATE' if (basic_n > 0 and logp > 0.5) else 'LOW'
    inh_2d6 = 'HIGH' if (basic_n > 0 and logp > 2 and aromatic_rings >= 1) else 'LOW'
    isoforms['CYP2D6'] = {
        'substrate_risk': sub_2d6,
        'inhibitor_risk': inh_2d6,
        'fraction_metabolized': '~25% of drugs; polymorphic (PM 5-10% Caucasians)',
        'clinical_impact': 'Polymorphic; poor metabolizers at risk for toxicity',
    }

    # ---- CYP2C9 ----
    # Substrates: weakly acidic, lipophilic
    sub_2c9 = 'HIGH' if (n_acids > 0 and logp > 2 and mw > 300) else \
              'MODERATE' if (logp > 2 and n_acids > 0) else 'LOW'
    inh_2c9 = 'MODERATE' if (logp > 3 and aromatic_rings >= 2) else 'LOW'
    isoforms['CYP2C9'] = {
        'substrate_risk': sub_2c9,
        'inhibitor_risk': inh_2c9,
        'fraction_metabolized': 'NSAIDs, warfarin, phenytoin',
        'clinical_impact': 'Warfarin metabolism; inhibition increases bleeding risk',
    }

    # ---- CYP2C19 ----
    sub_2c19 = 'MODERATE' if (logp > 1.5 and mw > 250 and aromatic_rings >= 1) else 'LOW'
    inh_2c19 = 'MODERATE' if (logp > 2 and aromatic_rings >= 2) else 'LOW'
    isoforms['CYP2C19'] = {
        'substrate_risk': sub_2c19,
        'inhibitor_risk': inh_2c19,
        'fraction_metabolized': 'PPIs, clopidogrel, antidepressants',
        'clinical_impact': 'Polymorphic; clopidogrel activation requires CYP2C19',
    }

    # ---- CYP1A2 ----
    # Substrates: planar, aromatic
    sub_1a2 = 'HIGH' if (aromatic_rings >= 3 and logp > 1) else \
              'MODERATE' if (aromatic_rings >= 2 and logp > 0.5) else 'LOW'
    inh_1a2 = 'MODERATE' if (aromatic_rings >= 2 and logp > 1) else 'LOW'
    isoforms['CYP1A2'] = {
        'substrate_risk': sub_1a2,
        'inhibitor_risk': inh_1a2,
        'fraction_metabolized': 'Caffeine, theophylline, some antipsychotics',
        'clinical_impact': 'Induced by smoking; dose adjustment for smokers',
    }

    # Overall metabolic risk
    high_sub = sum(1 for v in isoforms.values() if v['substrate_risk'] == 'HIGH')
    high_inh = sum(1 for v in isoforms.values() if v['inhibitor_risk'] == 'HIGH')

    print(f"CYP450 Assessment: {compound_name}")
    print(f"  MW={mw:.0f}  LogP={logp:.2f}  Basic N={basic_n}  Acids={n_acids}  Aromatic={aromatic_rings}")
    print(f"\n  {'Isoform':<10} {'Substrate':>10} {'Inhibitor':>10} {'Clinical Impact'}")
    print(f"  {'-'*65}")
    for iso, info in isoforms.items():
        print(f"  {iso:<10} {info['substrate_risk']:>10} {info['inhibitor_risk']:>10} {info['clinical_impact'][:40]}")

    print(f"\n  Summary:")
    print(f"    HIGH substrate risk: {high_sub} isoforms")
    print(f"    HIGH inhibitor risk: {high_inh} isoforms")
    if high_inh > 0:
        print(f"    DDI WARNING: high inhibitor risk detected - assess clinical DDI potential")
    if high_sub > 1:
        print(f"    Metabolized by multiple CYPs - may have variable clearance across populations")

    return {'compound': compound_name, 'isoforms': isoforms,
            'high_substrate': high_sub, 'high_inhibitor': high_inh}

# Example
cyp450_assessment("c1ccc(NC(=O)c2cc(Cl)ccc2F)cc1", "Test_compound")
cyp450_assessment("CC(=O)Oc1ccccc1C(=O)O", "Aspirin")
```

**Key parameters**: CYP3A4 metabolizes ~50% of drugs (large, lipophilic substrates). CYP2D6 is polymorphic and prefers basic amines. CYP2C9 handles acidic/lipophilic drugs (warfarin). Inhibitor risk indicates DDI potential. Multiple HIGH substrate risks suggest complex pharmacokinetics.

**Expected output**: Per-isoform substrate and inhibitor risk with clinical impact context and DDI warnings.

---

## Quick Reference

| Task | Recipe | Key Method |
|------|--------|-----------|
| Full ADMET pipeline | #1 | 5-stage descriptor + rule-based |
| pkCSM/admetSAR queries | #2 | External ML services |
| ADMETlab 2.0 batch | #3 | 77-endpoint ML predictions |
| Hepatotoxicity/DILI | #4 | Structural alerts + DILIst |
| hERG inhibition risk | #5 | Descriptor scoring + motifs |
| Ames mutagenicity | #6 | 16 mutagenic alert patterns |
| Skin sensitization | #7 | Protein reactivity alerts |
| PAINS filtering | #8 | RDKit FilterCatalog (480 patterns) |
| Brenk filtering | #9 | RDKit Brenk catalog (105 patterns) |
| Composite drug-likeness | #10 | Lipinski + Veber + Ghose + Egan + Muegge |
| Candidate ranking | #11 | Weighted multi-parameter scoring |
| Safety pharmacology | #12 | 10 off-target panels |
| CYP450 assessment | #13 | 5-isoform substrate + inhibitor |

---

## Cross-Skill Routing

- ML model training for ADMET (DeepChem, ChemBERTa) --> [ml-recipes.md](ml-recipes.md)
- RDKit basics (Lipinski, fingerprints, PAINS) --> [recipes.md](recipes.md)
- Full medicinal chemistry pipeline with MCP tools --> parent [SKILL.md](SKILL.md)
- Protein-ligand binding and docking --> `binder-discovery-specialist`
- Clinical pharmacokinetics modeling --> `clinical-pharmacology`
- Drug-drug interaction assessment --> `drug-interaction-analyst`
