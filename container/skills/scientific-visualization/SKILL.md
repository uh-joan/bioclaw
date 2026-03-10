---
name: scientific-visualization
description: "Publication-quality scientific figures for journals. Domain expertise in figure design, color science, statistical display, and journal-specific formatting. Use when user mentions publication figure, journal figure, colorblind palette, figure for Nature, figure for Science, publication-quality plot, scientific figure, manuscript figure, make figure publishable, figure formatting, DPI requirements, multi-panel figure, figure checklist, volcano plot, survival curve, heatmap with dendrogram, forest plot, figure resolution, vector figure, TIFF figure, EPS figure, figure for Cell, figure for PLOS, figure for NEJM, figure for Lancet"
---

# Scientific Visualization Specialist

Domain expertise skill for creating publication-quality scientific figures. This is NOT a matplotlib/seaborn tutorial — it encodes the specialized knowledge of what makes figures meet journal standards, pass reviewer scrutiny, and communicate data with scientific rigor. Covers journal-specific formatting requirements, color science for accessibility, statistical display conventions, multi-panel layout expertise, and ready-to-use code templates for common life science figure types.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_scientific_visualization_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as figures are generated and refined
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Statistical modeling and hypothesis testing methodology -> use `statistical-modeling`
- Single-cell RNA-seq analysis pipelines (UMAP generation, clustering) -> use `single-cell-analysis`
- Differential expression analysis (generating DE results to plot) -> use `rnaseq-deseq2`
- Proteomics quantification and analysis -> use `proteomics-analysis`
- Chemical structure rendering and SAR visualization -> use `medicinal-chemistry`
- Interactive dashboards or web-based visualization -> not a publication figure task
- Presentation slides (PowerPoint/Keynote) -> different DPI and format requirements

## Cross-Reference: Other Skills

- **Statistical modeling, hypothesis testing, power analysis** -> use statistical-modeling skill
- **Single-cell clustering, UMAP/tSNE, cell type annotation** -> use single-cell-analysis skill
- **RNA-seq differential expression pipelines** -> use rnaseq-deseq2 skill
- **Proteomics quantification, TMT/LFQ analysis** -> use proteomics-analysis skill
- **Compound optimization, SAR tables** -> use medicinal-chemistry skill
- **Pathway enrichment visualization (after generating gene lists)** -> use gene-enrichment skill
- **Multi-omics integration figures** -> use multi-omics-integration skill

---

## 1. Journal Requirements Reference

### Universal Principles

- **Vector formats preferred** for all line art, graphs, and diagrams
- **Raster formats** only for photographic images (microscopy, gels, blots)
- **NEVER use JPEG/JPG** — lossy compression introduces artifacts
- **RGB color space** for submission; CMYK may be required for final print
- **Embed all fonts** in PDF/EPS files (set pdf.fonttype=42, ps.fonttype=42)
- **No hairline rules** — minimum 0.5 pt line width at final print size

### Quick Reference Table

```
Journal  | 1-col (mm) | 2-col (mm) | Line DPI  | Photo DPI | Font       | Panels    | Formats
---------+------------+------------+-----------+-----------+------------+-----------+------------------
Nature   | 89         | 183        | 600       | 300       | Arial      | a,b,c     | PDF/EPS/TIFF/PNG
Science  | 55         | 120        | 600-1200  | 300       | Helvetica  | A,B,C     | PDF/EPS/TIFF
Cell     | 85         | 174        | 1000      | 300       | Arial      | A,B,C 12pt| PDF/EPS/TIFF/PNG
PLOS     | 83         | 173        | 300-600   | 300       | Arial      | A,B,C     | PDF/EPS/TIFF/PNG
NEJM     | 86         | 178        | 1200      | 300       | Helvetica  | A,B,C     | EPS/PDF/TIFF
Lancet   | 79         | 168        | 1000      | 350       | Arial/TNR  | A,B,C     | EPS/TIFF
```

### Nature (Nature Research Journals)

```
Widths: single 89mm (3.50in), 1.5-col 120mm (4.72in), double 183mm (7.20in)
Line art: 600 DPI minimum (vector preferred). Photos: 300 DPI. Combo: 500 DPI.
Fonts: Arial/Helvetica/Times, minimum 5pt (7pt recommended) at final size.
Panel labels: LOWERCASE bold 8pt (a, b, c) — unique among major journals.
Formats: PDF, EPS, AI (vector); TIFF, PNG (raster). NEVER JPEG/GIF/BMP.
Rules: Scale bars on microscopy. No brightness adjustments that obscure bands.
Max 10MB per figure. RGB for digital. Colorblind-safe palettes recommended.
```

### Science (AAAS)

