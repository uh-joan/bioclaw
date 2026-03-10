---
name: lab-data-standardization
description: Laboratory instrument data standardization using the Allotrope Simple Model (ASM). Converts raw instrument output from 65+ analytical techniques and 40+ device types into standardized ASM JSON. Covers cell counting, spectrophotometry, plate readers, qPCR, chromatography, electrophoresis, flow cytometry instruments. Implements three-tier conversion (native allotropy, pandas fallback, PDF extraction), raw vs calculated data separation, metadata provenance, and JSON-to-CSV flattening. Use when user mentions Allotrope, ASM, instrument data, lab data conversion, lab data standardization, instrument output parsing, analytical data, LIMS integration, cell counter data, plate reader data, qPCR data, chromatography data, spectrophotometer data, NanoDrop, QuantStudio, SoftMax Pro, Empower, TapeStation, FACSDiva, or converting instrument files to standard format.
---

# Lab Data Standardization (Allotrope Simple Model)

Standardize laboratory instrument data from proprietary vendor formats into the Allotrope Simple Model (ASM), the open JSON-LD schema for analytical data exchange. This skill covers 65+ analytical techniques, 40+ instrument types, three conversion strategies, regulatory-compliant metadata, and downstream LIMS/database integration.

The Allotrope Foundation defines ASM as a lightweight JSON format that captures instrument data with full provenance. Each ASM document has three layers: **manifest** (what was done), **data** (what was measured), and **metadata** (context and traceability). The schema separates raw measurements from calculated results — a critical distinction for GxP regulatory compliance.

## Report-First Workflow

1. **Create report file immediately**: `lab_data_standardization_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Converting...]`
3. **Populate progressively**: Update sections as data is parsed and validated
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Converting...]` placeholders remain

## When NOT to Use This Skill

- FHIR-based healthcare data exchange -> use `fhir-developer`
- Clinical trial data standardization (CDISC/SDTM) -> handle directly with CDISC tooling
- Electronic lab notebook (ELN) workflows -> handle directly
- Statistical analysis of lab data -> use `statistical-modeling`
- Experimental design for lab studies -> use `experimental-design`

---

## ASM Schema Architecture

### Three-Layer Structure

```
ASM Document
├── manifest (required)
│   ├── vocabulary: ["http://purl.allotrope.org/ontologies/..."]
│   └── description of analytical session
│
├── data-system-document (required)
│   ├── data-processing-document
│   │   ├── software name & version (converter identity)
│   │   └── library versions (allotropy, pandas, etc.)
│   └── file-information (original file hash, timestamps)
│
├── device-system-document (required for instrument data)
│   ├── device-identifier (serial number, asset tag)
│   ├── model-number
│   ├── brand-name (manufacturer)
│   └── firmware-version
│
├── measurement-aggregate-document (the actual data)
│   ├── measurement-document[] (array of individual measurements)
│   │   ├── measurement-identifier
│   │   ├── measurement-time
│   │   ├── sample-document (sample identity)
│   │   ├── device-control-document (instrument settings)
│   │   └── measured values (technique-specific)
│   │
│   └── calculated-data-aggregate-document (derived values)
│       └── calculated-data-document[]
│           ├── calculated-data-identifier
│           ├── calculation-description
│           ├── data-source-aggregate-document (links to raw)
│           └── calculated values
│
└── metadata (optional)
    ├── analyst
    ├── experiment-type
    └── custom fields
