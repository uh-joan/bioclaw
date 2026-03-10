# Colony & Swarming Phenotype Recipes

Executable Python code templates for bacterial colony image analysis, swarming motility quantification, and phenotype characterization. Each recipe is self-contained with inline comments.

---

## 1. Image Loading and Preprocessing (PIL/skimage)

```python
import numpy as np
from PIL import Image
from skimage import io, color, exposure, filters, util
import matplotlib.pyplot as plt

# Load plate image from file
img = io.imread("plate_image.png")
print(f"Image shape: {img.shape}")
print(f"Dtype: {img.dtype}, Range: [{img.min()}, {img.max()}]")

# Convert to grayscale for analysis
if img.ndim == 3:
    gray = color.rgb2gray(img)       # float64 in [0, 1]
else:
    gray = util.img_as_float(img)
print(f"Grayscale shape: {gray.shape}")

# Enhance contrast using CLAHE (adaptive histogram equalization)
# Useful when plate images have uneven illumination
gray_clahe = exposure.equalize_adapthist(gray, clip_limit=0.03)

# Gaussian blur to reduce noise before segmentation
gray_smooth = filters.gaussian(gray_clahe, sigma=2.0)

# Crop to plate region (remove borders/labels)
# Adjust these coordinates to match your plate images
h, w = gray.shape
margin = int(min(h, w) * 0.05)  # 5% margin
plate_region = gray_smooth[margin:h-margin, margin:w-margin]
print(f"Cropped plate region: {plate_region.shape}")

# Display preprocessing steps
fig, axes = plt.subplots(1, 4, figsize=(20, 5))
axes[0].imshow(img)
axes[0].set_title("Original")
axes[1].imshow(gray, cmap="gray")
axes[1].set_title("Grayscale")
axes[2].imshow(gray_clahe, cmap="gray")
axes[2].set_title("CLAHE Enhanced")
axes[3].imshow(gray_smooth, cmap="gray")
axes[3].set_title("Smoothed")
for ax in axes:
    ax.axis("off")
plt.tight_layout()
plt.savefig("preprocessing_steps.png", dpi=150)
print("Preprocessing complete")
```

---

## 2. Colony Boundary Detection (Thresholding, Edge Detection)

```python
import numpy as np
from skimage import io, color, filters, morphology, measure, segmentation
import matplotlib.pyplot as plt

img = io.imread("colony_plate.png")
gray = color.rgb2gray(img) if img.ndim == 3 else img.astype(float)

# --- Method 1: Otsu's automatic thresholding ---
thresh_otsu = filters.threshold_otsu(gray)
binary_otsu = gray < thresh_otsu     # colonies are darker than background
# Clean up: remove small objects and fill holes
binary_clean = morphology.remove_small_objects(binary_otsu, min_size=200)
binary_clean = morphology.binary_fill_holes(binary_clean)
print(f"Otsu threshold: {thresh_otsu:.3f}")

# --- Method 2: Adaptive thresholding (handles uneven illumination) ---
# block_size must be odd; offset shifts the threshold
thresh_local = filters.threshold_local(gray, block_size=101, offset=0.02)
binary_adaptive = gray < thresh_local
binary_adaptive = morphology.remove_small_objects(binary_adaptive, min_size=200)
binary_adaptive = morphology.binary_fill_holes(binary_adaptive)

# --- Method 3: Canny edge detection ---
edges = filters.canny(gray, sigma=2.0, low_threshold=0.05, high_threshold=0.15)
# Dilate edges to close gaps, then fill
edges_dilated = morphology.binary_dilation(edges, morphology.disk(3))
edges_filled = morphology.binary_fill_holes(edges_dilated)
edges_clean = morphology.remove_small_objects(edges_filled, min_size=200)

# Label connected components to get individual colonies
labeled_otsu = measure.label(binary_clean)
labeled_adaptive = measure.label(binary_adaptive)
print(f"Colonies detected (Otsu): {labeled_otsu.max()}")
print(f"Colonies detected (Adaptive): {labeled_adaptive.max()}")

# Visualize boundaries overlaid on original
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
axes[0].imshow(img)
axes[0].contour(binary_clean, colors="red", linewidths=0.8)
axes[0].set_title(f"Otsu ({labeled_otsu.max()} colonies)")
axes[1].imshow(img)
axes[1].contour(binary_adaptive, colors="cyan", linewidths=0.8)
axes[1].set_title(f"Adaptive ({labeled_adaptive.max()} colonies)")
axes[2].imshow(img)
axes[2].contour(edges_clean, colors="lime", linewidths=0.8)
axes[2].set_title("Canny Edge Detection")
for ax in axes:
    ax.axis("off")
plt.tight_layout()
plt.savefig("colony_boundaries.png", dpi=150)
```

---

## 3. Area/Diameter Measurement from Binary Masks