```
Widths: single 55mm (2.17in), double 120mm (4.72in), full page 174mm (6.85in)
Line art: 600 DPI min (1200 preferred). Photos: 300 DPI. Combo: 600 DPI.
Fonts: Helvetica or Arial ONLY, minimum 6pt at final size.
Panel labels: UPPERCASE bold (A, B, C).
Formats: PDF, EPS (preferred); TIFF. NEVER JPEG/GIF/BMP.
Rules: Very narrow single column (55mm) — design accordingly.
All text must be editable in vector files. No background shading on plots.
Figures MUST be interpretable in grayscale. Colorblind accessibility required.
```

### Cell (Cell Press)

```
Widths: single 85mm (3.35in), 1.5-col 114mm (4.49in), double 174mm (6.85in)
Line art: 1000 DPI minimum (HIGHEST requirement). Photos: 300 DPI. Combo: 600 DPI.
Fonts: Arial ONLY, minimum 6pt at final size.
Panel labels: UPPERCASE bold 12pt (A, B, C).
Formats: PDF, EPS, AI; TIFF (preferred raster), PNG. NEVER JPEG/Word-embedded.
Rules: White background required. Consistent font sizing across ALL panels.
RGB for initial submission, CMYK for final accepted manuscript.
```

### PLOS (PLOS ONE, PLOS Biology, etc.)

```
Widths: single 83mm (3.27in), 1.5-col 120mm (4.72in), double 173mm (6.81in)
Resolution: 300 DPI minimum for all (600 DPI recommended for line art).
Fonts: Arial/Times/Symbol, 6-12pt range at final size.
Panel labels: UPPERCASE (A, B, C).
Formats: PDF, EPS (preferred); TIFF, PNG. NEVER JPEG/GIF/BMP.
Rules: RGB required (no CMYK). Open access CC-BY license. White background.
Figure titles go in manuscript text, NOT in the figure. Max 10MB per figure.
```

### NEJM (New England Journal of Medicine)

```
Widths: single 86mm (3.39in), double 178mm (7.01in)
Line art: 1200 DPI minimum. Photos: 300 DPI. Combo: 600 DPI.
Fonts: Helvetica/Arial, minimum 8pt (HIGHEST font minimum).
Panel labels: UPPERCASE bold (A, B, C).
Formats: EPS (preferred), PDF; TIFF uncompressed. NEVER JPEG/PowerPoint.
Rules: NEJM art dept may redraw figures — provide raw data.
Clinical trials: CONSORT/STROBE flow diagrams. Kaplan-Meier: number-at-risk required.
Forest plots: standard format, diamond for summary estimate.
```

### The Lancet

```
Widths: single 79mm (3.11in — NARROWEST), double 168mm (6.61in)
Line art: 1000 DPI. Photos: 350 DPI. Combo: 600 DPI.
Fonts: Times New Roman (text), Arial (labels), minimum 6pt.
Panel labels: UPPERCASE (A, B, C).
Formats: EPS (preferred), PDF; TIFF. NEVER JPEG/Word-embedded.
Rules: Narrowest single column — plan layouts carefully. Max 8 panels per figure.
Kaplan-Meier: number-at-risk mandatory. No 3D effects or gradients.
```

---

## 2. Color Science for Publications

### The Okabe-Ito Palette (Gold Standard for Colorblind Safety)

Designed by vision scientists Masataka Okabe and Kei Ito (2002). Safe for deuteranopia, protanopia, and tritanopia. The **default palette for all categorical data** in publication figures.

```python
OKABE_ITO = {
    'blue':           '#0072B2',
    'orange':         '#E69F00',
    'bluish_green':   '#009E73',
    'vermillion':     '#D55E00',
    'sky_blue':       '#56B4E9',
    'reddish_purple': '#CC79A7',
    'yellow':         '#F0E442',  # low contrast on white — use sparingly
    'black':          '#000000',
}

# Recommended order for maximum distinguishability:
OKABE_ITO_ORDER = ['#0072B2', '#E69F00', '#009E73', '#D55E00',
                   '#56B4E9', '#CC79A7', '#F0E442', '#000000']
```

### Perceptually Uniform Sequential Colormaps

For continuous data (low to high). Equal data steps = equal perceived brightness steps.

```
viridis  — THE default. Blue-green-yellow. Prints well in grayscale. Colorblind-safe.
plasma   — Blue-purple-orange-yellow. Higher contrast. Use when viridis is taken.
cividis  — Blue-yellow only (2-hue). Maximum CVD safety. Designed for deuteranopia.
inferno  — Black-purple-red-yellow-white. Maximum perceptual range. Good for dark backgrounds.
magma    — Black-purple-pink-tan. Softer than inferno. Good for microscopy overlays.
```

### Diverging Colormaps

For data with a meaningful center (zero, baseline). Data diverges in two directions.