```

### Key Design Principles

| Principle | Implementation | Why It Matters |
|-----------|---------------|----------------|
| **Raw/calculated separation** | Raw in `measurement-document`, derived in `calculated-data-document` | GxP compliance: auditors need to trace calculations to source |
| **Data source traceability** | `data-source-aggregate-document` links calculated to raw | Reproducibility: know exactly which measurements produced a result |
| **Device provenance** | `device-system-document` with serial, model, firmware | Instrument qualification: tie data to specific calibrated hardware |
| **Converter provenance** | `data-system-document` with software/library versions | Reproducibility: same input + same converter = same output |
| **File integrity** | SHA-256 hash of original file | Data integrity: detect tampering or corruption |
| **Vocabulary control** | Allotrope ontology URIs for all field names | Interoperability: unambiguous field semantics across systems |

---

## Supported Analytical Techniques (65+)

### Technique Categories

| Category | Techniques | Common Outputs |
|----------|-----------|----------------|
| **Spectrophotometry** | UV-Vis, absorbance, fluorescence, luminescence | Spectra, single-point readings, concentration |
| **Chromatography** | HPLC, UPLC, GC, IC, SEC | Chromatograms, peak tables, retention times |
| **Mass Spectrometry** | LC-MS, GC-MS, MALDI, ESI | Mass spectra, MRM transitions, quantitation |
| **Plate Reading** | Absorbance, fluorescence, luminescence, AlphaLISA | Well-level readings, dose-response curves |
| **qPCR / dPCR** | Real-time PCR, digital PCR | Amplification curves, Ct/Cq values, copies/uL |
| **Cell Counting** | Automated cell counting, viability | Total cells, viable cells, viability %, diameter |
| **Electrophoresis** | Capillary electrophoresis, gel electrophoresis | Electropherograms, fragment sizes, purity % |
| **Flow Cytometry** | Immunophenotyping, cell sorting | Event counts, population percentages, MFI |
| **Cell Imaging** | High-content screening, colony counting | Object counts, morphology metrics |
| **Bioanalysis** | ELISA, MSD, Gyros, BLI, SPR | Concentrations, binding kinetics, EC50 |
| **Physical Properties** | pH, osmolality, viscosity, particle size | Direct measurements |

---

## Instrument Categories and Devices (40+)

### Cell Counting Instruments

| Instrument | Manufacturer | Native Format | ASM Technique |
|-----------|-------------|---------------|---------------|
| **Vi-CELL BLU** | Beckman Coulter | CSV, Excel | cell-counting |
| **Vi-CELL XR** | Beckman Coulter | CSV | cell-counting |
| **NucleoCounter NC-200** | ChemoMetec | CSV | cell-counting |
| **NucleoCounter NC-202** | ChemoMetec | CSV | cell-counting |
| **Cellaca MX** | Revvity (Nexcelom) | CSV, Excel | cell-counting |
| **Cellometer Auto 2000** | Revvity (Nexcelom) | CSV | cell-counting |
| **TC20** | Bio-Rad | CSV | cell-counting |
| **Countess 3** | Thermo Fisher | CSV, Excel | cell-counting |

**Cell counting ASM fields**:
```json
{
  "measurement-document": {
    "sample-document": {
      "sample-identifier": "Sample-001",
      "batch-identifier": "Batch-2024-03",
      "well-location-identifier": "A1"
    },
    "total-cell-count": {"value": 2500000, "unit": "cell"},
    "viable-cell-count": {"value": 2375000, "unit": "cell"},
    "cell-viability": {"value": 95.0, "unit": "%"},
    "average-cell-diameter": {"value": 12.5, "unit": "um"},
    "viable-cell-density": {"value": 2.5e6, "unit": "cell/mL"},
    "total-cell-density": {"value": 2.63e6, "unit": "cell/mL"}
  },
  "calculated-data-document": {
    "calculated-data-identifier": "doubling-time-001",
    "calculation-description": "Population doubling time from growth curve",
    "calculated-result": {"value": 24.5, "unit": "h"},
    "data-source-aggregate-document": {
      "data-source-document": [
        {"data-source-identifier": "measurement-001"},
        {"data-source-identifier": "measurement-002"}
      ]
    }
  }
}
```

### Spectrophotometry Instruments

| Instrument | Manufacturer | Native Format | ASM Technique |
|-----------|-------------|---------------|---------------|
| **NanoDrop One/Eight** | Thermo Fisher | TSV, CSV | ultraviolet-absorbance |
| **Lunatic** | Unchained Labs | CSV, Excel | ultraviolet-absorbance |
| **Stunner** | Unchained Labs | CSV | ultraviolet-absorbance, DLS |
| **SoloVPE** | C Technologies | CSV | ultraviolet-absorbance |
| **Agilent 8453** | Agilent | CSV | ultraviolet-absorbance |

**Spectrophotometry ASM fields**:
```json
{
  "measurement-document": {
    "sample-document": {"sample-identifier": "Protein-Sample-A"},
    "device-control-document": {
      "detector-wavelength-setting": {"value": 280, "unit": "nm"}
    },
    "absorbance": {"value": 0.542, "unit": "mAU"},
    "mass-concentration": {"value": 1.23, "unit": "mg/mL"},
    "a260-a280-ratio": {"value": 0.56},
    "path-length": {"value": 0.5, "unit": "mm"}
  }
}
```

### Plate Reader Instruments

| Instrument | Manufacturer | Software | Native Format |
|-----------|-------------|----------|---------------|
| **SpectraMax** series | Molecular Devices | SoftMax Pro | TXT, XML |
| **EnSight** | Revvity | Kaleido | CSV, Excel |
| **Spark** | Tecan | SparkControl | Excel, CSV |
| **CLARIOstar** | BMG Labtech | MARS | CSV, Excel |
| **Synergy H1/Neo2** | Agilent (BioTek) | Gen5 | CSV, Excel |
| **Victor Nivo** | Revvity | PerkinElmer | CSV |
| **Infinite** series | Tecan | iControl/Magellan | Excel, CSV |

**Plate reader ASM fields**:
```json
{
  "measurement-aggregate-document": {
    "plate-well-count": {"value": 96},
    "measurement-document": [
      {
        "well-location-identifier": "A1",
        "sample-document": {"sample-identifier": "Standard-1", "sample-role-type": "standard-sample-role"},
        "device-control-document": {
          "detector-wavelength-setting": {"value": 450, "unit": "nm"},
          "detector-bandwidth-setting": {"value": 9, "unit": "nm"},
          "number-of-flashes-setting": {"value": 25}
        },
        "absorbance": {"value": 0.123, "unit": "mAU"},
        "compartment-temperature": {"value": 25.0, "unit": "degC"}
      }
    ],
    "calculated-data-aggregate-document": {
      "calculated-data-document": [
        {
          "calculated-data-identifier": "ec50-calc-001",
          "calculation-description": "Four-parameter logistic EC50 from dose-response",
          "calculated-result": {"value": 2.34, "unit": "nM"},
          "data-source-aggregate-document": {
            "data-source-document": [
              {"data-source-identifier": "A1", "data-source-feature": "absorbance"},
              {"data-source-identifier": "A2", "data-source-feature": "absorbance"},
              {"data-source-identifier": "A3", "data-source-feature": "absorbance"}
            ]
          }
        }
      ]
    }
  }
}
```

### qPCR Instruments

| Instrument | Manufacturer | Software | Native Format |
|-----------|-------------|----------|---------------|
| **QuantStudio 5/6/7** | Thermo Fisher (Applied Biosystems) | Design & Analysis | Excel, CSV, EDS |
| **CFX96/384** | Bio-Rad | CFX Manager | CSV, Excel |
| **LightCycler 480/96** | Roche | LightCycler Software | TXT, XML |
| **Rotor-Gene Q** | QIAGEN | Rotor-Gene Q Software | CSV |
| **ViiA 7** | Thermo Fisher | QuantStudio | Excel, CSV |

**qPCR ASM fields**:
```json
{
  "measurement-document": {
    "sample-document": {
      "sample-identifier": "Unknown-1",
      "sample-role-type": "unknown-sample-role",
      "target-dna-description": "GAPDH"
    },
    "device-control-document": {
      "reporter-dye-setting": "FAM",
      "quencher-dye-setting": "TAMRA",
      "passive-reference-dye-setting": "ROX"
    },
    "cycle-threshold-result": {"value": 18.5, "unit": "cycle"},
    "cycle-threshold-value-setting": {"value": 0.2},
    "automatic-cycle-threshold-enabled-setting": false,
    "baseline-determination-start-cycle-setting": {"value": 3},
    "baseline-determination-end-cycle-setting": {"value": 15},
    "amplification-data-aggregate-document": {
      "amplification-data-document": [
        {"cycle-count": 1, "fluorescence": {"value": 12345.6, "unit": "RFU"}},
        {"cycle-count": 2, "fluorescence": {"value": 12389.2, "unit": "RFU"}}
      ]
    }
  },
  "calculated-data-document": {
    "calculated-data-identifier": "relative-quantity-001",
    "calculation-description": "Delta-delta Ct relative quantification",
    "calculated-result": {"value": 2.34, "unit": "(unitless)"},
    "data-source-aggregate-document": {
      "data-source-document": [
        {"data-source-identifier": "target-ct", "data-source-feature": "cycle-threshold-result"},
        {"data-source-identifier": "reference-ct", "data-source-feature": "cycle-threshold-result"}
      ]
    }
  }
}
```

### Chromatography Instruments

| Instrument/Software | Manufacturer | Native Format |
|---------------------|-------------|---------------|
| **Empower** | Waters | Channel export (CSV, TXT) |
| **Chromeleon** | Thermo Fisher (Dionex) | CDS export (CSV) |
| **OpenLab CDS** | Agilent | CSV, ChemStation formats |
| **LabSolutions** | Shimadzu | ASCII, CSV |
| **Unicorn** | Cytiva | CSV (AKTA systems) |

**Chromatography ASM fields**:
```json
{
  "measurement-document": {
    "sample-document": {"sample-identifier": "QC-Standard-1", "injection-volume": {"value": 10, "unit": "uL"}},
    "device-control-document": {
      "column-description": "Waters XBridge C18, 4.6x150mm, 3.5um",
      "detector-wavelength-setting": {"value": 214, "unit": "nm"},
      "flow-rate-setting": {"value": 1.0, "unit": "mL/min"}
    },
    "chromatogram-data-aggregate-document": {
      "chromatogram-data-document": [
        {"retention-time": {"value": 0.5, "unit": "min"}, "absorbance": {"value": 0.002, "unit": "AU"}},
        {"retention-time": {"value": 1.0, "unit": "min"}, "absorbance": {"value": 0.015, "unit": "AU"}}
      ]
    },
    "peak-list-aggregate-document": {
      "peak-list-document": [
        {
          "peak-identifier": "1",
          "peak-name": "Main Peak",
          "retention-time": {"value": 5.23, "unit": "min"},
          "peak-area": {"value": 1234567, "unit": "mAU*min"},
          "peak-height": {"value": 45678, "unit": "mAU"},
          "relative-peak-area": {"value": 98.5, "unit": "%"},
          "peak-width-at-half-height": {"value": 0.12, "unit": "min"},
          "number-of-theoretical-plates": {"value": 12500}
        }
      ]
    }
  }
}
```

### Electrophoresis Instruments

| Instrument | Manufacturer | Software | Native Format |
|-----------|-------------|----------|---------------|
| **TapeStation 4150/4200** | Agilent | TapeStation Analysis | CSV, PDF |
| **LabChip GX/GXII** | Revvity | LabChip GX Software | CSV |
| **Bioanalyzer 2100** | Agilent | 2100 Expert | CSV |
| **Fragment Analyzer** | Agilent | ProSize | CSV |
| **QIAxcel** | QIAGEN | QIAxcel ScreenGel | CSV |

### Flow Cytometry Instruments

| Instrument | Manufacturer | Software | Native Format |
|-----------|-------------|----------|---------------|
| **FACSCanto II** | BD Biosciences | FACSDiva | FCS, CSV |
| **FACSymphony** | BD Biosciences | FACSDiva | FCS, CSV |
| **CytoFLEX** | Beckman Coulter | CytExpert | FCS, CSV |
| **Attune NxT** | Thermo Fisher | Attune Software | FCS, CSV |
| **ID7000** | Sony | ID7000 Software | FCS, CSV |
| N/A (analysis) | FlowJo | FlowJo | CSV, Excel |

---

## Three-Tier Conversion Strategy

### Decision Tree

```
Input file received
│
├── Is there a native allotropy parser for this instrument?
│   ├── YES -> Tier 1: Native allotropy parsing
│   │   └── Highest fidelity, vendor-specific field mapping
│   │
│   └── NO -> Is the file CSV, Excel, or TXT?
│       ├── YES -> Tier 2: Pandas-based flexible parsing
│       │   └── Auto-detect format, column mapping, manual field assignment
│       │
│       └── NO -> Is the file PDF?
│           ├── YES -> Tier 3: PDF extraction
│           │   └── pdfplumber table/text extraction, regex parsing
│           │
│           └── NO -> Unsupported format (request raw data export)
```

### Tier 1: Native Allotropy Library Parsing

The `allotropy` Python library provides vendor-specific parsers that map instrument output directly to ASM.

```python
from allotropy.parser_factory import Vendor
from allotropy.to_allotrope import allotrope_from_file

