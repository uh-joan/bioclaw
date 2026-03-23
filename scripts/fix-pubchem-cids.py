#!/usr/bin/env python3
"""
Fix missing PubChem CIDs by trying alternate name strategies:
1. Strip parenthetical suffixes: "PT-141 (Bremelanotide)" → "Bremelanotide"
2. Try known alternate names from a manual mapping
3. Fall back to PubChem's autocomplete/search API
"""

import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import re
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent.parent / "container" / "skills" / "peptigotchi" / "knowledge"
COMPOUNDS_FILE = KNOWLEDGE_DIR / "compounds.json"

# Manual name mappings for compounds PubChem indexes differently
ALT_NAMES = {
    "retatrutide": ["LY3437943"],
    "tb-500": ["thymosin beta-4"],
    "cjc-1295": ["modified GRF 1-29", "CJC1295"],
    "liraglutide": ["liraglutide"],
    "pt-141": ["bremelanotide"],
    "cagrilintide": ["NN9838"],
    "eloralintide": ["eloralintide"],
    "mazdutide": ["LY3305677", "IBI362"],
    "orforglipron": ["LY3502970"],
    "survodutide": ["BI 456906"],
    "aod-9604": ["AOD9604", "anti-obesity drug 9604"],
    "sermorelin": ["sermorelin acetate", "sermorelin"],
    "ss-31": ["elamipretide", "MTP-131"],
    "dsip": ["delta sleep-inducing peptide"],
    "epithalon": ["epitalon", "epithalamin"],
    "ghrp-2": ["pralmorelin", "growth hormone releasing peptide 2"],
    "ghrp-6": ["growth hormone releasing peptide 6", "GHRP6"],
    "hexarelin": ["examorelin", "hexarelin"],
    "mots-c": ["MOTS-c peptide", "mitochondrial ORF of the 12S rRNA type-c"],
    "5-amino-1mq": ["5-amino-1-methylquinolinium"],
    "adamax": ["adamax peptide"],
    "adipotide": ["CKGGRAKDC-GG-D(KLAKLAK)2", "prohibitin-targeting peptide"],
    "ahk-cu": ["copper tripeptide AHK"],
    "aicar": ["aminoimidazole carboxamide ribonucleotide", "acadesine"],
    "ara-290": ["cibinetide"],
    "argireline": ["acetyl hexapeptide-3", "acetyl hexapeptide-8"],
    "bpc-157-tb-500-blend": ["BPC-157"],
    "bronchogen": ["bronchogen peptide"],
    "cardiogen": ["cardiogen peptide"],
    "cartalax": ["cartalax peptide"],
    "cerebrolysin": ["cerebrolysin"],
    "chonluten": ["chonluten peptide"],
    "cortagen": ["cortagen peptide"],
    "decapeptide-12": ["decapeptide-12"],
    "dermorphin": ["dermorphin"],
    "dihexa": ["dihexa", "N-hexanoic-Tyr-Ile-(6)-aminohexanoic amide"],
    "ds5": ["DS-5 peptide"],
    "dulaglutide": ["dulaglutide"],
    "enclomiphene": ["enclomiphene", "enclomifene"],
    "follistatin": ["follistatin"],
    "follistatin-315": ["follistatin 315"],
    "follistatin-344": ["follistatin 344"],
    "foxo4-dri": ["FOXO4-DRI peptide"],
    "ghk": ["glycyl-histidyl-lysine", "GHK peptide"],
    "glutathione": ["glutathione", "L-glutathione"],
    "gonadorelin": ["gonadorelin", "GnRH"],
    "hgh-fragment-176-191": ["HGH fragment 176-191", "AOD9604"],
    "humanin": ["humanin peptide"],
    "igf-1-des": ["des(1-3)IGF-1"],
    "igf-1-lr3": ["IGF-1 LR3", "long R3 IGF-1"],
    "kisspeptin-10": ["kisspeptin-10", "metastin 45-54"],
    "kpv": ["alpha-MSH 11-13", "KPV tripeptide"],
    "livagen": ["livagen peptide"],
    "ll-37": ["cathelicidin", "LL-37 peptide"],
    "matrixyl": ["palmitoyl pentapeptide-4", "palmitoyl pentapeptide"],
    "mt-1": ["melanotan I", "afamelanotide"],
    "melanotan-ii": ["melanotan II", "melanotan 2"],
    "mgf": ["mechano growth factor", "MGF peptide"],
    "mk-677": ["ibutamoren", "MK-0677"],
    "mots-c": ["MOTS-c"],
    "nad-plus": ["nicotinamide adenine dinucleotide", "NAD"],
    "nonapeptide-1": ["nonapeptide-1", "melanostatin-5"],
    "ovagen": ["ovagen peptide"],
    "oxytocin": ["oxytocin"],
    "p21": ["P21 peptide", "CNTF-derived peptide"],
    "pal-ahk": ["palmitoyl tripeptide-3"],
    "pal-ghk": ["palmitoyl tripeptide-1"],
    "palmitoyl-dipeptide-6": ["palmitoyl dipeptide-6"],
    "pancragen": ["pancragen peptide"],
    "pe-22-28": ["PE-22-28 peptide", "spadin analog"],
    "peg-mgf": ["PEGylated mechano growth factor"],
    "pentapeptide-18": ["leuphasyl", "pentapeptide-18"],
    "pgpipn": ["casomorphin fragment"],
    "pinealon": ["pinealon peptide", "EDR peptide"],
    "pnc-27": ["PNC-27 peptide"],
    "prostamax": ["prostamax peptide"],
    "rigin": ["rigin peptide"],
    "slu-pp-322": ["SLU-PP-332"],
    "snap-8": ["acetyl octapeptide-3"],
    "somatropin": ["somatotropin", "human growth hormone"],
    "syn-ake": ["dipeptide diaminobutyroyl benzylamide diacetate"],
    "syn-coll": ["palmitoyl tripeptide-5"],
    "tesofensine": ["tesofensine", "NS2330"],
    "testagen": ["testagen peptide"],
    "thymagen": ["thymagen peptide"],
    "thymalin": ["thymalin", "thymic peptide"],
    "tripeptide-29": ["collagen tripeptide", "GHK tripeptide"],
    "triptorelin": ["triptorelin", "triptorelin acetate"],
    "vesilute": ["vesilute peptide"],
    "vesugen": ["vesugen peptide", "KED peptide"],
    "vialox": ["pentapeptide-3"],
    "vilon": ["vilon peptide", "KE dipeptide"],
    "vip": ["vasoactive intestinal peptide"],
    "cagrilintide-semaglutide": ["CagriSema"],
}