```python
import numpy as np
from skimage import io, color, filters, morphology, measure
import pandas as pd
import matplotlib.pyplot as plt

img = io.imread("colony_plate.png")
gray = color.rgb2gray(img) if img.ndim == 3 else img.astype(float)

# Segment colonies
thresh = filters.threshold_otsu(gray)
binary = gray < thresh
binary = morphology.remove_small_objects(binary, min_size=100)
binary = morphology.binary_fill_holes(binary)
labeled = measure.label(binary)

# Calibration: pixels to physical units
# Measure a known reference (e.g., petri dish is 85mm diameter)
plate_diameter_mm = 85.0
plate_diameter_px = max(img.shape[:2])  # approximate
px_per_mm = plate_diameter_px / plate_diameter_mm
mm2_per_px2 = (1 / px_per_mm) ** 2
print(f"Scale: {px_per_mm:.1f} pixels/mm")

# Measure properties of each colony
props = measure.regionprops(labeled, intensity_image=gray)
colony_data = []
for prop in props:
    area_px = prop.area
    area_mm2 = area_px * mm2_per_px2
    # Equivalent diameter: diameter of circle with same area
    equiv_diam_px = prop.equivalent_diameter
    equiv_diam_mm = equiv_diam_px / px_per_mm
    # Perimeter and circularity (1.0 = perfect circle)
    perimeter_px = prop.perimeter
    circularity = (4 * np.pi * area_px) / (perimeter_px ** 2) if perimeter_px > 0 else 0
    colony_data.append({
        "label": prop.label,
        "area_px": area_px,
        "area_mm2": round(area_mm2, 3),
        "diameter_mm": round(equiv_diam_mm, 3),
        "circularity": round(circularity, 3),
        "centroid_y": round(prop.centroid[0], 1),
        "centroid_x": round(prop.centroid[1], 1),
        "mean_intensity": round(prop.mean_intensity, 4)
    })

df = pd.DataFrame(colony_data)
print(f"\nMeasured {len(df)} colonies:")
print(f"  Area: {df['area_mm2'].mean():.2f} +/- {df['area_mm2'].std():.2f} mm²")
print(f"  Diameter: {df['diameter_mm'].mean():.2f} +/- {df['diameter_mm'].std():.2f} mm")
print(f"  Circularity: {df['circularity'].mean():.3f} +/- {df['circularity'].std():.3f}")
print(df.describe().round(3))

# Save measurements
df.to_csv("colony_measurements.csv", index=False)

# Visualization: annotated colonies with measurements
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(img)
for _, row in df.iterrows():
    ax.annotate(
        f"{row['diameter_mm']:.1f}mm",
        (row["centroid_x"], row["centroid_y"]),
        color="yellow", fontsize=7, ha="center", fontweight="bold"
    )
ax.contour(binary, colors="red", linewidths=0.5)
ax.set_title(f"Colony Measurements (n={len(df)})")
ax.axis("off")
plt.tight_layout()
plt.savefig("colony_measurements.png", dpi=150)
```

---

## 4. Swarming Motility Quantification (Radial Distance from Center)

```python
import numpy as np
from skimage import io, color, filters, morphology, measure
import matplotlib.pyplot as plt
import pandas as pd

img = io.imread("swarm_plate.png")
gray = color.rgb2gray(img) if img.ndim == 3 else img.astype(float)

# Segment the swarm zone (colony + swarming area)
thresh = filters.threshold_otsu(gray)
binary = gray < thresh
binary = morphology.binary_fill_holes(binary)
binary = morphology.remove_small_objects(binary, min_size=500)

# Find the inoculation center (centroid of the largest connected component)
labeled = measure.label(binary)
props = measure.regionprops(labeled)
largest = max(props, key=lambda p: p.area)
center_y, center_x = largest.centroid
print(f"Inoculation center: ({center_x:.0f}, {center_y:.0f})")

# Measure radial distances from center to swarm edge
# Sample angles around 360 degrees
n_angles = 360
angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)
radial_distances = []

for angle in angles:
    # Walk outward from center along this angle
    max_radius = min(img.shape[:2]) // 2
    for r in range(1, max_radius):
        y = int(center_y + r * np.sin(angle))
        x = int(center_x + r * np.cos(angle))
        # Check bounds
        if y < 0 or y >= binary.shape[0] or x < 0 or x >= binary.shape[1]:
            radial_distances.append(r - 1)
            break
        if not binary[y, x]:
            radial_distances.append(r - 1)
            break
    else:
        radial_distances.append(max_radius)

radial_distances = np.array(radial_distances)

# Convert to mm (using plate diameter calibration)
plate_diameter_mm = 85.0
px_per_mm = max(img.shape[:2]) / plate_diameter_mm
radial_mm = radial_distances / px_per_mm

# Summary statistics
print(f"\nSwarming Motility Quantification:")
print(f"  Mean radial distance: {radial_mm.mean():.2f} mm")
print(f"  Max radial distance: {radial_mm.max():.2f} mm")
print(f"  Min radial distance: {radial_mm.min():.2f} mm")
print(f"  Std: {radial_mm.std():.2f} mm")
print(f"  Swarming area: {largest.area * (1/px_per_mm)**2:.2f} mm²")

# Asymmetry index: std/mean (0 = perfectly symmetric swarming)
asymmetry = radial_mm.std() / radial_mm.mean()
print(f"  Asymmetry index: {asymmetry:.3f}")

# Polar plot of swarming radius
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
# Radial profile
ax_polar = fig.add_subplot(121, projection="polar")
ax_polar.plot(angles, radial_mm, "b-", linewidth=0.8)
ax_polar.fill(angles, radial_mm, alpha=0.2)
ax_polar.set_title("Swarming Radial Profile")
# Overlay on image
axes[1].imshow(img)
axes[1].contour(binary, colors="red", linewidths=1)
axes[1].plot(center_x, center_y, "r+", markersize=15, markeredgewidth=2)
# Draw radial lines at 0, 90, 180, 270 degrees
for i, angle in enumerate([0, np.pi/2, np.pi, 3*np.pi/2]):
    r = radial_distances[int(angle / (2*np.pi) * n_angles)]
    end_y = center_y + r * np.sin(angle)
    end_x = center_x + r * np.cos(angle)
    axes[1].plot([center_x, end_x], [center_y, end_y], "y-", linewidth=1)
axes[1].set_title(f"Swarm Zone (mean radius = {radial_mm.mean():.1f} mm)")
axes[1].axis("off")
plt.tight_layout()
plt.savefig("swarming_motility.png", dpi=150)
```

