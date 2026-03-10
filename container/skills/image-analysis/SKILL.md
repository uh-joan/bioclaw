---
name: image-analysis
description: Biomedical image analysis and microscopy data processing. Cell segmentation, fluorescence quantification, histopathology analysis, image feature extraction, colocalization, morphological analysis, tissue classification, cell counting, intensity measurements. Use when user mentions image analysis, microscopy, cell segmentation, fluorescence, histopathology, H&E staining, immunofluorescence, colocalization, morphology, cell counting, image quantification, biomedical imaging, confocal, brightfield, DAPI, nuclei detection, watershed segmentation, Otsu threshold, stain deconvolution, regionprops, or tissue morphometry.
---

# Biomedical Image Analysis

Production-ready biomedical image analysis methodology. The agent writes and executes Python code using scikit-image, scipy, and numpy for microscopy image processing, cell segmentation, fluorescence quantification, histopathology analysis, and image feature extraction. All pipelines use standard scientific Python libraries without deep learning dependencies.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_image-analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Spatial gene expression overlaid on tissue images → use `spatial-transcriptomics`
- Spatial proteomics and multi-modal spatial data → use `spatial-omics-analysis`
- Single-cell quantification from segmented images → use `single-cell-analysis`
- Gene set enrichment of image-derived markers → use `gene-enrichment`
- Disease associations for identified biomarkers → use `disease-research`
- Protein 3D structure visualization and analysis → use `protein-structure-retrieval`

## Cross-Reference: Other Skills

- **Spatial gene expression overlaid on tissue images** -> use spatial-transcriptomics skill
- **Spatial proteomics and multi-modal spatial data** -> use spatial-omics-analysis skill
- **Single-cell quantification from segmented images** -> use single-cell-analysis skill
- **Gene set enrichment of image-derived markers** -> use gene-enrichment skill
- **Disease associations for identified biomarkers** -> use disease-research skill

## Python Environment

Available libraries (no deep learning frameworks):

| Library | Purpose |
|---------|---------|
| `scikit-image` (skimage) | Image processing, segmentation, feature extraction, morphology |
| `scipy` | Signal processing, spatial analysis, statistics, ndimage operations |
| `numpy` | Array operations, mathematical transforms |
| `matplotlib` | Visualization, overlays, montages, quantification plots |
| `pandas` | Tabular results, feature tables, statistics export |

**Not available:** TensorFlow, PyTorch, Keras, cellpose, StarDist, or other deep learning frameworks. All segmentation must use classical methods (thresholding, watershed, morphological operations).

---

## Analysis Decision Tree

```
User request -> Determine analysis type:

+-- Brightfield / H&E histopathology
|   -> Go to "H&E Analysis Framework"
|
+-- Fluorescence microscopy (single or multi-channel)
|   +-- Segmentation and counting
|   |   -> Phases 1-3, then Phase 6
|   +-- Intensity quantification
|   |   -> Phases 1-3, then Phase 4
|   +-- Colocalization
|   |   -> Phases 1-2, then Phase 5
|   +-- Full analysis
|       -> Phases 1-7 sequentially
|
+-- Cell counting only
|   -> Phases 1-2, then Phase 6
|
+-- Quality control / image assessment
|   -> Go to "Quality Control"
|
+-- Feature extraction from pre-segmented data
    -> Phase 3 directly
```

---

## Phase 1: Image Loading & Preprocessing

```python
import numpy as np
from skimage import io, img_as_float
from skimage.filters import gaussian
from skimage.morphology import disk, white_tophat
from skimage.exposure import rescale_intensity
import matplotlib.pyplot as plt

# Load and inspect
img = io.imread("image_path.tif")
print(f"Shape: {img.shape}, dtype: {img.dtype}, range: [{img.min()}, {img.max()}]")

# Channel splitting (auto-detect layout)
if img.ndim == 3 and img.shape[2] in [3, 4]:
    channels = [img[:, :, i] for i in range(min(img.shape[2], 3))]  # RGB
elif img.ndim == 3 and img.shape[0] < img.shape[1]:
    channels = [img[i] for i in range(img.shape[0])]  # channels-first
else:
    channels = [img]  # grayscale

# Background subtraction + smoothing
def preprocess_channel(channel, sigma=1.0, bg_radius=50):
    ch = img_as_float(channel)
    bg = ch - white_tophat(ch, disk(bg_radius))
    return gaussian(np.clip(ch - bg, 0, None), sigma=sigma)

processed = [preprocess_channel(ch) for ch in channels]
```