# Parse instrument file using vendor-specific parser
asm_result = allotrope_from_file(
    file_path="data/vicell_blu_export.csv",
    vendor_type=Vendor.BECKMAN_VI_CELL_BLU
)

# Result is a dict conforming to ASM schema
import json
with open("output/vicell_asm.json", "w") as f:
    json.dump(asm_result, f, indent=2, default=str)
```

**Supported vendors in allotropy library** (check latest version for updates):

| Vendor Enum | Instrument | File Types |
|------------|-----------|-----------|
| `Vendor.BECKMAN_VI_CELL_BLU` | Vi-CELL BLU | CSV |
| `Vendor.BECKMAN_VI_CELL_XR` | Vi-CELL XR | CSV |
| `Vendor.CHEMOMETEC_NUCLEOVIEW` | NucleoCounter | CSV |
| `Vendor.REVVITY_KALEIDO` | EnSight plate reader | CSV |
| `Vendor.MOLECULAR_DEVICES_SOFTMAX_PRO` | SoftMax Pro | TXT |
| `Vendor.THERMO_FISHER_NANODROP_EIGHT` | NanoDrop Eight | TSV |
| `Vendor.UNCHAINED_LABS_LUNATIC` | Lunatic | CSV |
| `Vendor.THERMO_FISHER_QUANT_STUDIO` | QuantStudio qPCR | Excel |
| `Vendor.BIORAD_BIOPLEX_MANAGER` | BioPlex Manager | CSV |
| `Vendor.AGILENT_TAPESTATION_ANALYSIS` | TapeStation | CSV |
| `Vendor.ROCHE_CEDEX_BIOHT` | Cedex Bio HT | CSV |
| `Vendor.BMG_MARS` | CLARIOstar reader | CSV |
| `Vendor.MESO_SCALE_DISCOVERY` | MSD ELISA | Excel |
| `Vendor.NOVABIO_FLEX2` | NovaBio Flex2 | CSV |
| `Vendor.TECAN_SPARK` | Spark plate reader | Excel |
| `Vendor.PERKIN_ELMER_ENVISION` | EnVision reader | CSV |
| `Vendor.AGILENT_GEN5` | BioTek Gen5 reader | CSV |

**Error handling**:
```python
from allotropy.exceptions import AllotropeConversionError