---

## 5. Colony Counting in Plate Images

```python
import numpy as np
from skimage import io, color, filters, morphology, measure, segmentation
import matplotlib.pyplot as plt

img = io.imread("cfu_plate.png")
gray = color.rgb2gray(img) if img.ndim == 3 else img.astype(float)

# Enhance contrast for colony detection
from skimage.exposure import equalize_adapthist
gray_eq = equalize_adapthist(gray, clip_limit=0.02)

# Threshold to detect colonies (dark spots on light agar)
thresh = filters.threshold_otsu(gray_eq)
binary = gray_eq < thresh

# Morphological cleanup
binary = morphology.remove_small_objects(binary, min_size=50)   # remove noise
binary = morphology.binary_fill_holes(binary)                    # fill holes

# Watershed segmentation to separate touching colonies
from scipy import ndimage
distance = ndimage.distance_transform_edt(binary)
from skimage.feature import peak_local_max
# Find local maxima in distance map (colony centers)
local_max = peak_local_max(
    distance,
    min_distance=15,          # minimum distance between colony centers
    threshold_abs=5,          # minimum distance value to be a peak
    labels=binary
)
# Create markers for watershed
markers = np.zeros_like(binary, dtype=int)
for i, (y, x) in enumerate(local_max):
    markers[y, x] = i + 1
markers = morphology.dilation(markers, morphology.disk(3))

# Apply watershed
labels = segmentation.watershed(-distance, markers, mask=binary)
n_colonies = labels.max()
print(f"Colony count: {n_colonies}")

# Filter by size to remove artifacts
props = measure.regionprops(labels)
min_area = 100    # minimum colony area in pixels
max_area = 50000  # maximum colony area (exclude plate edges)
valid_colonies = [p for p in props if min_area <= p.area <= max_area]
print(f"Valid colonies (area {min_area}-{max_area} px): {len(valid_colonies)}")

# Area distribution
areas = [p.area for p in valid_colonies]
print(f"Colony area: mean = {np.mean(areas):.0f} px, "
      f"median = {np.median(areas):.0f} px, "
      f"std = {np.std(areas):.0f} px")

# Visualization with numbered colonies
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
axes[0].imshow(img)
axes[0].set_title("Original")
axes[1].imshow(binary, cmap="gray")
axes[1].set_title("Thresholded")
axes[2].imshow(segmentation.mark_boundaries(img, labels, color=(1, 0, 0)))
for prop in valid_colonies[:50]:  # annotate first 50
    y, x = prop.centroid
    axes[2].text(x, y, str(prop.label), color="yellow", fontsize=5,
                 ha="center", va="center", fontweight="bold")
axes[2].set_title(f"Watershed Segmented ({len(valid_colonies)} colonies)")
for ax in axes:
    ax.axis("off")
plt.tight_layout()
plt.savefig("colony_counting.png", dpi=150)
```

---

## 6. Color-Based Classification (RGB/HSV Analysis)