```
RdBu_r   — Red=up/positive, Blue=down/negative. Default for fold change, correlation.
PuOr     — Purple-orange. Use when RdBu is already taken.
BrBG     — Brown-bluegreen. Good for ecological data.

CRITICAL: Always center diverging colormaps at zero.
```

```python
import matplotlib.colors as mcolors
vmax = np.max(np.abs(data))
norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
plt.imshow(data, cmap='RdBu_r', norm=norm)
```

### Why NEVER Use Jet/Rainbow

Jet is **banned from serious scientific publications** because:
1. **Perceptual non-uniformity** — equal data steps produce wildly different perceived changes
2. **Luminance reversals** — bright-dark-bright creates phantom features
3. **Colorblind failure** — red-green transitions invisible to ~8% of males
4. **Grayscale destruction** — green and red map to similar grays
5. **Journal policy** — Nature, Science, Cell explicitly discourage/ban rainbow colormaps

Replace: jet/rainbow -> viridis (sequential) or RdBu_r (diverging)

### Color Choices by Data Type

```
Data type                    | Colormap choice           | Rationale
-----------------------------+---------------------------+---------------------------
Categorical (2-8 groups)     | Okabe-Ito discrete        | Colorblind-safe, distinct
Sequential continuous        | viridis, plasma, cividis   | Perceptually uniform
Diverging (centered at 0)    | RdBu_r, PuOr, BrBG       | Symmetric around midpoint
Binary (yes/no, up/down)     | Two Okabe-Ito colors      | Maximum contrast pair
Ordered categories           | Sequential subset          | Implies ordering
Expression intensity         | viridis or magma           | No misleading boundaries
Fold change / log2FC         | RdBu_r centered at 0      | Red=up, blue=down convention
Correlation coefficient      | RdBu_r, vmin=-1, vmax=1   | Symmetric diverging
P-value / significance       | Sequential (YlOrRd)       | Hot = more significant
```

### The Grayscale Test

**Every figure must work in grayscale.** Many readers print in B&W.

```python
from PIL import Image
img = Image.open('figure.png').convert('L')
img.save('figure_grayscale.png')
# CHECK: Can you still distinguish all data series?
```

### Redundant Encoding

Never rely on color alone. Layer multiple visual channels:

```python
styles = [
    {'color': '#0072B2', 'linestyle': '-',  'marker': 'o', 'label': 'Control'},
    {'color': '#E69F00', 'linestyle': '--', 'marker': 's', 'label': 'Treatment A'},
    {'color': '#009E73', 'linestyle': ':',  'marker': '^', 'label': 'Treatment B'},
    {'color': '#D55E00', 'linestyle': '-.', 'marker': 'D', 'label': 'Treatment C'},
]
for style, (x, y) in zip(styles, datasets):
    plt.plot(x, y, **style, linewidth=1.5, markersize=6)
```

---

## 3. Statistical Rigor in Figures

### Error Bars: Always Specify in Caption

```
SD      — Spread of data. Use when describing variability.
SEM     — Precision of mean (SD/sqrt(n)). DANGER: makes data look less variable.
95% CI  — THE BEST default. Non-overlap suggests p<0.05. Directly interpretable.
IQR     — Interquartile range. For non-parametric/skewed data, boxplots.
```

**Caption template:** "Error bars represent [SD|SEM|95% CI]. n=[X] biological replicates per group. Statistical comparison by [test]; *p<0.05, **p<0.01, ***p<0.001."

### Show Individual Data Points (Always)

Modern journals require or strongly prefer individual data points over bar charts alone.

```
BAD:  Bar chart + error bars only (hides n, distribution, outliers)
GOOD: Strip/swarm + summary statistic (individual points visible)
BEST: Violin + strip + box overlay (distribution + points + quartiles)
```

```python
import seaborn as sns
fig, ax = plt.subplots(figsize=(4, 5))
sns.violinplot(data=df, x='group', y='value', inner=None,
               color='lightgray', alpha=0.5, ax=ax)
sns.stripplot(data=df, x='group', y='value', size=4,
              jitter=0.2, alpha=0.7, palette=OKABE_ITO_ORDER, ax=ax)
sns.boxplot(data=df, x='group', y='value', width=0.3,
            showcaps=False, boxprops={'facecolor': 'none'},
            whiskerprops={'linewidth': 0}, ax=ax)
```

### Sample Size Must Always Be Visible

State n for every group: in caption, below x-axis labels "(n=12)", annotated on plot, or implied by visible data points (still state in caption).

### Significance Markers

```
ns: p >= 0.05 | *: p < 0.05 | **: p < 0.01 | ***: p < 0.001 | ****: p < 0.0001
```