try:
    asm_result = allotrope_from_file(file_path, vendor_type)
except AllotropeConversionError as e:
    print(f"Conversion failed: {e}")
    print("Falling back to Tier 2 pandas parsing")
    # -> Tier 2
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Unexpected error: {e}")
    # -> Tier 2
```

### Tier 2: Flexible Pandas-Based Fallback

When no native parser exists, parse the file with pandas and map columns to ASM fields manually.

```python
import pandas as pd
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

def parse_generic_instrument_file(file_path: str, config: dict) -> dict:
    """
    Generic instrument file parser using pandas.

    config = {
        "technique": "cell-counting",
        "manufacturer": "Example Instruments",
        "model": "Counter 3000",
        "column_map": {
            "Sample ID": "sample-identifier",
            "Total Cells": "total-cell-count",
            "Viable Cells": "viable-cell-count",
            "Viability %": "cell-viability",
            "Date": "measurement-time"
        },
        "unit_map": {
            "total-cell-count": "cell",
            "viable-cell-count": "cell",
            "cell-viability": "%"
        },
        "skip_rows": 0,
        "sheet_name": 0
    }
    """
    path = Path(file_path)

    # Auto-detect format
    if path.suffix.lower() in ('.xlsx', '.xls'):
        df = pd.read_excel(file_path, sheet_name=config.get("sheet_name", 0),
                          skiprows=config.get("skip_rows", 0))
    elif path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path, skiprows=config.get("skip_rows", 0))
    elif path.suffix.lower() == '.tsv':
        df = pd.read_csv(file_path, sep='\t', skiprows=config.get("skip_rows", 0))
    elif path.suffix.lower() == '.txt':
        # Try common delimiters
        for sep in ['\t', ',', ';', '|']:
            try:
                df = pd.read_csv(file_path, sep=sep, skiprows=config.get("skip_rows", 0))
                if len(df.columns) > 1:
                    break
            except Exception:
                continue
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    # Compute file hash for provenance
    file_hash = hashlib.sha256(path.read_bytes()).hexdigest()

    # Build ASM document
    column_map = config["column_map"]
    unit_map = config.get("unit_map", {})

    measurements = []
    for _, row in df.iterrows():
        measurement = {
            "measurement-identifier": f"meas-{len(measurements)+1:04d}",
            "sample-document": {},
            "device-control-document": {}
        }

        for source_col, asm_field in column_map.items():
            if source_col not in df.columns:
                continue
            value = row[source_col]
            if pd.isna(value):
                continue

            if asm_field == "sample-identifier":
                measurement["sample-document"]["sample-identifier"] = str(value)
            elif asm_field == "measurement-time":
                measurement["measurement-time"] = str(value)
            elif asm_field in unit_map:
                measurement[asm_field] = {
                    "value": float(value),
                    "unit": unit_map[asm_field]
                }
            else:
                measurement[asm_field] = value

        measurements.append(measurement)

    asm_document = {
        "$asm.manifest": {
            "vocabulary": ["http://purl.allotrope.org/ontologies/result"],
            "technique": config["technique"]
        },
        "data-system-document": {
            "data-processing-document": {
                "software-name": "custom-pandas-converter",
                "software-version": "1.0.0",
                "library-versions": {
                    "pandas": pd.__version__,
                    "python": "3.11"
                }
            },
            "file-information": {
                "original-file-name": path.name,
                "original-file-hash": f"sha256:{file_hash}",
                "conversion-timestamp": datetime.now(timezone.utc).isoformat()
            }
        },
        "device-system-document": {
            "brand-name": config["manufacturer"],
            "model-number": config["model"],
            "device-identifier": config.get("serial_number", "UNKNOWN")
        },
        "measurement-aggregate-document": {
            "measurement-document": measurements
        }
    }

    return asm_document