```python
import numpy as np
from skimage import io, color, filters, morphology, measure
import pandas as pd
import matplotlib.pyplot as plt

img = io.imread("colored_colonies.png")
gray = color.rgb2gray(img)

# Segment colonies first
thresh = filters.threshold_otsu(gray)
binary = gray < thresh
binary = morphology.remove_small_objects(binary, min_size=100)
binary = morphology.binary_fill_holes(binary)
labeled = measure.label(binary)

# Convert to HSV color space for color classification
hsv = color.rgb2hsv(img)

# Analyze color of each colony
props = measure.regionprops(labeled)
colony_colors = []

for prop in props:
    mask = labeled == prop.label
    # Extract mean RGB values within colony mask
    r_mean = img[mask, 0].mean()
    g_mean = img[mask, 1].mean()
    b_mean = img[mask, 2].mean()
    # Extract HSV values
    h_mean = hsv[mask, 0].mean()    # hue: 0-1 (mapped from 0-360)
    s_mean = hsv[mask, 1].mean()    # saturation: 0-1
    v_mean = hsv[mask, 2].mean()    # value (brightness): 0-1

    # Classify colony color based on HSV ranges
    if s_mean < 0.15:
        colony_type = "white"           # low saturation = achromatic
    elif h_mean < 0.05 or h_mean > 0.95:
        colony_type = "red"             # red wraps around 0/1
    elif 0.05 <= h_mean < 0.18:
        colony_type = "yellow/orange"
    elif 0.18 <= h_mean < 0.45:
        colony_type = "green"
    elif 0.45 <= h_mean < 0.70:
        colony_type = "blue"
    else:
        colony_type = "purple"

    colony_colors.append({
        "label": prop.label,
        "area_px": prop.area,
        "R": round(r_mean, 1), "G": round(g_mean, 1), "B": round(b_mean, 1),
        "H": round(h_mean, 3), "S": round(s_mean, 3), "V": round(v_mean, 3),
        "color_class": colony_type
    })

df = pd.DataFrame(colony_colors)
print("Colony Color Classification:")
print(df["color_class"].value_counts())
print(f"\nTotal colonies: {len(df)}")

# Color distribution plot
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# HSV scatter: Hue vs Saturation
scatter = axes[0].scatter(df["H"], df["S"], c=df[["R", "G", "B"]].values / 255,
                          s=df["area_px"] / 50, alpha=0.7, edgecolors="black", linewidths=0.3)
axes[0].set_xlabel("Hue")
axes[0].set_ylabel("Saturation")
axes[0].set_title("Colony Colors (HSV space)")

# Color class bar chart
color_map = {"white": "lightgray", "red": "red", "yellow/orange": "orange",
             "green": "green", "blue": "blue", "purple": "purple"}
counts = df["color_class"].value_counts()
bars = axes[1].bar(counts.index, counts.values,
                   color=[color_map.get(c, "gray") for c in counts.index],
                   edgecolor="black")
axes[1].set_title("Colony Count by Color")
axes[1].set_ylabel("Count")

# Annotated image
axes[2].imshow(img)
for _, row in df.iterrows():
    prop = props[row["label"] - 1]
    y, x = prop.centroid
    axes[2].plot(x, y, ".", color=color_map.get(row["color_class"], "gray"),
                 markersize=8, markeredgecolor="black", markeredgewidth=0.5)
axes[2].set_title("Color Classification Overlay")
axes[2].axis("off")

plt.tight_layout()
plt.savefig("colony_color_classification.png", dpi=150)
df.to_csv("colony_color_data.csv", index=False)
```

---

## 7. Growth Curve Fitting (Logistic Model)

```python
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

# Load OD600 time-series data (columns: time_h, od600, condition)
df = pd.read_csv("growth_curves.csv")

def logistic_growth(t, N0, K, r, lag):
    """4-parameter logistic growth model.
    N0: initial population, K: carrying capacity,
    r: growth rate, lag: lag time before exponential growth.
    """
    return K / (1 + ((K - N0) / N0) * np.exp(-r * (t - lag)))

def gompertz_growth(t, A, mu, lam):
    """Gompertz growth model (asymmetric sigmoid).
    A: maximum OD, mu: max growth rate, lam: lag time.
    """
    return A * np.exp(-np.exp((mu * np.e / A) * (lam - t) + 1))

# Fit each condition separately
conditions = df["condition"].unique()
results = []

fig, axes = plt.subplots(1, len(conditions), figsize=(6 * len(conditions), 5))
if len(conditions) == 1:
    axes = [axes]

for i, cond in enumerate(conditions):
    subset = df[df["condition"] == cond].sort_values("time_h")
    t = subset["time_h"].values
    od = subset["od600"].values

    # Fit logistic model with reasonable initial guesses
    p0 = [od.min() + 0.01, od.max(), 0.5, t[np.argmax(np.gradient(od))] / 2]
    bounds = ([0, 0, 0, 0], [1, 10, 5, t.max()])
    try:
        popt, pcov = curve_fit(logistic_growth, t, od, p0=p0, bounds=bounds, maxfev=10000)
        N0, K, r, lag = popt
        perr = np.sqrt(np.diag(pcov))

        # Goodness of fit
        y_pred = logistic_growth(t, *popt)
        r_sq = 1 - np.sum((od - y_pred)**2) / np.sum((od - od.mean())**2)
        doubling_time = np.log(2) / r

        results.append({
            "condition": cond,
            "N0": round(N0, 4), "K": round(K, 4),
            "growth_rate": round(r, 4), "lag_time_h": round(lag, 2),
            "doubling_time_h": round(doubling_time, 2),
            "R_squared": round(r_sq, 4)
        })
        print(f"\n{cond}:")
        print(f"  Carrying capacity (K): {K:.4f}")
        print(f"  Growth rate (r): {r:.4f} h⁻¹")
        print(f"  Doubling time: {doubling_time:.2f} h")
        print(f"  Lag phase: {lag:.2f} h")
        print(f"  R²: {r_sq:.4f}")

        # Plot
        t_fine = np.linspace(0, t.max(), 200)
        axes[i].scatter(t, od, s=20, alpha=0.6, label="Data")
        axes[i].plot(t_fine, logistic_growth(t_fine, *popt), "r-", linewidth=2, label="Logistic fit")
        axes[i].axvline(lag, color="gray", linestyle="--", alpha=0.5, label=f"Lag = {lag:.1f}h")
        axes[i].axhline(K, color="green", linestyle=":", alpha=0.5, label=f"K = {K:.3f}")
    except RuntimeError:
        print(f"\n{cond}: Fitting failed")
        axes[i].scatter(t, od, s=20, alpha=0.6)

    axes[i].set_xlabel("Time (hours)")
    axes[i].set_ylabel("OD600")
    axes[i].set_title(f"{cond}")
    axes[i].legend(fontsize=8)

plt.tight_layout()
plt.savefig("growth_curves_fitted.png", dpi=150)

results_df = pd.DataFrame(results)
print(f"\n\nGrowth Parameters Summary:\n{results_df.to_string(index=False)}")
results_df.to_csv("growth_parameters.csv", index=False)
```