```python
def add_significance_bracket(ax, x1, x2, y, p_value, dh=0.02, fs=10):
    if p_value >= 0.05: sig = 'ns'
    elif p_value < 0.0001: sig = '****'
    elif p_value < 0.001: sig = '***'
    elif p_value < 0.01: sig = '**'
    else: sig = '*'
    dy = dh * (ax.get_ylim()[1] - ax.get_ylim()[0])
    bar_y = y + dy
    ax.plot([x1, x1, x2, x2], [y, bar_y, bar_y, y], lw=1.0, color='black')
    ax.text((x1+x2)/2, bar_y, sig, ha='center', va='bottom', fontsize=fs)
```

### Y-Axis Zero Rule

Bar charts MUST start at zero — truncation exaggerates differences because bar height encodes absolute magnitude. Cutting the base makes small differences appear large.

```
Acceptable truncation (must justify in caption):
  - Data spans narrow range far from zero (e.g., body temperature 36-40C)
  - Log-scale data where zero is undefined
  - Time series where baseline is established by context

Never truncate:
  - Bar charts comparing group means
  - Stacked bar charts
  - Any chart where bar height implies magnitude

Always acceptable to truncate:
  - Line charts (slope/rate of change is the message, not absolute value)
  - Dot plots / scatter plots (no bar height to misrepresent)
  - Box plots / violin plots
```

### Choosing the Right Plot Type

```
Question                              | Plot type            | Why
--------------------------------------+----------------------+---------------------------
Compare means across groups           | Violin + strip       | Shows distribution + points
Show trend over time                  | Line plot            | Emphasizes temporal pattern
Show relationship between 2 variables | Scatter plot         | Reveals correlation/pattern
Compare proportions                   | Stacked bar          | Parts of a whole
Show distribution shape               | Histogram / density  | Reveals modality, skew
Compare paired measurements          | Paired dot plot      | Shows individual changes
Show survival/time-to-event          | Kaplan-Meier         | Handles censoring correctly
Display effect sizes from studies    | Forest plot          | Standard for meta-analysis
Show differential expression         | Volcano plot         | FC + significance together
Show expression-dependent effects    | MA plot              | Mean vs fold change
Cluster samples/genes                | Heatmap + dendrogram | Reveals grouping patterns
Reduce dimensions                    | PCA/UMAP scatter     | Reveals structure in high-D data
```

---

## 4. Multi-Panel Figure Expertise

### GridSpec Layouts

```python
from matplotlib.gridspec import GridSpec
fig = plt.figure(figsize=(7.2, 6))  # Nature double column
gs = GridSpec(2, 3, figure=fig, width_ratios=[1.5, 1, 1.5],
              height_ratios=[1, 1], hspace=0.35, wspace=0.35)
ax_a = fig.add_subplot(gs[0, :2])  # Top-left, spanning 2 cols
ax_b = fig.add_subplot(gs[0, 2])   # Top-right
ax_c = fig.add_subplot(gs[1, 0])   # Bottom-left
ax_d = fig.add_subplot(gs[1, 1])   # Bottom-middle
ax_e = fig.add_subplot(gs[1, 2])   # Bottom-right
```

### Panel Labels

```python
def add_panel_labels(fig, axes, labels=None, fontsize=10,
                     fontweight='bold', case='upper', offset=(-0.1, 1.05)):
    """case: 'upper' for A,B,C (most journals) or 'lower' for a,b,c (Nature)"""
    if labels is None:
        labels = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    if case == 'lower':
        labels = [l.lower() for l in labels]
    for ax, label in zip(axes, labels):
        ax.text(offset[0], offset[1], label, transform=ax.transAxes,
                fontsize=fontsize, fontweight=fontweight, va='top', ha='right')
```

### Consistent Styling Across Panels

Every panel must use identical: font family/sizes, line widths, color palette, tick parameters, legend style.

```python
PUB_STYLE = {
    'font.family': 'Arial', 'font.size': 8,
    'axes.titlesize': 9, 'axes.labelsize': 8,
    'xtick.labelsize': 7, 'ytick.labelsize': 7, 'legend.fontsize': 7,
    'axes.linewidth': 0.8, 'xtick.major.width': 0.8, 'ytick.major.width': 0.8,
    'xtick.major.size': 3, 'ytick.major.size': 3,
    'lines.linewidth': 1.2, 'lines.markersize': 4,
    'figure.dpi': 300, 'savefig.dpi': 600, 'savefig.bbox': 'tight',
    'pdf.fonttype': 42, 'ps.fonttype': 42,  # CRITICAL: embed fonts as TrueType
}
plt.rcParams.update(PUB_STYLE)
```

### White Space and Alignment