**Key parameters:** `sigma` 0.5-1.0 for high-SNR, 1.5-3.0 for noisy. `bg_radius` must exceed largest object size. Always convert 16-bit to float before processing.

---

## Phase 2: Segmentation

```python
from skimage.filters import threshold_otsu, threshold_local
from skimage.segmentation import watershed
from skimage.morphology import (binary_opening, binary_closing,
    remove_small_objects, remove_small_holes, disk, label)
from skimage.feature import peak_local_max
from skimage.color import label2rgb
from scipy import ndimage as ndi

# Method 1: Otsu (uniform illumination, well-separated objects)
def segment_otsu(image, min_size=100):
    binary = image > threshold_otsu(image)
    binary = remove_small_objects(binary_opening(binary, disk(2)), min_size=min_size)
    return label(remove_small_holes(binary, area_threshold=50))

# Method 2: Adaptive threshold (uneven illumination)
def segment_adaptive(image, block_size=51, offset=0.01, min_size=100):
    binary = image > threshold_local(image, block_size=block_size, offset=offset)
    return label(remove_small_objects(binary_opening(binary, disk(2)), min_size=min_size))

# Method 3: Watershed (touching/clustered cells) — most common for microscopy
def segment_watershed(image, min_distance=10, min_size=100):
    binary = image > threshold_otsu(image)
    binary = remove_small_holes(remove_small_objects(
        binary_opening(binary, disk(2)), min_size=min_size), area_threshold=50)
    distance = ndi.distance_transform_edt(binary)
    coords = peak_local_max(distance, min_distance=min_distance, labels=binary)
    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    return watershed(-distance, label(mask), mask=binary)

# Method 4: Nuclei (DAPI/Hoechst — opening+closing for round shapes)
def segment_nuclei(dapi, sigma=2.0, min_distance=8, min_size=50):
    smoothed = gaussian(dapi, sigma=sigma)
    binary = smoothed > threshold_otsu(smoothed)
    binary = binary_closing(binary_opening(binary, disk(3)), disk(3))
    binary = remove_small_holes(remove_small_objects(binary, min_size=min_size),
                                 area_threshold=min_size // 2)
    distance = ndi.distance_transform_edt(binary)
    coords = peak_local_max(distance, min_distance=min_distance, labels=binary)
    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    return watershed(-distance, label(mask), mask=binary)

nuclei_labels = segment_nuclei(processed[0])  # DAPI = channel 0
print(f"Detected {nuclei_labels.max()} nuclei")

# Visualization
overlay = label2rgb(nuclei_labels, image=processed[0], bg_label=0, alpha=0.3)
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
axes[0].imshow(processed[0], cmap="gray"); axes[0].set_title("Input")
axes[1].imshow(overlay); axes[1].set_title(f"Segmented ({nuclei_labels.max()} objects)")
for ax in axes: ax.axis("off")
plt.savefig("segmentation_result.png", dpi=150, bbox_inches="tight"); plt.close()
```

**Choosing a method:** Otsu for uniform background; Adaptive for uneven illumination; Watershed for touching cells (tune `min_distance`); Nuclei-specific for DAPI/Hoechst with round morphology.

---

## Phase 3: Feature Extraction

```python
from skimage.measure import regionprops_table, regionprops
from skimage.feature import graycomatrix, graycoprops
import pandas as pd

# --- Morphological + intensity features ---
def extract_features(label_image, intensity_images, channel_names=None):
    """Extract morphological and per-channel intensity features."""
    if channel_names is None:
        channel_names = [f"ch{i}" for i in range(len(intensity_images))]

    # Morphological features from label image
    morph_props = regionprops_table(
        label_image,
        properties=[
            "label", "area", "perimeter", "eccentricity",
            "solidity", "extent", "major_axis_length",
            "minor_axis_length", "orientation",
            "centroid", "bbox"
        ]
    )
    df = pd.DataFrame(morph_props)

    # Derived morphological features
    df["circularity"] = (4 * np.pi * df["area"]) / (df["perimeter"] ** 2 + 1e-8)
    df["aspect_ratio"] = df["major_axis_length"] / (df["minor_axis_length"] + 1e-8)

    # Per-channel intensity features
    for ch_img, ch_name in zip(intensity_images, channel_names):
        regions = regionprops(label_image, intensity_image=ch_img)
        int_data = []
        for r in regions:
            px = r.image_intensity[r.image]
            int_data.append({
                f"{ch_name}_mean": np.mean(px), f"{ch_name}_std": np.std(px),
                f"{ch_name}_median": np.median(px), f"{ch_name}_max": np.max(px),
                f"{ch_name}_integrated": np.sum(px),
            })
        df = pd.concat([df, pd.DataFrame(int_data)], axis=1)

    return df

features = extract_features(
    nuclei_labels,
    intensity_images=processed,
    channel_names=["DAPI", "GFP", "RFP"]  # adjust to actual channels
)
print(f"Extracted features for {len(features)} objects")
print(features.describe())
features.to_csv("cell_features.csv", index=False)
```