---

## 8. Time-Series Colony Expansion Analysis

```python
import numpy as np
import pandas as pd
from skimage import io, color, filters, morphology, measure
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

# Process a series of plate images taken at different timepoints
image_dir = "timelapse_images/"
timepoints_h = [0, 2, 4, 6, 8, 12, 16, 20, 24, 36, 48]
image_files = [f"plate_t{t}h.png" for t in timepoints_h]

expansion_data = []

for t, fname in zip(timepoints_h, image_files):
    fpath = os.path.join(image_dir, fname)
    if not os.path.exists(fpath):
        print(f"  Skipping {fname} (not found)")
        continue

    img = io.imread(fpath)
    gray = color.rgb2gray(img) if img.ndim == 3 else img.astype(float)

    # Segment colony
    thresh = filters.threshold_otsu(gray)
    binary = gray < thresh
    binary = morphology.binary_fill_holes(binary)
    binary = morphology.remove_small_objects(binary, min_size=100)
    labeled = measure.label(binary)

    if labeled.max() == 0:
        expansion_data.append({"time_h": t, "area_px": 0, "diameter_px": 0})
        continue

    # Find largest connected component (the main colony)
    props = measure.regionprops(labeled)
    largest = max(props, key=lambda p: p.area)

    expansion_data.append({
        "time_h": t,
        "area_px": largest.area,
        "diameter_px": largest.equivalent_diameter,
        "perimeter_px": largest.perimeter,
        "centroid_y": largest.centroid[0],
        "centroid_x": largest.centroid[1]
    })
    print(f"  t={t}h: area={largest.area} px, diameter={largest.equivalent_diameter:.1f} px")

df = pd.DataFrame(expansion_data)

# Convert pixels to mm
plate_diameter_mm = 85.0
px_per_mm = max(io.imread(os.path.join(image_dir, image_files[0])).shape[:2]) / plate_diameter_mm
df["area_mm2"] = df["area_px"] * (1 / px_per_mm) ** 2
df["diameter_mm"] = df["diameter_px"] / px_per_mm

# Fit expansion rate: diameter vs time (linear phase)
# Colony expansion is often linear after initial lag
from scipy.stats import linregress
# Find the linear growth phase (exclude lag and stationary)
growth_phase = df[(df["area_mm2"] > 0) & (df["time_h"] > 2)]  # skip early lag
if len(growth_phase) > 2:
    slope, intercept, r_val, p_val, se = linregress(
        growth_phase["time_h"], growth_phase["diameter_mm"]
    )
    expansion_rate = slope  # mm per hour
    print(f"\nExpansion rate: {expansion_rate:.3f} mm/h (R²={r_val**2:.4f})")

# Plot expansion dynamics
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Area over time
axes[0].plot(df["time_h"], df["area_mm2"], "bo-", markersize=6)
axes[0].set_xlabel("Time (hours)")
axes[0].set_ylabel("Colony Area (mm²)")
axes[0].set_title("Colony Area Expansion")

# Diameter over time with linear fit
axes[1].plot(df["time_h"], df["diameter_mm"], "ro-", markersize=6, label="Observed")
if len(growth_phase) > 2:
    t_fit = np.linspace(0, df["time_h"].max(), 100)
    axes[1].plot(t_fit, slope * t_fit + intercept, "k--",
                 label=f"Linear fit ({expansion_rate:.3f} mm/h)")
axes[1].set_xlabel("Time (hours)")
axes[1].set_ylabel("Colony Diameter (mm)")
axes[1].set_title("Colony Diameter Expansion")
axes[1].legend()

# Expansion rate (derivative)
if len(df) > 2:
    dt = np.diff(df["time_h"].values)
    d_area = np.diff(df["area_mm2"].values)
    rate = d_area / dt
    t_mid = (df["time_h"].values[:-1] + df["time_h"].values[1:]) / 2
    axes[2].plot(t_mid, rate, "gs-", markersize=6)
    axes[2].set_xlabel("Time (hours)")
    axes[2].set_ylabel("Expansion Rate (mm²/h)")
    axes[2].set_title("Instantaneous Expansion Rate")

plt.tight_layout()
plt.savefig("colony_expansion_analysis.png", dpi=150)
df.to_csv("colony_expansion_data.csv", index=False)
```

---

## 9. Statistical Comparison of Colony Sizes Across Conditions

