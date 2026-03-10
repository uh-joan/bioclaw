#!/bin/bash
# Build the NanoClaw MCP-bundled agent container image
#
# This script:
# 1. Stages all MCP server build artifacts into mcp-servers-stage/
# 2. Builds container/Dockerfile.mcp-bundled as nanoclaw-agent-mcp:latest
#
# MCP servers are discovered from .env (same paths used by the regular image).
# Only servers with a valid build/ directory are included.
#
# Usage:
#   ./container/build-mcp-bundled.sh [tag]    # default tag: latest

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STAGE_DIR="$SCRIPT_DIR/mcp-servers-stage"
IMAGE_NAME="nanoclaw-agent-mcp"
TAG="${1:-latest}"
CONTAINER_RUNTIME="${CONTAINER_RUNTIME:-docker}"

# All 38 MCP server names (must match entrypoint.sh loop)
MCP_SERVERS=(
  fda ctgov pubmed drugbank ema opentargets chembl nlm cdc pubchem
  biorxiv medicare medicaid eu-filings ensembl uniprot stringdb reactome
  kegg alphafold pdb hpo gtex geneontology depmap gnomad cbioportal
  bindingdb geo clinpgx monarch jaspar clinvar cosmic gwas hmdb openalex
)

echo "=== Staging MCP server build artifacts ==="

# Clean previous staging
rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"

# Read .env for MCP paths
ENV_FILE="$PROJECT_ROOT/.env"
staged=0
skipped=0

for srv in "${MCP_SERVERS[@]}"; do
  # Convert server name to env var name: fda -> FDA_MCP_SERVER_PATH, eu-filings -> EU_FILINGS_MCP_SERVER_PATH
  env_name="$(echo "${srv}" | tr '[:lower:]-' '[:upper:]_')_MCP_SERVER_PATH"

  # Read path from .env file
  srv_path=""
  if [ -f "$ENV_FILE" ]; then
    srv_path=$(grep "^${env_name}=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '"' | tr -d "'")
  fi
  # Fallback to environment variable
  if [ -z "$srv_path" ]; then
    srv_path="${!env_name}"
  fi

  dest="$STAGE_DIR/${srv}-mcp-server"

  if [ -n "$srv_path" ] && [ -d "$srv_path/build" ]; then
    mkdir -p "$dest"
    cp -r "$srv_path/build" "$dest/build"
    cp "$srv_path/package.json" "$dest/package.json" 2>/dev/null || true
    staged=$((staged + 1))
    echo "  ✓ ${srv} (from $srv_path)"
  else
    skipped=$((skipped + 1))
    if [ -n "$srv_path" ]; then
      echo "  ✗ ${srv} (no build/ at $srv_path)"
    else
      echo "  ✗ ${srv} (not configured)"
    fi
  fi
done

echo ""
echo "Staged: ${staged} servers, Skipped: ${skipped}"
echo ""

if [ "$staged" -eq 0 ]; then
  echo "WARNING: No MCP servers were staged. The image will work but without any MCP tools."
  echo "Make sure your .env has *_MCP_SERVER_PATH variables pointing to built MCP servers."
  echo ""
fi

echo "=== Building Docker image ==="
echo "Image: ${IMAGE_NAME}:${TAG}"
echo "Dockerfile: container/Dockerfile.mcp-bundled"
echo ""

${CONTAINER_RUNTIME} build \
  -t "${IMAGE_NAME}:${TAG}" \
  -f "$SCRIPT_DIR/Dockerfile.mcp-bundled" \
  "$SCRIPT_DIR"

# Clean up staging directory
rm -rf "$STAGE_DIR"

echo ""
echo "Build complete!"
echo "Image: ${IMAGE_NAME}:${TAG}"
echo ""
echo "To use this image, set in .env:"
echo "  CONTAINER_IMAGE=nanoclaw-agent-mcp:latest"
echo ""
echo "MCP servers are bundled in the image. Host mount overrides still work:"
echo "  Set *_MCP_SERVER_PATH in .env to override a bundled server (dev workflow)."