```
Principles:
  1. Use constrained_layout=True for complex figures (preferred over tight_layout)
  2. Consistent margins between all panels (hspace/wspace)
  3. Panel labels must not overlap axes or titles
  4. Legends must not cover data — place outside: bbox_to_anchor=(1.02, 1)
  5. Check final output at actual print size (zoom to 100% at target DPI)
  6. Minimize dead space but preserve breathing room

Axis sharing:
  - Panels comparing same variable MUST share axis limits (sharey=True, sharex=True)
  - Remove redundant tick labels on internal axes for clean appearance
  - Colorbars should align with their parent panel edges

Common white space mistakes:
  - Legends overlapping data points
  - Panel labels cut off by tight bounding box
  - Axis labels overlapping between adjacent panels
  - Colorbars wider than the plot they describe
  - Too much space between panels (wasted page real estate)
```

```python
# Share axes for comparable panels
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(7.2, 2.5), sharey=True)
for ax in (ax2, ax3):
    ax.tick_params(labelleft=False)  # Remove redundant y labels
```

---

## 5. Publication Figure Checklist

```
RESOLUTION      [ ] Line art >= journal-specific DPI (600-1200)
                [ ] Photos >= 300 DPI | Correct dimensions for column width

FORMAT          [ ] Vector (PDF/EPS) for graphs | Raster (TIFF/PNG) for photos only
                [ ] NEVER JPEG | Fonts embedded (pdf.fonttype=42)

COLOR           [ ] Colorblind-safe palette (Okabe-Ito or equivalent)
                [ ] Grayscale test passed | Redundant encoding present
                [ ] No jet/rainbow | Diverging colormaps centered at 0

FONTS           [ ] All text >= journal minimum (5-8pt at final size)
                [ ] Consistent font family across entire figure

LABELS          [ ] Every axis labeled WITH units ("Concentration (uM)")
                [ ] Colorbar labeled | Legend complete | Gene names in italic

STATISTICS      [ ] Error bars specified in caption (SD/SEM/95%CI)
                [ ] Individual data points shown | n stated per group
                [ ] Statistical test named | p-value thresholds defined
                [ ] Y-axis starts at zero for bar charts (or justified)

PANELS          [ ] Correct case (lowercase for Nature, uppercase otherwise)
                [ ] Consistent size/weight/position | Sequential ordering

FINAL           [ ] Print at target size in grayscale — all features distinguishable
```

---

## 6. Common Figure Types for Life Sciences

### Volcano Plot (Differential Expression)

```python
def volcano_plot(df, fc_col='log2FoldChange', pval_col='padj',
                 fc_thresh=1.0, pval_thresh=0.05, figsize=(4, 4.5)):
    fig, ax = plt.subplots(figsize=figsize)
    neglog10p = -np.log10(df[pval_col].clip(lower=1e-300))
    sig_up = (df[fc_col] >= fc_thresh) & (df[pval_col] < pval_thresh)
    sig_down = (df[fc_col] <= -fc_thresh) & (df[pval_col] < pval_thresh)
    ns = ~sig_up & ~sig_down
    ax.scatter(df.loc[ns, fc_col], neglog10p[ns], c='#999999', s=3, alpha=0.5, rasterized=True)
    ax.scatter(df.loc[sig_up, fc_col], neglog10p[sig_up],
               c='#D55E00', s=5, alpha=0.7, label=f'Up ({sig_up.sum()})')
    ax.scatter(df.loc[sig_down, fc_col], neglog10p[sig_down],
               c='#0072B2', s=5, alpha=0.7, label=f'Down ({sig_down.sum()})')
    ax.axhline(-np.log10(pval_thresh), ls='--', lw=0.8, color='gray')
    ax.axvline(fc_thresh, ls='--', lw=0.8, color='gray')
    ax.axvline(-fc_thresh, ls='--', lw=0.8, color='gray')
    ax.set_xlabel('$\\log_2$(Fold Change)')
    ax.set_ylabel('$-\\log_{10}$(Adjusted P-value)')
    ax.legend(frameon=False, fontsize=7)
    ax.spines[['top', 'right']].set_visible(False)
    return fig, ax
```

### Kaplan-Meier Survival Curve

```python
from lifelines import KaplanMeierFitter

def kaplan_meier_plot(df, time_col, event_col, group_col,
                      palette=None, figsize=(5, 4), at_risk=True):
    """Includes number-at-risk table (required by NEJM, Lancet)."""
    if palette is None:
        palette = ['#0072B2', '#E69F00', '#009E73', '#D55E00']
    fig, ax = plt.subplots(figsize=figsize)
    kmfs = []
    for i, (name, grp) in enumerate(df.groupby(group_col)):
        kmf = KaplanMeierFitter()
        kmf.fit(grp[time_col], grp[event_col], label=f'{name} (n={len(grp)})')
        kmf.plot_survival_function(ax=ax, ci_show=True, color=palette[i % len(palette)])
        kmfs.append((name, kmf))
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=False, fontsize=7, loc='lower left')
    ax.spines[['top', 'right']].set_visible(False)
    if at_risk:
        time_points = np.linspace(0, df[time_col].max(), 6).astype(int)
        for i, (name, kmf) in enumerate(kmfs):
            for j, t in enumerate(time_points):
                n = int(kmf.event_table.loc[:t, 'at_risk'].iloc[-1]) if t <= kmf.timeline.max() else 0
                ax.text(t, -0.12 - i*0.06, str(n), ha='center', fontsize=6,
                       transform=ax.get_xaxis_transform(), color=palette[i])
    return fig, ax
```