def pubchem_name_lookup(name: str) -> int:
    """Try exact name lookup on PubChem."""
    encoded = urllib.parse.quote(name)
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/JSON"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NanoClaw-CIDFix/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data["PC_Compounds"][0]["id"]["id"]["cid"]
    except Exception:
        return 0


def pubchem_autocomplete(name: str) -> int:
    """Try PubChem autocomplete API as fallback."""
    encoded = urllib.parse.quote(name)
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/autocomplete/compound/{encoded}/JSON?limit=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NanoClaw-CIDFix/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            match = data.get("dictionary_terms", {}).get("compound", [])
            if match:
                # Now look up the matched name
                return pubchem_name_lookup(match[0])
    except Exception:
        pass
    return 0


def try_resolve_cid(compound_id: str, name: str) -> tuple[int, list[str]]:
    """Try multiple strategies to resolve a PubChem CID."""
    new_aliases = []

    # Strategy 1: Strip parenthetical — "PT-141 (Bremelanotide)" → "Bremelanotide"
    paren_match = re.search(r'\(([^)]+)\)', name)
    if paren_match:
        inner = paren_match.group(1)
        cid = pubchem_name_lookup(inner)
        if cid:
            new_aliases.append(inner)
            return cid, new_aliases
        time.sleep(0.3)

    # Strategy 2: Try manual alt names
    alts = ALT_NAMES.get(compound_id, [])
    for alt in alts:
        cid = pubchem_name_lookup(alt)
        if cid:
            if alt.lower() != name.lower():
                new_aliases.append(alt)
            return cid, new_aliases
        time.sleep(0.3)

    # Strategy 3: Autocomplete with cleaned name
    clean = re.sub(r'\s*\([^)]*\)', '', name).strip()
    cid = pubchem_autocomplete(clean)
    if cid:
        return cid, new_aliases
    time.sleep(0.3)

    # Strategy 4: Try just the first word if it's a multi-word name
    words = clean.split()
    if len(words) > 1:
        cid = pubchem_name_lookup(words[0])
        if cid:
            return cid, new_aliases

    return 0, new_aliases


def main():
    with open(COMPOUNDS_FILE) as f:
        data = json.load(f)

    missing = [(i, c) for i, c in enumerate(data["compounds"]) if c["pubchem_cid"] == 0]
    print(f"Compounds missing CID: {len(missing)}/{len(data['compounds'])}")

    fixed = 0
    still_missing = []

    for idx, compound in missing:
        cid, new_aliases = try_resolve_cid(compound["id"], compound["name"])
        if cid:
            data["compounds"][idx]["pubchem_cid"] = cid
            # Merge new aliases
            existing = set(a.lower() for a in compound.get("aliases", []))
            for alias in new_aliases:
                if alias.lower() not in existing:
                    data["compounds"][idx].setdefault("aliases", []).append(alias)
            fixed += 1
            print(f"  ✓ {compound['name']} → CID:{cid}")
        else:
            still_missing.append(compound["name"])
            print(f"  ✗ {compound['name']} — not found")
        time.sleep(0.3)

    # Write back
    with open(COMPOUNDS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nFixed: {fixed}/{len(missing)}")
    print(f"Still missing: {len(still_missing)}")
    if still_missing:
        print(f"  {still_missing}")


if __name__ == "__main__":
    main()