```python
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Load colony measurements from multiple conditions
# Expected columns: condition, colony_id, area_mm2, diameter_mm
df = pd.read_csv("colony_measurements_all.csv")
conditions = df["condition"].unique()
print(f"Conditions: {conditions}")
print(f"Total colonies: {len(df)}")

# Summary statistics per condition
summary = df.groupby("condition").agg(
    n=("area_mm2", "count"),
    mean_area=("area_mm2", "mean"),
    std_area=("area_mm2", "std"),
    median_area=("area_mm2", "median"),
    mean_diam=("diameter_mm", "mean"),
    std_diam=("diameter_mm", "std")
).round(3)
print(f"\nSummary:\n{summary}")

# --- Pairwise comparisons ---
if len(conditions) == 2:
    # Two conditions: t-test (parametric) and Mann-Whitney (non-parametric)
    a = df[df["condition"] == conditions[0]]["area_mm2"]
    b = df[df["condition"] == conditions[1]]["area_mm2"]

    # Check normality first
    _, p_norm_a = stats.shapiro(a[:5000])
    _, p_norm_b = stats.shapiro(b[:5000])
    print(f"\nNormality (Shapiro-Wilk): {conditions[0]} p={p_norm_a:.4f}, "
          f"{conditions[1]} p={p_norm_b:.4f}")

    # Welch's t-test (does not assume equal variances)
    t_stat, t_p = stats.ttest_ind(a, b, equal_var=False)
    print(f"Welch t-test: t={t_stat:.3f}, p={t_p:.4f}")

    # Mann-Whitney U (non-parametric)
    u_stat, u_p = stats.mannwhitneyu(a, b, alternative="two-sided")
    print(f"Mann-Whitney U: U={u_stat:.0f}, p={u_p:.4f}")

    # Effect size: Cohen's d
    pooled_std = np.sqrt((a.std()**2 + b.std()**2) / 2)
    cohens_d = (a.mean() - b.mean()) / pooled_std
    print(f"Cohen's d: {cohens_d:.3f}")

elif len(conditions) > 2:
    # Multiple conditions: ANOVA + post-hoc
    groups = [df[df["condition"] == c]["area_mm2"].values for c in conditions]

    # One-way ANOVA
    f_stat, anova_p = stats.f_oneway(*groups)
    print(f"\nOne-way ANOVA: F={f_stat:.3f}, p={anova_p:.4f}")

    # Kruskal-Wallis (non-parametric alternative)
    h_stat, kw_p = stats.kruskal(*groups)
    print(f"Kruskal-Wallis: H={h_stat:.3f}, p={kw_p:.4f}")

    # Post-hoc pairwise comparisons with Bonferroni correction
    n_comparisons = len(conditions) * (len(conditions) - 1) // 2
    print(f"\nPost-hoc pairwise t-tests (Bonferroni, {n_comparisons} comparisons):")
    for i in range(len(conditions)):
        for j in range(i + 1, len(conditions)):
            a = df[df["condition"] == conditions[i]]["area_mm2"]
            b = df[df["condition"] == conditions[j]]["area_mm2"]
            _, p = stats.ttest_ind(a, b, equal_var=False)
            p_adj = min(p * n_comparisons, 1.0)
            sig = "***" if p_adj < 0.001 else "**" if p_adj < 0.01 else "*" if p_adj < 0.05 else "ns"
            print(f"  {conditions[i]} vs {conditions[j]}: "
                  f"p_adj={p_adj:.4f} {sig}")

# Visualization
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Box plot
bp = axes[0].boxplot(
    [df[df["condition"] == c]["area_mm2"].values for c in conditions],
    labels=conditions, patch_artist=True
)
colors = plt.cm.Set2(np.linspace(0, 1, len(conditions)))
for patch, c in zip(bp["boxes"], colors):
    patch.set_facecolor(c)
axes[0].set_ylabel("Area (mm²)")
axes[0].set_title("Colony Size Distribution")

# Violin plot
parts = axes[1].violinplot(
    [df[df["condition"] == c]["area_mm2"].values for c in conditions],
    showmeans=True, showmedians=True
)
axes[1].set_xticks(range(1, len(conditions) + 1))
axes[1].set_xticklabels(conditions)
axes[1].set_ylabel("Area (mm²)")
axes[1].set_title("Colony Size Violin Plot")

# Histogram overlay
for c, col in zip(conditions, colors):
    data = df[df["condition"] == c]["area_mm2"]
    axes[2].hist(data, bins=20, alpha=0.5, color=col, label=c, density=True)
axes[2].set_xlabel("Area (mm²)")
axes[2].set_ylabel("Density")
axes[2].set_title("Area Distribution by Condition")
axes[2].legend()

plt.tight_layout()
plt.savefig("colony_size_comparison.png", dpi=150)
```

---

## 10. Batch Processing Multiple Plate Images

