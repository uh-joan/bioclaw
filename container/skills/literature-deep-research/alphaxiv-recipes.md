# AlphaXiv Paper Lookup Recipes

Recipes for retrieving AI-generated structured overviews of arxiv preprints via alphaxiv.org. These endpoints return machine-readable markdown — faster and more reliable than parsing raw PDFs.

**No authentication required.** All endpoints are publicly accessible.

---

## Recipe 1: Quick Paper Overview from ArXiv URL

When a user provides an arxiv URL, extract the paper ID and fetch the structured overview.

```bash
# Extract paper ID from various URL formats:
#   https://arxiv.org/abs/2401.12345
#   https://arxiv.org/abs/2401.12345v2
#   https://arxiv.org/pdf/2401.12345
#   https://alphaxiv.org/abs/2401.12345

PAPER_ID="2401.12345"  # extracted from URL, strip version suffix

# Fetch AI-generated structured overview (preferred first call)
curl -s "https://alphaxiv.org/overview/${PAPER_ID}.md"
```

**Output:** Structured markdown with key findings, methodology summary, results, and significance — optimized for LLM consumption.

---

## Recipe 2: Full Paper Text as Markdown

When the overview lacks specific details (equations, tables, supplementary methods), fetch the complete paper text.

```bash
PAPER_ID="2401.12345"

# Full paper text converted to markdown
curl -s "https://alphaxiv.org/abs/${PAPER_ID}.md"
```

**When to use:** Only when the overview from Recipe 1 doesn't contain the specific detail needed (e.g., exact equations, full tables, supplementary data).

---

## Recipe 3: Paper ID Extraction Patterns

```bash
# From arxiv.org URLs
echo "https://arxiv.org/abs/2401.12345v2" | grep -oP '\d{4}\.\d{4,5}'
# Result: 2401.12345

# From alphaxiv.org URLs
echo "https://alphaxiv.org/abs/2401.12345" | grep -oP '\d{4}\.\d{4,5}'
# Result: 2401.12345

# Older arxiv format (pre-2007)
echo "https://arxiv.org/abs/hep-th/9905111" | grep -oP '[a-z-]+/\d{7}'
# Result: hep-th/9905111
```

---

## Recipe 4: Batch Paper Lookup

When reviewing multiple papers (e.g., from a citation list or search results):

```bash
PAPER_IDS=("2401.12345" "2312.67890" "2405.11111")

for pid in "${PAPER_IDS[@]}"; do
  echo "=== Paper: ${pid} ==="
  overview=$(curl -s "https://alphaxiv.org/overview/${pid}.md")
  if echo "$overview" | grep -q "404\|Not Found"; then
    echo "Overview not available, falling back to arxiv PDF"
    echo "PDF: https://arxiv.org/pdf/${pid}"
  else
    echo "$overview"
  fi
  echo ""
done
```

---

## Recipe 5: Overview + PubMed Cross-Reference

Combine alphaxiv overview with PubMed metadata for papers that have been published:

```bash
PAPER_ID="2401.12345"

# 1. Get the structured overview
curl -s "https://alphaxiv.org/overview/${PAPER_ID}.md" > /tmp/overview.md

# 2. Extract title from overview, then search PubMed for the published version
# Use mcp__pubmed__pubmed_articles with method: search_keywords
# to find if the preprint has a peer-reviewed publication
```

**Use case:** Determine if a preprint has been peer-reviewed and published, cross-reference citation counts, and check for post-publication corrections.

---

## Recipe 6: Deep Research Integration

When building a literature-deep-research report that includes preprints:

```bash
# Standard workflow:
# 1. Search PubMed + bioRxiv via MCP tools for seed papers
# 2. For any arxiv/bioRxiv hits, fetch alphaxiv overview for quick triage
# 3. Use overview to decide if paper merits full inclusion in report
# 4. Fetch full text only for papers needing detailed extraction

PAPER_ID="2401.12345"

# Quick triage — is this paper relevant to the research question?
curl -s "https://alphaxiv.org/overview/${PAPER_ID}.md"

# If relevant, get full text for detailed evidence extraction
curl -s "https://alphaxiv.org/abs/${PAPER_ID}.md"
```

---

## Recipe 7: Fallback Chain

When alphaxiv endpoints return 404 (overview not yet generated):

```bash
PAPER_ID="2401.12345"

# Try overview first
response=$(curl -s -o /tmp/paper.md -w "%{http_code}" "https://alphaxiv.org/overview/${PAPER_ID}.md")

if [ "$response" = "200" ]; then
  cat /tmp/paper.md
else
  # Fallback: try full text
  response=$(curl -s -o /tmp/paper.md -w "%{http_code}" "https://alphaxiv.org/abs/${PAPER_ID}.md")
  if [ "$response" = "200" ]; then
    cat /tmp/paper.md
  else
    # Final fallback: direct PDF
    echo "AlphaXiv unavailable. PDF at: https://arxiv.org/pdf/${PAPER_ID}"
    # Use pdf-reader skill if available
  fi
fi
```

---

## Endpoint Reference

| Endpoint | Returns | Best for |
|----------|---------|----------|
| `alphaxiv.org/overview/{ID}.md` | AI-generated structured summary | Quick triage, understanding key findings |
| `alphaxiv.org/abs/{ID}.md` | Full paper text as markdown | Equations, tables, detailed methods |
| `arxiv.org/pdf/{ID}` | Raw PDF (fallback) | When alphaxiv hasn't processed the paper |
