# NanoClaw Agent Container
# Runs Claude Agent SDK in isolated Linux VM with browser automation

FROM node:22-slim

# Install system dependencies for Chromium and PDF tools
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-liberation \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    libgbm1 \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libcups2 \
    libdrm2 \
    libxshmfence1 \
    curl \
    git \
    poppler-utils \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Python scientific packages for compute/omics skills
RUN pip3 install --no-cache-dir --break-system-packages \
    numpy \
    pandas \
    scipy \
    scikit-learn \
    scikit-image \
    statsmodels \
    lifelines \
    matplotlib \
    seaborn \
    scanpy \
    anndata \
    squidpy \
    harmonypy \
    pydeseq2 \
    gseapy

# Set Chromium path for agent-browser
ENV AGENT_BROWSER_EXECUTABLE_PATH=/usr/bin/chromium
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium

# Install agent-browser and claude-code globally
RUN npm install -g agent-browser @anthropic-ai/claude-code

# Create app directory
WORKDIR /app

# Copy package files first for better caching
COPY agent-runner/package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY agent-runner/ ./

# Build TypeScript
RUN npm run build

# Install pdf-reader CLI
COPY skills/pdf-reader/pdf-reader /usr/local/bin/pdf-reader
RUN chmod +x /usr/local/bin/pdf-reader

# Pre-install pharma MCP server dependencies (native modules compiled for Linux)
# Shared node_modules used by all MCP servers at runtime via symlinks
RUN mkdir -p /opt/mcp-deps && cd /opt/mcp-deps && \
    npm init -y > /dev/null 2>&1 && \
    npm install --ignore-scripts \
      @modelcontextprotocol/sdk@1 \
      better-sqlite3@12 \
      axios@1 \
      adm-zip@0.5 \
      xlsx@0.18 \
      xml2js@0.6 \
      fast-xml-parser@4 \
      xml-stream@0.4 \
      dotenv@16 \
      zod@3 \
      axios-retry@4 \
      cheerio@1 \
      exceljs@4 \
      node-fetch@3 \
      express@4 \
      2>/dev/null && \
    npx --yes prebuild-install -r napi --path node_modules/better-sqlite3 2>/dev/null || \
    cd node_modules/better-sqlite3 && npx --yes node-gyp rebuild 2>/dev/null; \
    cd /opt/mcp-deps && rm -f package.json package-lock.json

# Create workspace directories
RUN mkdir -p /workspace/group /workspace/global /workspace/extra /workspace/ipc/messages /workspace/ipc/tasks /workspace/ipc/input

# Create entrypoint script
# Secrets are passed via stdin JSON — temp file is deleted immediately after Node reads it
# Follow-up messages arrive via IPC files in /workspace/ipc/input/
# For each mounted MCP server, symlink build + package.json + shared node_modules
RUN printf '#!/bin/bash\nset -e\ncd /app && npx tsc --outDir /tmp/dist 2>&1 >&2\nln -s /app/node_modules /tmp/dist/node_modules\nchmod -R a-w /tmp/dist\nfor srv in fda ctgov pubmed drugbank ema opentargets chembl nlm cdc pubchem biorxiv medicare medicaid eu-filings ensembl uniprot stringdb reactome kegg alphafold pdb hpo gtex geneontology depmap gnomad cbioportal bindingdb geo clinpgx monarch jaspar; do\n  if [ -d /opt/${srv}-mcp-server/build ]; then\n    mkdir -p /tmp/${srv}-mcp-server/data\n    ln -s /opt/${srv}-mcp-server/build /tmp/${srv}-mcp-server/build\n    ln -s /opt/${srv}-mcp-server/package.json /tmp/${srv}-mcp-server/package.json\n    ln -s /opt/mcp-deps/node_modules /tmp/${srv}-mcp-server/node_modules\n  fi\ndone\ncat > /tmp/input.json\nnode /tmp/dist/index.js < /tmp/input.json\n' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Set ownership to node user (non-root) for writable directories
RUN chown -R node:node /workspace && chmod 777 /home/node

# Switch to non-root user (required for --dangerously-skip-permissions)
USER node

# Set working directory to group workspace
WORKDIR /workspace/group

# Entry point reads JSON from stdin, outputs JSON to stdout
ENTRYPOINT ["/app/entrypoint.sh"]