### Texture Features (GLCM)

```python
def extract_texture_features(label_image, intensity_image, distances=[1, 3], angles=[0]):
    """Extract GLCM texture features per labeled region."""
    texture_data = []
    regions = regionprops(label_image, intensity_image=intensity_image)

    for region in regions:
        # Crop and rescale intensity patch to uint8 for GLCM
        patch = region.image_intensity.copy()
        patch = ((patch - patch.min()) / (patch.max() - patch.min() + 1e-8) * 255).astype(np.uint8)

        # Mask out background pixels
        patch[~region.image] = 0

        if patch.size < 4:
            continue

        glcm = graycomatrix(patch, distances=distances, angles=angles,
                            levels=256, symmetric=True, normed=True)

        row = {"label": region.label}
        for prop_name in ["contrast", "dissimilarity", "homogeneity", "energy", "correlation"]:
            values = graycoprops(glcm, prop_name)
            row[f"texture_{prop_name}"] = values.mean()

        texture_data.append(row)

    return pd.DataFrame(texture_data)

texture_features = extract_texture_features(nuclei_labels, processed[0])
features = features.merge(texture_features, on="label", how="left")
```

---

## Phase 4: Fluorescence Quantification

```python
def quantify_fluorescence(label_image, channels, channel_names, bg_correction=True):
    """Per-cell fluorescence: mean, integrated, max, std, CV per channel. Background-corrected."""
    results = []
    bg_medians = {}
    if bg_correction:
        for ch, name in zip(channels, channel_names):
            bg_medians[name] = np.median(ch[label_image == 0])

    for region in regionprops(label_image):
        row = {"label": region.label, "area": region.area,
               "centroid_y": region.centroid[0], "centroid_x": region.centroid[1]}
        for ch, name in zip(channels, channel_names):
            px = ch[region.slice][region.image].astype(float)
            if bg_correction:
                px = np.clip(px - bg_medians[name], 0, None)
            row[f"{name}_mean"] = np.mean(px)
            row[f"{name}_integrated"] = np.sum(px)
            row[f"{name}_max"] = np.max(px)
            row[f"{name}_cv"] = np.std(px) / (np.mean(px) + 1e-8)
        results.append(row)

    df = pd.DataFrame(results)
    # Channel ratios
    for i, a in enumerate(channel_names):
        for b in channel_names[i+1:]:
            df[f"ratio_{a}_{b}"] = df[f"{a}_mean"] / (df[f"{b}_mean"] + 1e-8)
    return df

fluor_data = quantify_fluorescence(nuclei_labels, processed, ["DAPI", "GFP", "RFP"])
fluor_data.to_csv("fluorescence_quantification.csv", index=False)
print(fluor_data.describe())
```

---

## Phase 5: Colocalization Analysis