### Heatmap with Dendrograms (Clustermap)

```python
def clustermap_publication(data, cmap='RdBu_r', center=0,
                           row_colors=None, col_colors=None, figsize=(6, 8)):
    """data: DataFrame (genes x samples), ideally z-scored."""
    vmax = np.max(np.abs(data.values))
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=center, vmax=vmax)
    g = sns.clustermap(data, cmap=cmap, norm=norm, figsize=figsize,
                        method='ward', row_colors=row_colors, col_colors=col_colors,
                        linewidths=0, dendrogram_ratio=(0.1, 0.1),
                        cbar_pos=(0.02, 0.8, 0.03, 0.15),
                        cbar_kws={'label': 'Z-score'})
    g.ax_heatmap.set_xticklabels(g.ax_heatmap.get_xticklabels(), rotation=45, ha='right', fontsize=6)
    g.ax_heatmap.set_yticklabels(g.ax_heatmap.get_yticklabels(), fontsize=5)
    return g
```

### Box/Violin with Strip Overlay

```python
def violin_strip_plot(df, x, y, order=None, palette=None, figsize=(4, 4.5)):
    if palette is None:
        palette = ['#0072B2', '#E69F00', '#009E73', '#D55E00', '#56B4E9', '#CC79A7']
    fig, ax = plt.subplots(figsize=figsize)
    sns.violinplot(data=df, x=x, y=y, order=order, inner=None,
                   color='lightgray', alpha=0.4, ax=ax)
    sns.stripplot(data=df, x=x, y=y, order=order, size=4, jitter=0.15,
                  alpha=0.7, palette=palette, ax=ax)
    sns.boxplot(data=df, x=x, y=y, order=order, width=0.2, showcaps=False,
                boxprops={'facecolor': 'none'}, whiskerprops={'linewidth': 0},
                medianprops={'color': 'black'}, fliersize=0, ax=ax)
    ax.spines[['top', 'right']].set_visible(False)
    for i, grp in enumerate(order or df[x].unique()):
        ax.text(i, ax.get_ylim()[0], f'n={df[df[x]==grp].shape[0]}',
               ha='center', va='top', fontsize=6, color='gray')
    return fig, ax
```

### Dose-Response Curve with IC50

```python
from scipy.optimize import curve_fit

def hill_equation(x, top, bottom, ic50, hill_slope):
    return bottom + (top - bottom) / (1 + (x / ic50) ** hill_slope)

def dose_response_plot(concentrations, responses, labels=None,
                       palette=None, figsize=(4, 3.5)):
    if palette is None:
        palette = ['#0072B2', '#E69F00', '#009E73', '#D55E00']
    fig, ax = plt.subplots(figsize=figsize)
    for i, (conc, resp) in enumerate(zip(concentrations, responses)):
        color = palette[i % len(palette)]
        lbl = labels[i] if labels else f'Compound {i+1}'
        try:
            popt, _ = curve_fit(hill_equation, conc, resp,
                               p0=[100, 0, np.median(conc), 1], maxfev=10000)
            x_fit = np.logspace(np.log10(conc.min()), np.log10(conc.max()), 200)
            ax.plot(x_fit, hill_equation(x_fit, *popt), color=color, lw=1.5)
            ax.scatter(conc, resp, color=color, s=25, zorder=5,
                      label=f'{lbl} (IC50={popt[2]:.2e})')
        except RuntimeError:
            ax.scatter(conc, resp, color=color, s=25, label=lbl)
    ax.set_xscale('log')
    ax.set_xlabel('Concentration (M)')
    ax.set_ylabel('Response (%)')
    ax.legend(frameon=False, fontsize=7)
    ax.spines[['top', 'right']].set_visible(False)
    return fig, ax
```

### PCA / UMAP Embeddings