```

**Format auto-detection heuristics**:

| File Extension | Detection Strategy |
|---------------|-------------------|
| `.csv` | Read with comma separator, check column count |
| `.tsv` | Read with tab separator |
| `.txt` | Try tab, comma, semicolon, pipe in order; keep first with >1 column |
| `.xlsx` / `.xls` | Use openpyxl/xlrd; check for multiple sheets, header row location |
| `.xml` | Parse with ElementTree, look for known instrument XML schemas |

**Column mapping strategy**:
1. Check for exact column name match against known instrument patterns
2. Fuzzy match column headers against ASM field names
3. Ask user to provide explicit column mapping if automated detection fails
4. Store mapping configuration for future files from the same instrument

### Tier 3: PDF Extraction

For legacy instruments that only produce PDF reports.

```python
import pdfplumber
import re
from typing import Optional

def extract_from_pdf(file_path: str, extraction_config: dict) -> dict:
    """
    Extract structured data from instrument PDF reports.

    extraction_config = {
        "table_pages": [0, 1],           # Pages with data tables
        "table_settings": {               # pdfplumber table extraction settings
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines"
        },
        "regex_patterns": {               # For text-based extraction
            "sample_id": r"Sample:\s*(\S+)",
            "result_value": r"Result:\s*([\d.]+)\s*(\S+)",
            "date": r"Date:\s*(\d{4}-\d{2}-\d{2})"
        }
    }
    """
    measurements = []

    with pdfplumber.open(file_path) as pdf:
        # Table extraction
        for page_num in extraction_config.get("table_pages", range(len(pdf.pages))):
            if page_num >= len(pdf.pages):
                continue
            page = pdf.pages[page_num]

            tables = page.extract_tables(
                table_settings=extraction_config.get("table_settings", {})
            )

            for table in tables:
                if not table or len(table) < 2:
                    continue
                headers = [str(h).strip() if h else "" for h in table[0]]
                for row in table[1:]:
                    if all(cell is None or str(cell).strip() == "" for cell in row):
                        continue
                    row_data = {}
                    for i, cell in enumerate(row):
                        if i < len(headers) and headers[i] and cell:
                            row_data[headers[i]] = str(cell).strip()
                    if row_data:
                        measurements.append(row_data)

        # Text-based regex extraction (fallback for non-tabular PDFs)
        if not measurements:
            full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            patterns = extraction_config.get("regex_patterns", {})

            for field_name, pattern in patterns.items():
                matches = re.findall(pattern, full_text)
                for match in matches:
                    # Build measurement entries from regex matches
                    pass

    return measurements


def pdf_to_asm(file_path: str, config: dict) -> dict:
    """Convert PDF extraction results to ASM format."""
    raw_data = extract_from_pdf(file_path, config)

    # Map extracted data to ASM fields using column_map
    # Same pattern as Tier 2, but with PDF-extracted data
    # ...

    asm_document = {
        "$asm.manifest": {"technique": config["technique"]},
        "data-system-document": {
            "data-processing-document": {
                "software-name": "pdf-extractor",
                "extraction-method": "pdfplumber-table",
                "confidence-note": "PDF extraction may have lower fidelity than native formats"
            }
        },
        # ... rest of ASM structure
    }
    return asm_document
```

**PDF extraction quality checklist**:
- [ ] Tables extracted with correct row/column alignment
- [ ] Numeric values parsed correctly (decimal separators, scientific notation)
- [ ] Units captured alongside values
- [ ] Sample identifiers extracted without truncation
- [ ] Date/time formats parsed correctly
- [ ] Multi-page tables merged correctly
- [ ] Headers vs data rows distinguished accurately

---

## Raw vs Calculated Data Separation

This is the most critical aspect of ASM for regulated environments.

### Decision Tree: Where Does This Field Belong?

```
Is this value directly read from the instrument detector?
│
├── YES -> measurement-document (raw data)
│   Examples:
│   - Absorbance reading at 450nm
│   - Fluorescence intensity (RFU)
│   - Ct value from amplification curve
│   - Cell count from image analysis
│   - Peak area from integration
│   - Retention time
│
└── NO -> Was this value computed from one or more raw values?
    │
    ├── YES -> calculated-data-document (calculated data)
    │   Examples:
    │   - Concentration from standard curve interpolation
    │   - Viability % (viable / total * 100)
    │   - Delta-delta Ct relative quantification
    │   - EC50 from dose-response fit
    │   - Purity % from peak area ratios
    │   - Titer from dilution series
    │   MUST include: data-source-aggregate-document linking to raw measurements
    │
    └── NO -> Is this a device setting or sample property?
        │
        ├── Device setting -> device-control-document
        │   Examples: wavelength, temperature, flow rate, gain
        │
        └── Sample property -> sample-document
            Examples: sample ID, well position, dilution factor