```python
import numpy as np
import pandas as pd
from skimage import io, color, filters, morphology, measure
import matplotlib.pyplot as plt
import os
import glob

# Batch process all plate images in a directory
image_dir = "plate_images/"
# Supported formats
image_files = sorted(
    glob.glob(os.path.join(image_dir, "*.png")) +
    glob.glob(os.path.join(image_dir, "*.jpg")) +
    glob.glob(os.path.join(image_dir, "*.tif"))
)
print(f"Found {len(image_files)} plate images")

# Parse metadata from filenames: e.g., "WT_rep1_24h.png"
def parse_filename(filepath):
    """Extract condition, replicate, and timepoint from filename."""
    basename = os.path.splitext(os.path.basename(filepath))[0]
    parts = basename.split("_")
    return {
        "condition": parts[0] if len(parts) > 0 else "unknown",
        "replicate": parts[1] if len(parts) > 1 else "rep1",
        "timepoint": parts[2] if len(parts) > 2 else "unknown"
    }

# Calibration
plate_diam_mm = 85.0

all_results = []

for fpath in image_files:
    meta = parse_filename(fpath)
    img = io.imread(fpath)
    gray = color.rgb2gray(img) if img.ndim == 3 else img.astype(float)

    px_per_mm = max(gray.shape) / plate_diam_mm

    # Segment
    thresh = filters.threshold_otsu(gray)
    binary = gray < thresh
    binary = morphology.remove_small_objects(binary, min_size=100)
    binary = morphology.binary_fill_holes(binary)
    labeled = measure.label(binary)

    # Measure each colony
    props = measure.regionprops(labeled, intensity_image=gray)
    for prop in props:
        area_mm2 = prop.area / (px_per_mm ** 2)
        diam_mm = prop.equivalent_diameter / px_per_mm
        circularity = (4 * np.pi * prop.area) / (prop.perimeter ** 2) if prop.perimeter > 0 else 0

        all_results.append({
            "file": os.path.basename(fpath),
            "condition": meta["condition"],
            "replicate": meta["replicate"],
            "timepoint": meta["timepoint"],
            "colony_id": prop.label,
            "area_mm2": round(area_mm2, 3),
            "diameter_mm": round(diam_mm, 3),
            "circularity": round(circularity, 3),
            "mean_intensity": round(prop.mean_intensity, 4)
        })

    print(f"  {os.path.basename(fpath)}: {len(props)} colonies detected")

df = pd.DataFrame(all_results)
print(f"\nTotal colonies measured: {len(df)}")
print(f"Conditions: {df['condition'].unique()}")
print(f"Replicates per condition:\n{df.groupby('condition')['replicate'].nunique()}")

# Aggregate: mean colony count and size per condition x timepoint
agg = df.groupby(["condition", "timepoint", "replicate"]).agg(
    n_colonies=("colony_id", "count"),
    mean_area=("area_mm2", "mean"),
    total_area=("area_mm2", "sum")
).reset_index()
print(f"\nAggregated results:\n{agg.round(3)}")

# Summary across replicates
summary = agg.groupby(["condition", "timepoint"]).agg(
    mean_count=("n_colonies", "mean"),
    sem_count=("n_colonies", "sem"),
    mean_area=("mean_area", "mean"),
    sem_area=("mean_area", "sem")
).reset_index()
print(f"\nSummary (across replicates):\n{summary.round(3)}")

# Save results
df.to_csv("batch_colony_measurements.csv", index=False)
agg.to_csv("batch_colony_summary.csv", index=False)

# Quick overview plot: colony count by condition
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for cond in df["condition"].unique():
    cond_data = agg[agg["condition"] == cond]
    axes[0].bar(cond, cond_data["n_colonies"].mean(), yerr=cond_data["n_colonies"].sem(),
                capsize=5, alpha=0.7, label=cond)
axes[0].set_ylabel("Colony Count")
axes[0].set_title("Mean Colony Count by Condition")

# Colony size distribution by condition
conditions = df["condition"].unique()
data_per_cond = [df[df["condition"] == c]["area_mm2"].values for c in conditions]
axes[1].boxplot(data_per_cond, labels=conditions)
axes[1].set_ylabel("Area (mm²)")
axes[1].set_title("Colony Size Distribution")

plt.tight_layout()
plt.savefig("batch_analysis_overview.png", dpi=150)
print("\nBatch processing complete")
```

---

## 11. Biofilm Ring / Zone of Inhibition Measurement