```python
from scipy.stats import pearsonr, spearmanr

def colocalization_analysis(channel_a, channel_b, mask=None):
    """Colocalization metrics: Pearson, Manders M1/M2, Li's ICQ, overlap coefficient."""
    if mask is not None:
        a = channel_a[mask].flatten().astype(float)
        b = channel_b[mask].flatten().astype(float)
    else:
        a = channel_a.flatten().astype(float)
        b = channel_b.flatten().astype(float)

    nonzero = (a > 0) | (b > 0)
    a, b = a[nonzero], b[nonzero]

    results = {}
    results["pearson_r"], results["pearson_p"] = pearsonr(a, b)
    results["spearman_r"], results["spearman_p"] = spearmanr(a, b)

    # Mander's coefficients
    thresh_a = threshold_otsu(channel_a[channel_a > 0]) if (channel_a > 0).any() else 0
    thresh_b = threshold_otsu(channel_b[channel_b > 0]) if (channel_b > 0).any() else 0
    results["manders_M1"] = np.sum(a[b > thresh_b]) / (np.sum(a) + 1e-8)
    results["manders_M2"] = np.sum(b[a > thresh_a]) / (np.sum(b) + 1e-8)

    # Overlap coefficient
    results["overlap_coeff"] = np.sum(a * b) / (np.sqrt(np.sum(a**2) * np.sum(b**2)) + 1e-8)

    # Li's ICQ: -0.5 (segregated) to +0.5 (dependent colocalization)
    product = (a - np.mean(a)) * (b - np.mean(b))
    results["li_ICQ"] = (np.sum(product > 0) / len(product)) - 0.5

    return results

cell_mask = nuclei_labels > 0
coloc = colocalization_analysis(processed[1], processed[2], mask=cell_mask)
for k, v in coloc.items():
    print(f"  {k}: {v}")

# Scatter plot
fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(processed[1][cell_mask].flatten(), processed[2][cell_mask].flatten(),
           s=1, alpha=0.1, c="gray")
ax.set_xlabel("GFP Intensity"); ax.set_ylabel("RFP Intensity")
ax.set_title(f"Colocalization (r={coloc['pearson_r']:.3f})")
plt.savefig("colocalization_scatter.png", dpi=150, bbox_inches="tight"); plt.close()
```

**Interpreting colocalization:** Pearson r>0.7 = strong, 0.4-0.7 = moderate, <0.4 = weak. Li's ICQ>0.1 = dependent staining, <-0.1 = exclusion. Always report both Manders M1 and M2 as they are asymmetric.

---

## Phase 6: Cell Counting & Statistics

```python
from scipy.spatial import KDTree
from scipy.stats import mannwhitneyu, ttest_ind

def cell_counting_analysis(label_image, pixel_size_um=None):
    """Count cells, compute density, nearest-neighbor distances, Clark-Evans index."""
    regions = regionprops(label_image)
    n_cells = len(regions)
    centroids = np.array([r.centroid for r in regions])
    results = {"total_count": n_cells, "image_shape": label_image.shape}

    if pixel_size_um is not None:
        area_mm2 = label_image.shape[0] * label_image.shape[1] * (pixel_size_um ** 2) / 1e6
        results["area_mm2"] = area_mm2
        results["density_per_mm2"] = n_cells / area_mm2

    if n_cells > 1:
        tree = KDTree(centroids)
        nn_dist = tree.query(centroids, k=2)[0][:, 1]  # nearest neighbor (skip self)
        if pixel_size_um:
            nn_dist = nn_dist * pixel_size_um
        results["nn_distance_mean"] = np.mean(nn_dist)
        results["nn_distance_std"] = np.std(nn_dist)
        # Clark-Evans R: <1 clustered, =1 random, >1 dispersed
        if pixel_size_um and "density_per_mm2" in results:
            expected_nn = 0.5 / np.sqrt(results["density_per_mm2"] / 1e6)
            results["clark_evans_R"] = results["nn_distance_mean"] / expected_nn

    return results, centroids

count_results, centroids = cell_counting_analysis(nuclei_labels, pixel_size_um=0.65)

# Spatial density heatmap
from scipy.ndimage import gaussian_filter
density_map = np.zeros(nuclei_labels.shape[:2])
coords = centroids.astype(int)
coords[:, 0] = np.clip(coords[:, 0], 0, nuclei_labels.shape[0] - 1)
coords[:, 1] = np.clip(coords[:, 1], 0, nuclei_labels.shape[1] - 1)
for y, x in coords:
    density_map[y, x] += 1
density_map = gaussian_filter(density_map, sigma=30)

fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(density_map, cmap="hot", interpolation="bilinear")
plt.colorbar(im, ax=ax, label="Cell Density")
ax.set_title(f"Cell Density (n={count_results['total_count']})")
ax.axis("off")
plt.savefig("cell_density_heatmap.png", dpi=150, bbox_inches="tight"); plt.close()

# Compare two populations
def compare_populations(features_a, features_b, metric):
    """t-test and Mann-Whitney U comparison between two cell populations."""
    a, b = features_a[metric].dropna(), features_b[metric].dropna()
    t_stat, t_p = ttest_ind(a, b)
    u_stat, u_p = mannwhitneyu(a, b, alternative="two-sided")
    print(f"  A: n={len(a)}, mean={a.mean():.4f} | B: n={len(b)}, mean={b.mean():.4f}")
    print(f"  t-test p={t_p:.2e}, Mann-Whitney p={u_p:.2e}")
    return {"t_pval": t_p, "u_pval": u_p}
```