```

### Worked Example: Plate Reader ELISA

```
Raw (measurement-document):
  Well A1: absorbance = 0.052 AU (blank)
  Well A2: absorbance = 0.123 AU (standard 1)
  Well A3: absorbance = 0.345 AU (standard 2)
  Well A4: absorbance = 0.789 AU (standard 3)
  Well B1: absorbance = 0.456 AU (unknown 1)
  Well B2: absorbance = 0.234 AU (unknown 2)

Calculated (calculated-data-document):
  Standard curve R^2 = 0.998
    -> data-source: A2, A3, A4 absorbance values
  Unknown 1 concentration = 45.2 ng/mL
    -> data-source: B1 absorbance + standard curve
  Unknown 2 concentration = 18.7 ng/mL
    -> data-source: B2 absorbance + standard curve
```

---

## Mandatory Metadata

### Data System Document (Converter Provenance)

Every ASM document MUST include converter information:

```json
{
  "data-system-document": {
    "data-processing-document": {
      "software-name": "custom-lab-converter",
      "software-version": "2.1.0",
      "library-versions": {
        "allotropy": "0.1.50",
        "pandas": "2.2.0",
        "pdfplumber": "0.11.0",
        "openpyxl": "3.1.2",
        "python": "3.11.7"
      }
    },
    "file-information": {
      "original-file-name": "20240315_vicell_run.csv",
      "original-file-path": "/data/raw/cell_counting/",
      "original-file-hash": "sha256:a3f2b8c9d4e5f6...",
      "original-file-size-bytes": 45678,
      "conversion-timestamp": "2024-03-15T14:30:00Z",
      "conversion-duration-seconds": 1.2
    }
  }
}
```

### Device System Document (Hardware Provenance)

Every ASM document MUST include instrument identification:

```json
{
  "device-system-document": {
    "brand-name": "Beckman Coulter",
    "model-number": "Vi-CELL BLU",
    "device-identifier": "SN-VCB-2024-001",
    "firmware-version": "3.0.12",
    "equipment-serial-number": "VCB-2024-001",
    "asset-management-identifier": "EQ-LAB3-042",
    "device-calibration-status": "qualified",
    "last-calibration-date": "2024-02-15",
    "calibration-due-date": "2024-08-15"
  }
}
```

---

## JSON-to-CSV Flattening

Convert hierarchical ASM JSON to flat CSV for LIMS/database integration.

```python
import pandas as pd
import json
from typing import Any

def flatten_asm_to_csv(asm_document: dict, output_path: str) -> pd.DataFrame:
    """
    Flatten ASM JSON document to tabular CSV format for LIMS import.

    Flattening strategy:
    - One row per measurement
    - Nested objects become dot-separated column names
    - Quantity objects expand to {field}_value and {field}_unit columns
    - Array data (chromatograms, amplification curves) go to separate files
    """
    measurements = (
        asm_document
        .get("measurement-aggregate-document", {})
        .get("measurement-document", [])
    )

    # Device info (same for all rows)
    device = asm_document.get("device-system-document", {})
    device_flat = {
        "device.brand": device.get("brand-name", ""),
        "device.model": device.get("model-number", ""),
        "device.serial": device.get("device-identifier", "")
    }

    rows = []
    for meas in measurements:
        row = dict(device_flat)  # Copy device info
        row["measurement_id"] = meas.get("measurement-identifier", "")
        row["measurement_time"] = meas.get("measurement-time", "")

        # Sample info
        sample = meas.get("sample-document", {})
        row["sample_id"] = sample.get("sample-identifier", "")
        row["well_location"] = sample.get("well-location-identifier", "")
        row["sample_role"] = sample.get("sample-role-type", "")

        # Flatten quantity fields
        for key, value in meas.items():
            if isinstance(value, dict) and "value" in value and "unit" in value:
                clean_key = key.replace("-", "_")
                row[f"{clean_key}_value"] = value["value"]
                row[f"{clean_key}_unit"] = value["unit"]
            elif key not in ("sample-document", "device-control-document",
                           "measurement-identifier", "measurement-time"):
                if not isinstance(value, (dict, list)):
                    row[key.replace("-", "_")] = value

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)

    # Also flatten calculated data to a separate CSV
    calculated = (
        asm_document
        .get("measurement-aggregate-document", {})
        .get("calculated-data-aggregate-document", {})
        .get("calculated-data-document", [])
    )

    if calculated:
        calc_rows = []
        for calc in calculated:
            calc_row = {
                "calculated_data_id": calc.get("calculated-data-identifier", ""),
                "calculation_description": calc.get("calculation-description", ""),
            }
            result = calc.get("calculated-result", {})
            if isinstance(result, dict):
                calc_row["result_value"] = result.get("value")
                calc_row["result_unit"] = result.get("unit", "")

            # Data sources
            sources = (
                calc.get("data-source-aggregate-document", {})
                .get("data-source-document", [])
            )
            calc_row["data_sources"] = "; ".join(
                s.get("data-source-identifier", "") for s in sources
            )
            calc_rows.append(calc_row)

        calc_df = pd.DataFrame(calc_rows)
        calc_path = output_path.replace(".csv", "_calculated.csv")
        calc_df.to_csv(calc_path, index=False)

    return df