```python
import numpy as np
from skimage import io, color, filters, morphology, measure
import matplotlib.pyplot as plt

img = io.imread("inhibition_zone.png")
gray = color.rgb2gray(img) if img.ndim == 3 else img.astype(float)

# Detect the clear zone (zone of inhibition) around antibiotic disk
# The zone is brighter than the surrounding bacterial lawn
thresh = filters.threshold_otsu(gray)
zone_mask = gray > thresh   # clear zone is brighter
zone_mask = morphology.binary_fill_holes(zone_mask)
zone_mask = morphology.remove_small_objects(zone_mask, min_size=500)

# Find the antibiotic disk (center of the zone)
labeled = measure.label(zone_mask)
props = measure.regionprops(labeled)
if len(props) == 0:
    print("No zone detected")
else:
    largest_zone = max(props, key=lambda p: p.area)
    center_y, center_x = largest_zone.centroid
    zone_area = largest_zone.area

    # Measure zone diameter using radial sampling
    n_angles = 360
    angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)
    radii = []
    for angle in angles:
        for r in range(1, min(gray.shape) // 2):
            y = int(center_y + r * np.sin(angle))
            x = int(center_x + r * np.cos(angle))
            if (y < 0 or y >= gray.shape[0] or x < 0 or x >= gray.shape[1]
                    or not zone_mask[y, x]):
                radii.append(r - 1)
                break

    radii = np.array(radii)
    # Convert to mm
    plate_diameter_mm = 85.0
    px_per_mm = max(gray.shape) / plate_diameter_mm
    diameter_mm = 2 * radii.mean() / px_per_mm

    print(f"Zone of inhibition:")
    print(f"  Center: ({center_x:.0f}, {center_y:.0f})")
    print(f"  Mean diameter: {diameter_mm:.1f} mm")
    print(f"  Min diameter: {2 * radii.min() / px_per_mm:.1f} mm")
    print(f"  Max diameter: {2 * radii.max() / px_per_mm:.1f} mm")

    # Visualize
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(img)
    ax.contour(zone_mask, colors="lime", linewidths=1.5)
    ax.plot(center_x, center_y, "r+", markersize=20, markeredgewidth=2)
    circle = plt.Circle((center_x, center_y), radii.mean(),
                         fill=False, color="yellow", linewidth=1.5, linestyle="--")
    ax.add_patch(circle)
    ax.set_title(f"Zone of Inhibition: {diameter_mm:.1f} mm diameter")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("inhibition_zone_measured.png", dpi=150)
```

---

## 12. Morphological Classification of Colony Types

```python
import numpy as np
import pandas as pd
from skimage import io, color, filters, morphology, measure
import matplotlib.pyplot as plt

img = io.imread("mixed_colonies.png")
gray = color.rgb2gray(img) if img.ndim == 3 else img.astype(float)

# Segment colonies
thresh = filters.threshold_otsu(gray)
binary = gray < thresh
binary = morphology.remove_small_objects(binary, min_size=100)
binary = morphology.binary_fill_holes(binary)
labeled = measure.label(binary)

# Extract morphological features for classification
props = measure.regionprops(labeled, intensity_image=gray)
morph_data = []

for prop in props:
    area = prop.area
    perim = prop.perimeter
    circularity = (4 * np.pi * area) / (perim ** 2) if perim > 0 else 0
    # Solidity: ratio of area to convex hull area (1.0 = convex)
    solidity = prop.solidity
    # Eccentricity: 0 = circle, 1 = line
    eccentricity = prop.eccentricity
    # Extent: ratio of area to bounding box area
    extent = prop.extent
    # Texture proxy: intensity variance within colony
    mask = labeled == prop.label
    intensity_var = gray[mask].var()

    # Classify morphology
    if circularity > 0.85 and solidity > 0.95:
        morph_type = "round_smooth"      # typical colony
    elif circularity > 0.7 and solidity < 0.85:
        morph_type = "irregular"          # rough/lobate edges
    elif eccentricity > 0.85:
        morph_type = "elongated"          # swarming tendril
    elif solidity < 0.7:
        morph_type = "branching"          # dendritic growth
    elif circularity < 0.5:
        morph_type = "filamentous"        # fuzzy/filamentous
    else:
        morph_type = "other"

    morph_data.append({
        "label": prop.label,
        "area": area,
        "circularity": round(circularity, 3),
        "solidity": round(solidity, 3),
        "eccentricity": round(eccentricity, 3),
        "extent": round(extent, 3),
        "intensity_var": round(intensity_var, 5),
        "morphology": morph_type
    })

df = pd.DataFrame(morph_data)
print("Colony Morphology Classification:")
print(df["morphology"].value_counts())
print(f"\nMorphological Feature Ranges:")
for col in ["circularity", "solidity", "eccentricity"]:
    print(f"  {col}: {df[col].min():.3f} - {df[col].max():.3f} "
          f"(mean={df[col].mean():.3f})")

# Feature scatter plot
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
morph_colors = {"round_smooth": "green", "irregular": "orange",
                "elongated": "blue", "branching": "red",
                "filamentous": "purple", "other": "gray"}

for morph, c in morph_colors.items():
    subset = df[df["morphology"] == morph]
    if len(subset) > 0:
        axes[0].scatter(subset["circularity"], subset["solidity"],
                        c=c, label=morph, s=40, alpha=0.7)
        axes[1].scatter(subset["eccentricity"], subset["extent"],
                        c=c, label=morph, s=40, alpha=0.7)

axes[0].set_xlabel("Circularity")
axes[0].set_ylabel("Solidity")
axes[0].set_title("Circularity vs Solidity")
axes[0].legend(fontsize=8)
axes[1].set_xlabel("Eccentricity")
axes[1].set_ylabel("Extent")
axes[1].set_title("Eccentricity vs Extent")

# Annotated image
axes[2].imshow(img)
for _, row in df.iterrows():
    prop = props[row["label"] - 1]
    y, x = prop.centroid
    c = morph_colors.get(row["morphology"], "gray")
    axes[2].plot(x, y, "o", color=c, markersize=6, markeredgecolor="black",
                 markeredgewidth=0.5)
axes[2].set_title("Morphology Classification")
axes[2].axis("off")

plt.tight_layout()
plt.savefig("colony_morphology_classification.png", dpi=150)
df.to_csv("colony_morphology_data.csv", index=False)
```