```python
def embedding_plot(coords, labels, method='PCA', explained_variance=None,
                   palette=None, figsize=(4, 4), point_size=8):
    if palette is None:
        palette = ['#0072B2', '#E69F00', '#009E73', '#D55E00',
                   '#56B4E9', '#CC79A7', '#F0E442', '#000000']
    fig, ax = plt.subplots(figsize=figsize)
    for i, lbl in enumerate(np.unique(labels)):
        mask = labels == lbl
        ax.scatter(coords[mask, 0], coords[mask, 1], c=palette[i % len(palette)],
                  s=point_size, alpha=0.7, label=lbl, rasterized=True)
    if method == 'PCA' and explained_variance:
        ax.set_xlabel(f'PC1 ({explained_variance[0]:.1f}% variance)')
        ax.set_ylabel(f'PC2 ({explained_variance[1]:.1f}% variance)')
    else:
        ax.set_xlabel(f'{method} 1')
        ax.set_ylabel(f'{method} 2')
    ax.legend(frameon=False, fontsize=7, markerscale=1.5,
             bbox_to_anchor=(1.02, 1), loc='upper left')
    ax.spines[['top', 'right']].set_visible(False)
    return fig, ax
```

### Forest Plot (Meta-Analysis)

```python
def forest_plot(studies, effects, ci_lower, ci_upper, weights=None,
                summary_effect=None, summary_ci=None, xlabel='Effect Size',
                null_value=0, figsize=(6, None)):
    n = len(studies)
    if figsize[1] is None:
        figsize = (figsize[0], max(3, n * 0.35 + 1))
    fig, ax = plt.subplots(figsize=figsize)
    y_pos = np.arange(n, 0, -1)
    sizes = 50 + 200 * (weights / weights.max()) if weights is not None else np.full(n, 80)
    for i in range(n):
        ax.plot([ci_lower[i], ci_upper[i]], [y_pos[i]]*2, color='#0072B2', lw=1.5)
        ax.scatter(effects[i], y_pos[i], s=sizes[i], color='#0072B2', zorder=5, marker='s')
    if summary_effect is not None and summary_ci is not None:
        dy, dh = 0.3, 0.25
        ax.fill([summary_ci[0], summary_effect, summary_ci[1], summary_effect],
                [dy, dy+dh, dy, dy-dh], color='#D55E00', edgecolor='black', lw=0.8)
    ax.axvline(null_value, ls='--', color='gray', lw=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(studies, fontsize=7)
    ax.set_xlabel(xlabel)
    ax.spines[['top', 'right']].set_visible(False)
    return fig, ax
```

### Correlation Matrix (Lower Triangle Only)

```python
def correlation_triangle(df, method='pearson', figsize=(5, 4.5), annot=True):
    corr = df.corr(method=method)
    mask = np.triu(np.ones_like(corr, dtype=bool))
    norm = mcolors.TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1)
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(corr, mask=mask, cmap='RdBu_r', norm=norm, annot=annot,
                fmt='.2f', annot_kws={'fontsize': 6}, square=True,
                linewidths=0.5, cbar_kws={'label': f'{method.capitalize()} r'}, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=7)
    return fig, ax
```

### MA Plot (Differential Expression)

```python
def ma_plot(df, mean_col='baseMean', fc_col='log2FoldChange',
            pval_col='padj', pval_thresh=0.05, figsize=(4, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    log_mean = np.log10(df[mean_col].clip(lower=0.1))
    sig = df[pval_col] < pval_thresh
    ax.scatter(log_mean[~sig], df.loc[~sig, fc_col], c='#999999', s=2, alpha=0.3, rasterized=True)
    ax.scatter(log_mean[sig], df.loc[sig, fc_col], c='#D55E00', s=3, alpha=0.5,
               rasterized=True, label=f'Significant ({sig.sum()})')
    ax.axhline(0, ls='-', lw=0.8, color='black')
    ax.set_xlabel('$\\log_{10}$(Mean Expression)')
    ax.set_ylabel('$\\log_2$(Fold Change)')
    ax.legend(frameon=False, fontsize=7)
    ax.spines[['top', 'right']].set_visible(False)
    return fig, ax
```

---

## 7. Export and Save

```python
def save_publication_figure(fig, filename, journal='nature'):
    """Save in publication-ready format with correct DPI for target journal."""
    settings = {
        'nature':  {'dpi': 600,  'fmt': 'pdf'},
        'science': {'dpi': 1200, 'fmt': 'pdf'},
        'cell':    {'dpi': 1000, 'fmt': 'pdf'},
        'plos':    {'dpi': 600,  'fmt': 'tiff'},
        'nejm':    {'dpi': 1200, 'fmt': 'eps'},
        'lancet':  {'dpi': 1000, 'fmt': 'eps'},
    }
    s = settings.get(journal.lower(), settings['nature'])
    fig.savefig(f'{filename}.{s["fmt"]}', dpi=s['dpi'], bbox_inches='tight', pad_inches=0.05)
    fig.savefig(f'{filename}_preview.png', dpi=300, bbox_inches='tight', pad_inches=0.05)

def figure_size_from_journal(journal, columns=1, aspect_ratio=0.75):
    """Returns (width_inches, height_inches) for target journal column width."""
    widths = {
        'nature':  {1: 89, 1.5: 120, 2: 183}, 'science': {1: 55, 1.5: 87, 2: 120},
        'cell':    {1: 85, 1.5: 114, 2: 174}, 'plos':    {1: 83, 1.5: 120, 2: 173},
        'nejm':    {1: 86, 1.5: 132, 2: 178}, 'lancet':  {1: 79, 1.5: 124, 2: 168},
    }
    w_mm = widths.get(journal.lower(), widths['nature']).get(columns, 89)
    w_in = w_mm / 25.4
    return (round(w_in, 2), round(w_in * aspect_ratio, 2))
```