```

---

## Unit Normalization

### Common Unit Conversions

| Measurement | Preferred Unit | UCUM Code | Alternatives to Normalize |
|------------|---------------|-----------|--------------------------|
| Cell count | cell | {cell} | cells, count |
| Cell density | cell/mL | {cell}/mL | cells/mL, x10^6/mL |
| Viability | % | % | fraction (multiply by 100) |
| Concentration | mg/mL | mg/mL | g/L (divide by 1000), ug/mL (multiply by 1000) |
| Absorbance | AU | AU | OD, mAU (divide by 1000) |
| Fluorescence | RFU | {RFU} | AFU, counts |
| Temperature | degC | Cel | F (convert), K (convert) |
| Volume | uL | uL | mL (multiply by 1000), nL (divide by 1000) |
| Time | min | min | s (divide by 60), h (multiply by 60) |
| Wavelength | nm | nm | um (multiply by 1000) |
| Mass | mg | mg | g (multiply by 1000), ug (divide by 1000) |
| Flow rate | mL/min | mL/min | uL/min (divide by 1000) |

```python
UNIT_CONVERSIONS = {
    ("g/L", "mg/mL"): lambda x: x,           # 1 g/L = 1 mg/mL
    ("ug/mL", "mg/mL"): lambda x: x / 1000,
    ("ng/mL", "mg/mL"): lambda x: x / 1e6,
    ("mAU", "AU"): lambda x: x / 1000,
    ("x10^6/mL", "cell/mL"): lambda x: x * 1e6,
    ("cells/mL", "cell/mL"): lambda x: x,     # Just unit name normalization
}

def normalize_unit(value: float, from_unit: str, to_unit: str) -> float:
    """Convert value from one unit to another."""
    key = (from_unit, to_unit)
    if key in UNIT_CONVERSIONS:
        return UNIT_CONVERSIONS[key](value)
    raise ValueError(f"No conversion defined: {from_unit} -> {to_unit}")
```

---

## Provenance Tracking

### File Hashing

```python
import hashlib
from pathlib import Path

def compute_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """Compute cryptographic hash of input file for data integrity tracking."""
    h = hashlib.new(algorithm)
    path = Path(file_path)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return f"{algorithm}:{h.hexdigest()}"
```

### Conversion Audit Trail

```json
{
  "conversion-audit": {
    "original-file": {
      "name": "20240315_vicell_run.csv",
      "hash": "sha256:a3f2b8c9...",
      "size-bytes": 45678,
      "last-modified": "2024-03-15T10:00:00Z"
    },
    "converter": {
      "name": "lab-standardizer",
      "version": "2.1.0",
      "tier": 1,
      "vendor-parser": "Vendor.BECKMAN_VI_CELL_BLU"
    },
    "environment": {
      "python": "3.11.7",
      "allotropy": "0.1.50",
      "pandas": "2.2.0",
      "os": "Linux 6.1",
      "hostname": "lab-server-01"
    },
    "conversion": {
      "timestamp": "2024-03-15T14:30:00Z",
      "duration-seconds": 1.2,
      "records-processed": 48,
      "records-skipped": 0,
      "warnings": [],
      "errors": []
    },
    "output-file": {
      "name": "20240315_vicell_run_asm.json",
      "hash": "sha256:d7e8f9a0...",
      "size-bytes": 123456
    }
  }
}
```

---

## Validation

### Schema Compliance Checking

```python
import jsonschema
from typing import Optional