---

## Phase 7: Visualization & Reporting

```python
from skimage.color import label2rgb
from matplotlib.colors import Normalize
from matplotlib import cm

# Segmentation overlay
def create_overlay(image, label_image, alpha=0.3):
    """Colored segmentation overlay on original image."""
    if image.ndim == 2:
        image_rgb = np.stack([image] * 3, axis=-1)
    else:
        image_rgb = image.copy()
    image_rgb = (image_rgb / image_rgb.max() * 255).astype(np.uint8)
    return label2rgb(label_image, image=image_rgb, bg_label=0, alpha=alpha)

# Feature-mapped overlay (color cells by a quantitative metric)
def feature_overlay(image, label_image, feature_values, feature_name, cmap_name="viridis"):
    """Color each cell by a measured value (e.g., GFP intensity, area)."""
    vmin, vmax = np.percentile(feature_values, [2, 98])
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap(cmap_name)
    colored = np.zeros((*label_image.shape, 3))
    for region, val in zip(regionprops(label_image), feature_values):
        colored[label_image == region.label] = cmap(norm(val))[:3]
    bg = np.stack([image / image.max()] * 3, axis=-1) if image.ndim == 2 else image / image.max()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(bg * 0.5 + colored * 0.5)
    plt.colorbar(cm.ScalarMappable(cmap=cmap, norm=norm), ax=ax, label=feature_name)
    ax.axis("off")
    plt.savefig(f"overlay_{feature_name}.png", dpi=150, bbox_inches="tight"); plt.close()

# Summary report
def generate_report(count_results, features, coloc_results=None):
    """Print and save text summary of analysis results."""
    print(f"Total cells: {count_results['total_count']}")
    if "density_per_mm2" in count_results:
        print(f"Density: {count_results['density_per_mm2']:.1f} cells/mm2")
    if "clark_evans_R" in count_results:
        ce = count_results["clark_evans_R"]
        print(f"Clark-Evans R={ce:.3f} ({'clustered' if ce<0.95 else 'dispersed' if ce>1.05 else 'random'})")
    print(f"Mean area: {features['area'].mean():.1f} px, circularity: {features['circularity'].mean():.3f}")
    if coloc_results:
        print(f"Colocalization: Pearson r={coloc_results['pearson_r']:.3f}, "
              f"M1={coloc_results['manders_M1']:.3f}, M2={coloc_results['manders_M2']:.3f}")
```

---

## H&E Analysis Framework

```python
from skimage.color import rgb2hed, rgb2gray

def he_deconvolution(rgb_image):
    """Separate H&E into Hematoxylin (nuclei) and Eosin (cytoplasm) channels."""
    hed = rgb2hed(img_as_float(rgb_image))
    hematoxylin = rescale_intensity(hed[:, :, 0], out_range=(0, 1))
    eosin = rescale_intensity(hed[:, :, 1], out_range=(0, 1))
    return hematoxylin, eosin

def detect_tissue(rgb_image, min_size=10000):
    """Detect tissue vs glass slide background."""
    gray = rgb2gray(rgb_image)
    tissue = gray < threshold_otsu(gray)
    tissue = binary_closing(binary_opening(tissue, disk(5)), disk(10))
    return remove_small_objects(tissue, min_size=min_size)

def segment_he_nuclei(hematoxylin, min_size=30, min_distance=5):
    """Segment nuclei from hematoxylin channel using watershed."""
    smoothed = gaussian(hematoxylin, sigma=1.0)
    binary = smoothed > threshold_otsu(smoothed)
    binary = binary_opening(binary, disk(2))
    binary = remove_small_objects(binary, min_size=min_size)
    binary = remove_small_holes(binary, area_threshold=min_size)
    distance = ndi.distance_transform_edt(binary)
    coords = peak_local_max(distance, min_distance=min_distance, labels=binary)
    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    return watershed(-distance, label(mask), mask=binary)

# Full H&E pipeline
he_image = io.imread("he_image.tif")
hematoxylin, eosin = he_deconvolution(he_image)
tissue_mask = detect_tissue(he_image)
nuclei_labels = segment_he_nuclei(hematoxylin)
nuclei_labels[~tissue_mask] = 0
print(f"Tissue: {tissue_mask.sum()} px, Nuclei: {nuclei_labels.max()}")
```