---

## 8. Publication Style Template

Apply at the top of every figure-generating script.

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

def set_publication_style(journal='nature'):
    style = {
        'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica'],
        'font.size': 8, 'axes.titlesize': 9, 'axes.labelsize': 8,
        'xtick.labelsize': 7, 'ytick.labelsize': 7, 'legend.fontsize': 7,
        'axes.linewidth': 0.8, 'axes.spines.top': False, 'axes.spines.right': False,
        'axes.grid': False, 'axes.facecolor': 'white',
        'xtick.major.width': 0.8, 'ytick.major.width': 0.8,
        'xtick.major.size': 3.5, 'ytick.major.size': 3.5,
        'xtick.direction': 'out', 'ytick.direction': 'out',
        'lines.linewidth': 1.2, 'lines.markersize': 4,
        'figure.facecolor': 'white', 'figure.dpi': 150,
        'savefig.dpi': 600, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.05,
        'pdf.fonttype': 42, 'ps.fonttype': 42,  # CRITICAL: TrueType font embedding
        'legend.frameon': False, 'image.cmap': 'viridis',
    }
    dpi_overrides = {'cell': 1000, 'nejm': 1200, 'science': 1200, 'lancet': 1000}
    if journal.lower() in dpi_overrides:
        style['savefig.dpi'] = dpi_overrides[journal.lower()]
    mpl.rcParams.update(style)
```

---

## 9. Microscopy and Gel Image Guidelines

```
Microscopy images:
  - ALWAYS include a scale bar (white or black, with size annotation)
  - State magnification in caption if relevant
  - Use consistent brightness/contrast adjustments across all panels in a comparison
  - Any image processing must be disclosed in Methods
  - Do NOT add arrows or annotations that obscure underlying data
  - Insets should have a visible border and scale bar

Gel/blot images:
  - No brightness/contrast adjustments that obscure or eliminate bands
  - Show full blot or state that it is cropped
  - Include molecular weight markers
  - Loading control on same membrane or state it was re-probed
  - Adjustments must be applied uniformly across entire image

Flow cytometry:
  - Use biexponential (logicle) scaling, NOT log scaling
  - State gating strategy in figure or supplementary
  - Show percentage in each gate
  - Use contour plots for dense data, dot plots for sparse
```

## 10. Common Mistakes and Fixes

```
Mistake                            | Fix
-----------------------------------+-------------------------------------------
JPEG for figures                   | PDF (vector) or TIFF/PNG (raster)
Jet/rainbow colormap               | viridis (sequential) or RdBu_r (diverging)
Bar chart without data points      | Add strip/swarm overlay
Error bars unspecified in caption   | State SD/SEM/95%CI explicitly
Font too small at print size       | Check at actual column width (min 6-8pt)
Truncated y-axis on bar chart      | Start at zero or justify in caption
Missing units on axis labels       | "Time (hours)" not "Time"
Type 3 fonts in PDF/EPS            | Set pdf.fonttype=42, ps.fonttype=42
Missing/wrong-case panel labels    | lowercase for Nature, UPPERCASE otherwise
Diverging colormap not centered    | Use TwoSlopeNorm(vcenter=0)
3D bar charts or pie charts        | Never. Use grouped/stacked bars.
Legend covering data               | bbox_to_anchor=(1.02, 1) outside plot
```

---

## 11. Cross-Skill Integration Guide

### From rnaseq-deseq2 Results
DESeq2 table (gene, log2FC, padj, baseMean) -> volcano_plot, ma_plot, clustermap_publication (top DE genes), embedding_plot (PCA of samples)

### From single-cell-analysis Results
AnnData with embeddings/clusters -> embedding_plot (UMAP by cluster), violin_strip_plot (marker genes), dot plots, clustermap_publication

### From proteomics-analysis Results
Protein quantification/differential abundance -> volcano_plot, correlation_triangle (samples), clustermap_publication (significant proteins), embedding_plot (PCA)

### From medicinal-chemistry Results
SAR data, IC50 values -> dose_response_plot, activity heatmaps, property radar charts

### From statistical-modeling Results
Model coefficients, meta-analysis -> forest_plot, kaplan_meier_plot, regression diagnostics, Bland-Altman plots