def validate_asm_document(asm_document: dict) -> list[str]:
    """
    Validate ASM document against required field rules.
    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Required top-level sections
    if "$asm.manifest" not in asm_document:
        errors.append("Missing required: $asm.manifest")
    if "data-system-document" not in asm_document:
        errors.append("Missing required: data-system-document")

    # Data system document validation
    dsd = asm_document.get("data-system-document", {})
    dpd = dsd.get("data-processing-document", {})
    if not dpd.get("software-name"):
        errors.append("Missing required: data-system-document.data-processing-document.software-name")

    fi = dsd.get("file-information", {})
    if not fi.get("original-file-hash"):
        errors.append("Missing recommended: file-information.original-file-hash")

    # Device system document validation
    dev = asm_document.get("device-system-document", {})
    if not dev.get("model-number"):
        errors.append("Missing recommended: device-system-document.model-number")
    if not dev.get("device-identifier"):
        errors.append("Missing recommended: device-system-document.device-identifier")

    # Measurement validation
    mad = asm_document.get("measurement-aggregate-document", {})
    measurements = mad.get("measurement-document", [])

    if not measurements:
        errors.append("No measurement-document entries found")

    for i, meas in enumerate(measurements):
        if "sample-document" not in meas:
            errors.append(f"measurement-document[{i}]: missing sample-document")
        elif not meas["sample-document"].get("sample-identifier"):
            errors.append(f"measurement-document[{i}]: missing sample-identifier")

    # Calculated data validation: check data source references
    calc_agg = mad.get("calculated-data-aggregate-document", {})
    calc_docs = calc_agg.get("calculated-data-document", [])

    measurement_ids = {m.get("measurement-identifier") for m in measurements}

    for i, calc in enumerate(calc_docs):
        if not calc.get("calculation-description"):
            errors.append(f"calculated-data-document[{i}]: missing calculation-description")

        sources = (
            calc.get("data-source-aggregate-document", {})
            .get("data-source-document", [])
        )
        if not sources:
            errors.append(
                f"calculated-data-document[{i}]: missing data-source-aggregate-document "
                f"(calculated data must reference raw measurements)"
            )

    return errors
```

### Required Field Verification Matrix

| Section | Field | Required | Regulatory Impact |
|---------|-------|----------|------------------|
| manifest | vocabulary | Yes | Schema version identification |
| manifest | technique | Yes | Analytical method classification |
| data-system-document | software-name | Yes | Converter traceability |
| data-system-document | software-version | Yes | Reproducibility |
| file-information | original-file-hash | Recommended | Data integrity (21 CFR Part 11) |
| file-information | conversion-timestamp | Recommended | Audit trail |
| device-system-document | brand-name | Yes | Instrument qualification |
| device-system-document | model-number | Yes | Instrument qualification |
| device-system-document | device-identifier | Recommended | Specific hardware traceability |
| measurement-document | sample-identifier | Yes | Sample traceability |
| measurement-document | measurement-time | Recommended | Temporal context |
| calculated-data-document | data-source-document | Yes | Calculation traceability |
| calculated-data-document | calculation-description | Yes | Method transparency |

---

## End-to-End Conversion Workflow

```python
from pathlib import Path
import json

def convert_instrument_file(
    file_path: str,
    instrument_type: str,
    output_dir: str,
    device_info: dict,
    column_map: dict = None
) -> dict:
    """
    Complete conversion pipeline: detect tier, parse, validate, output.

    Args:
        file_path: Path to raw instrument file
        instrument_type: Vendor enum string or instrument name
        output_dir: Directory for ASM JSON and flattened CSV output
        device_info: {"brand": "...", "model": "...", "serial": "..."}
        column_map: Manual column mapping (Tier 2 only)

    Returns:
        dict with conversion results and file paths
    """
    path = Path(file_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Attempt Tier 1 (native allotropy)
    asm_document = None
    tier_used = None

    try:
        from allotropy.parser_factory import Vendor
        from allotropy.to_allotrope import allotrope_from_file

        vendor = getattr(Vendor, instrument_type, None)
        if vendor:
            asm_document = allotrope_from_file(str(path), vendor_type=vendor)
            tier_used = 1
    except Exception as e:
        print(f"Tier 1 failed: {e}")

    # Step 2: Fallback to Tier 2 (pandas)
    if asm_document is None and path.suffix.lower() in ('.csv', '.tsv', '.xlsx', '.xls', '.txt'):
        try:
            config = {
                "technique": "generic",
                "manufacturer": device_info.get("brand", "Unknown"),
                "model": device_info.get("model", "Unknown"),
                "column_map": column_map or {},
                "unit_map": {}
            }
            asm_document = parse_generic_instrument_file(str(path), config)
            tier_used = 2
        except Exception as e:
            print(f"Tier 2 failed: {e}")

    # Step 3: Fallback to Tier 3 (PDF)
    if asm_document is None and path.suffix.lower() == '.pdf':
        try:
            asm_document = pdf_to_asm(str(path), {"technique": "generic"})
            tier_used = 3
        except Exception as e:
            print(f"Tier 3 failed: {e}")

    if asm_document is None:
        raise ValueError(f"All conversion tiers failed for {file_path}")

    # Step 4: Validate
    validation_errors = validate_asm_document(asm_document)
    if validation_errors:
        print(f"Validation warnings ({len(validation_errors)}):")
        for err in validation_errors:
            print(f"  - {err}")

    # Step 5: Output ASM JSON
    json_path = out_dir / f"{path.stem}_asm.json"
    with open(json_path, "w") as f:
        json.dump(asm_document, f, indent=2, default=str)

    # Step 6: Output flattened CSV
    csv_path = out_dir / f"{path.stem}_flat.csv"
    flatten_asm_to_csv(asm_document, str(csv_path))

    return {
        "tier_used": tier_used,
        "asm_json_path": str(json_path),
        "csv_path": str(csv_path),
        "validation_errors": validation_errors,
        "record_count": len(
            asm_document
            .get("measurement-aggregate-document", {})
            .get("measurement-document", [])
        )
    }
```

---

## Completeness Checklist

- [ ] Input file format identified and appropriate tier selected (1/2/3)
- [ ] All raw measurement values placed in `measurement-document` (not in calculated)
- [ ] All derived values placed in `calculated-data-document` with data source links
- [ ] `data-system-document` includes converter name, version, and library versions
- [ ] `device-system-document` includes manufacturer, model, and serial number
- [ ] Original file hash computed and stored for data integrity
- [ ] Units normalized to standard forms (UCUM where applicable)
- [ ] Sample identifiers preserved without truncation or modification
- [ ] Validation passes with no errors (warnings acceptable with justification)
- [ ] JSON output conforms to ASM schema structure
- [ ] CSV flattened output ready for LIMS import with clear column names
- [ ] Conversion audit trail documented (timestamp, duration, record counts)