---

## Quality Control

```python
from skimage.filters import laplace

def assess_image_quality(image):
    """Focus, saturation, illumination uniformity, and dynamic range assessment."""
    gray = rgb2gray(image) if image.ndim == 3 else img_as_float(image)
    results = {}

    # Focus (Laplacian variance): higher = sharper, threshold ~0.001
    results["focus_score"] = np.var(laplace(gray))

    # Saturation: warn if >1% pixels at max
    if image.dtype == np.uint8:
        results["saturated_frac"] = np.mean(image >= 254)
    elif image.dtype == np.uint16:
        results["saturated_frac"] = np.mean(image >= 65534)
    else:
        results["saturated_frac"] = np.mean(image >= 0.99)

    # Illumination uniformity (quadrant CV): <0.1 uniform, >0.3 non-uniform
    h, w = gray.shape
    quads = [gray[:h//2, :w//2], gray[:h//2, w//2:], gray[h//2:, :w//2], gray[h//2:, w//2:]]
    q_means = [np.mean(q) for q in quads]
    results["illumination_cv"] = np.std(q_means) / (np.mean(q_means) + 1e-8)

    # Dynamic range
    results["dynamic_range"] = np.percentile(gray, 95) - np.percentile(gray, 5)

    # Flag issues
    issues = []
    if results["focus_score"] < 0.001: issues.append("DEFOCUSED")
    if results["saturated_frac"] > 0.01: issues.append("SATURATED")
    if results["illumination_cv"] > 0.3: issues.append("UNEVEN ILLUMINATION")
    if results["dynamic_range"] < 0.2: issues.append("LOW CONTRAST")
    results["issues"] = issues or ["PASS"]
    return results

qc = assess_image_quality(img)
for k, v in qc.items():
    print(f"  {k}: {v}")
```

---

## Evidence Grading

When reporting image analysis results, grade confidence based on:

| Grade | Criteria |
|-------|----------|
| **High** | QC passed, >100 cells segmented, segmentation visually validated, appropriate method for image type |
| **Medium** | QC passed with minor issues, 20-100 cells, segmentation reasonable but not manually validated |
| **Low** | QC flagged issues (saturation, defocus), <20 cells, or segmentation method may not suit the image type |
| **Uncertain** | Severe QC failures, segmentation artifacts visible, or analysis assumptions violated |

Always report:
1. Number of cells/objects detected and method used.
2. Any QC issues flagged.
3. Key parameter choices and their rationale.
4. Limitations of classical (non-deep-learning) segmentation for the specific image type.

---

## Multi-Agent Workflow Examples

**"Segment cells in fluorescence images and correlate with spatial gene expression"**
1. Image Analysis -> Segment nuclei from DAPI, quantify marker fluorescence per cell
2. Spatial Transcriptomics -> Map gene expression to tissue coordinates
3. Single-Cell Analysis -> Cluster cells by combined image + expression features

**"Analyze H&E slides and identify tissue regions for spatial omics integration"**
1. Image Analysis -> H&E deconvolution, tissue detection, nuclei segmentation, morphological features
2. Spatial Omics Analysis -> Register spatial omics data to tissue coordinates
3. Disease Research -> Literature context for tissue morphology findings

**"Quantify immunofluorescence co-staining and assess cell phenotypes"**
1. Image Analysis -> Segment cells, quantify multi-channel fluorescence, colocalization analysis
2. Single-Cell Analysis -> Phenotype classification from intensity profiles
3. Gene Enrichment -> Pathway analysis of marker-positive vs marker-negative populations

**"Assess image quality across a microscopy dataset and flag problematic acquisitions"**
1. Image Analysis -> Batch QC (focus, saturation, illumination) across all images
2. Image Analysis -> Segment and quantify only images passing QC thresholds
3. Visualization and reporting of QC-filtered results

## Completeness Checklist

- [ ] Image quality control (QC) assessment performed and issues documented
- [ ] Segmentation method chosen and justified for the image type
- [ ] Key parameters (sigma, min_size, min_distance) documented with rationale
- [ ] Segmentation overlay visualization saved for validation
- [ ] Feature extraction completed with morphological and intensity metrics
- [ ] Statistical comparisons include appropriate tests (t-test, Mann-Whitney)
- [ ] All output files saved (CSVs, PNGs) with descriptive names
- [ ] Limitations of classical (non-deep-learning) segmentation acknowledged
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
