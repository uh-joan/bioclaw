import os from 'os';
import path from 'path';

import { readEnvFile } from './env.js';

// Read config values from .env (falls back to process.env).
// Secrets are NOT read here — they stay on disk and are loaded only
// where needed (container-runner.ts) to avoid leaking to child processes.
const envConfig = readEnvFile([
  'ASSISTANT_NAME',
  'ASSISTANT_HAS_OWN_NUMBER',
  'CONTAINER_IMAGE',
  'FDA_MCP_SERVER_PATH',
  'CTGOV_MCP_SERVER_PATH',
  'PUBMED_MCP_SERVER_PATH',
  'DRUGBANK_MCP_SERVER_PATH',
  'EMA_MCP_SERVER_PATH',
  'OPENTARGETS_MCP_SERVER_PATH',
  'CHEMBL_MCP_SERVER_PATH',
  'NLM_MCP_SERVER_PATH',
  'CDC_MCP_SERVER_PATH',
  'PUBCHEM_MCP_SERVER_PATH',
  'BIORXIV_MCP_SERVER_PATH',
  'MEDICARE_MCP_SERVER_PATH',
  'MEDICAID_MCP_SERVER_PATH',
  'EU_FILINGS_MCP_SERVER_PATH',
  'ENSEMBL_MCP_SERVER_PATH',
  'UNIPROT_MCP_SERVER_PATH',
  'STRINGDB_MCP_SERVER_PATH',
  'REACTOME_MCP_SERVER_PATH',
  'KEGG_MCP_SERVER_PATH',
  'ALPHAFOLD_MCP_SERVER_PATH',
  'PDB_MCP_SERVER_PATH',
  'HPO_MCP_SERVER_PATH',
  'GTEX_MCP_SERVER_PATH',
  'GENEONTOLOGY_MCP_SERVER_PATH',
  'DEPMAP_MCP_SERVER_PATH',
  'GNOMAD_MCP_SERVER_PATH',
  'CBIOPORTAL_MCP_SERVER_PATH',
  'BINDINGDB_MCP_SERVER_PATH',
  'GEO_MCP_SERVER_PATH',
  'CLINPGX_MCP_SERVER_PATH',
  'MONARCH_MCP_SERVER_PATH',
  'JASPAR_MCP_SERVER_PATH',
  'CLINVAR_MCP_SERVER_PATH',
  'COSMIC_MCP_SERVER_PATH',
  'GWAS_MCP_SERVER_PATH',
  'HMDB_MCP_SERVER_PATH',
  'OPENALEX_MCP_SERVER_PATH',
  'NCBI_MCP_SERVER_PATH',
  'FINANCIALS_MCP_SERVER_PATH',
  'SEC_MCP_SERVER_PATH',
  'PATENTS_MCP_SERVER_PATH',
]);

export const ASSISTANT_NAME =
  process.env.ASSISTANT_NAME || envConfig.ASSISTANT_NAME || 'Andy';
export const ASSISTANT_HAS_OWN_NUMBER =
  (process.env.ASSISTANT_HAS_OWN_NUMBER ||
    envConfig.ASSISTANT_HAS_OWN_NUMBER) === 'true';
export const POLL_INTERVAL = 2000;
export const SCHEDULER_POLL_INTERVAL = 60000;

// Absolute paths needed for container mounts
const PROJECT_ROOT = process.cwd();
const HOME_DIR = process.env.HOME || os.homedir();

// Mount security: allowlist stored OUTSIDE project root, never mounted into containers
export const MOUNT_ALLOWLIST_PATH = path.join(
  HOME_DIR,
  '.config',
  'nanoclaw',
  'mount-allowlist.json',
);
export const SENDER_ALLOWLIST_PATH = path.join(
  HOME_DIR,
  '.config',
  'nanoclaw',
  'sender-allowlist.json',
);
export const STORE_DIR = path.resolve(PROJECT_ROOT, 'store');
export const GROUPS_DIR = path.resolve(PROJECT_ROOT, 'groups');
export const DATA_DIR = path.resolve(PROJECT_ROOT, 'data');

export const CONTAINER_IMAGE =
  process.env.CONTAINER_IMAGE ||
  envConfig.CONTAINER_IMAGE ||
  'nanoclaw-agent:latest';
export const CONTAINER_TIMEOUT = parseInt(
  process.env.CONTAINER_TIMEOUT || '1800000',
  10,
);
export const CONTAINER_MAX_OUTPUT_SIZE = parseInt(
  process.env.CONTAINER_MAX_OUTPUT_SIZE || '10485760',
  10,
); // 10MB default
export const IPC_POLL_INTERVAL = 1000;
export const IDLE_TIMEOUT = parseInt(process.env.IDLE_TIMEOUT || '1800000', 10); // 30min default — how long to keep container alive after last result
export const MAX_CONCURRENT_CONTAINERS = Math.max(
  1,
  parseInt(process.env.MAX_CONCURRENT_CONTAINERS || '5', 10) || 5,
);

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export const TRIGGER_PATTERN = new RegExp(
  `^@${escapeRegex(ASSISTANT_NAME)}\\b`,
  'i',
);

// Pharma MCP Server paths (optional — enables pharmaceutical intelligence tools in containers)
export const FDA_MCP_SERVER_PATH =
  process.env.FDA_MCP_SERVER_PATH || envConfig.FDA_MCP_SERVER_PATH || '';
export const CTGOV_MCP_SERVER_PATH =
  process.env.CTGOV_MCP_SERVER_PATH || envConfig.CTGOV_MCP_SERVER_PATH || '';
export const PUBMED_MCP_SERVER_PATH =
  process.env.PUBMED_MCP_SERVER_PATH || envConfig.PUBMED_MCP_SERVER_PATH || '';
export const DRUGBANK_MCP_SERVER_PATH =
  process.env.DRUGBANK_MCP_SERVER_PATH ||
  envConfig.DRUGBANK_MCP_SERVER_PATH ||
  '';
export const EMA_MCP_SERVER_PATH =
  process.env.EMA_MCP_SERVER_PATH || envConfig.EMA_MCP_SERVER_PATH || '';
export const OPENTARGETS_MCP_SERVER_PATH =
  process.env.OPENTARGETS_MCP_SERVER_PATH ||
  envConfig.OPENTARGETS_MCP_SERVER_PATH ||
  '';
export const CHEMBL_MCP_SERVER_PATH =
  process.env.CHEMBL_MCP_SERVER_PATH || envConfig.CHEMBL_MCP_SERVER_PATH || '';
export const NLM_MCP_SERVER_PATH =
  process.env.NLM_MCP_SERVER_PATH || envConfig.NLM_MCP_SERVER_PATH || '';
export const CDC_MCP_SERVER_PATH =
  process.env.CDC_MCP_SERVER_PATH || envConfig.CDC_MCP_SERVER_PATH || '';
export const PUBCHEM_MCP_SERVER_PATH =
  process.env.PUBCHEM_MCP_SERVER_PATH ||
  envConfig.PUBCHEM_MCP_SERVER_PATH ||
  '';
export const BIORXIV_MCP_SERVER_PATH =
  process.env.BIORXIV_MCP_SERVER_PATH ||
  envConfig.BIORXIV_MCP_SERVER_PATH ||
  '';
export const MEDICARE_MCP_SERVER_PATH =
  process.env.MEDICARE_MCP_SERVER_PATH ||
  envConfig.MEDICARE_MCP_SERVER_PATH ||
  '';
export const MEDICAID_MCP_SERVER_PATH =
  process.env.MEDICAID_MCP_SERVER_PATH ||
  envConfig.MEDICAID_MCP_SERVER_PATH ||
  '';
export const EU_FILINGS_MCP_SERVER_PATH =
  process.env.EU_FILINGS_MCP_SERVER_PATH ||
  envConfig.EU_FILINGS_MCP_SERVER_PATH ||
  '';
export const ENSEMBL_MCP_SERVER_PATH =
  process.env.ENSEMBL_MCP_SERVER_PATH ||
  envConfig.ENSEMBL_MCP_SERVER_PATH ||
  '';
export const UNIPROT_MCP_SERVER_PATH =
  process.env.UNIPROT_MCP_SERVER_PATH ||
  envConfig.UNIPROT_MCP_SERVER_PATH ||
  '';
export const STRINGDB_MCP_SERVER_PATH =
  process.env.STRINGDB_MCP_SERVER_PATH ||
  envConfig.STRINGDB_MCP_SERVER_PATH ||
  '';
export const REACTOME_MCP_SERVER_PATH =
  process.env.REACTOME_MCP_SERVER_PATH ||
  envConfig.REACTOME_MCP_SERVER_PATH ||
  '';
export const KEGG_MCP_SERVER_PATH =
  process.env.KEGG_MCP_SERVER_PATH || envConfig.KEGG_MCP_SERVER_PATH || '';
export const ALPHAFOLD_MCP_SERVER_PATH =
  process.env.ALPHAFOLD_MCP_SERVER_PATH ||
  envConfig.ALPHAFOLD_MCP_SERVER_PATH ||
  '';
export const PDB_MCP_SERVER_PATH =
  process.env.PDB_MCP_SERVER_PATH || envConfig.PDB_MCP_SERVER_PATH || '';
export const HPO_MCP_SERVER_PATH =
  process.env.HPO_MCP_SERVER_PATH || envConfig.HPO_MCP_SERVER_PATH || '';
export const GTEX_MCP_SERVER_PATH =
  process.env.GTEX_MCP_SERVER_PATH || envConfig.GTEX_MCP_SERVER_PATH || '';
export const GENEONTOLOGY_MCP_SERVER_PATH =
  process.env.GENEONTOLOGY_MCP_SERVER_PATH ||
  envConfig.GENEONTOLOGY_MCP_SERVER_PATH ||
  '';
export const DEPMAP_MCP_SERVER_PATH =
  process.env.DEPMAP_MCP_SERVER_PATH || envConfig.DEPMAP_MCP_SERVER_PATH || '';
export const GNOMAD_MCP_SERVER_PATH =
  process.env.GNOMAD_MCP_SERVER_PATH || envConfig.GNOMAD_MCP_SERVER_PATH || '';
export const CBIOPORTAL_MCP_SERVER_PATH =
  process.env.CBIOPORTAL_MCP_SERVER_PATH ||
  envConfig.CBIOPORTAL_MCP_SERVER_PATH ||
  '';
export const BINDINGDB_MCP_SERVER_PATH =
  process.env.BINDINGDB_MCP_SERVER_PATH ||
  envConfig.BINDINGDB_MCP_SERVER_PATH ||
  '';
export const GEO_MCP_SERVER_PATH =
  process.env.GEO_MCP_SERVER_PATH || envConfig.GEO_MCP_SERVER_PATH || '';
export const CLINPGX_MCP_SERVER_PATH =
  process.env.CLINPGX_MCP_SERVER_PATH ||
  envConfig.CLINPGX_MCP_SERVER_PATH ||
  '';
export const MONARCH_MCP_SERVER_PATH =
  process.env.MONARCH_MCP_SERVER_PATH ||
  envConfig.MONARCH_MCP_SERVER_PATH ||
  '';
export const JASPAR_MCP_SERVER_PATH =
  process.env.JASPAR_MCP_SERVER_PATH || envConfig.JASPAR_MCP_SERVER_PATH || '';
export const CLINVAR_MCP_SERVER_PATH =
  process.env.CLINVAR_MCP_SERVER_PATH ||
  envConfig.CLINVAR_MCP_SERVER_PATH ||
  '';
export const COSMIC_MCP_SERVER_PATH =
  process.env.COSMIC_MCP_SERVER_PATH || envConfig.COSMIC_MCP_SERVER_PATH || '';
export const GWAS_MCP_SERVER_PATH =
  process.env.GWAS_MCP_SERVER_PATH || envConfig.GWAS_MCP_SERVER_PATH || '';
export const HMDB_MCP_SERVER_PATH =
  process.env.HMDB_MCP_SERVER_PATH || envConfig.HMDB_MCP_SERVER_PATH || '';
export const OPENALEX_MCP_SERVER_PATH =
  process.env.OPENALEX_MCP_SERVER_PATH ||
  envConfig.OPENALEX_MCP_SERVER_PATH ||
  '';
export const NCBI_MCP_SERVER_PATH =
  process.env.NCBI_MCP_SERVER_PATH || envConfig.NCBI_MCP_SERVER_PATH || '';
export const FINANCIALS_MCP_SERVER_PATH =
  process.env.FINANCIALS_MCP_SERVER_PATH ||
  envConfig.FINANCIALS_MCP_SERVER_PATH ||
  '';
export const SEC_MCP_SERVER_PATH =
  process.env.SEC_MCP_SERVER_PATH || envConfig.SEC_MCP_SERVER_PATH || '';
export const PATENTS_MCP_SERVER_PATH =
  process.env.PATENTS_MCP_SERVER_PATH ||
  envConfig.PATENTS_MCP_SERVER_PATH ||
  '';

// Timezone for scheduled tasks (cron expressions, etc.)
// Uses system timezone by default
export const TIMEZONE =
  process.env.TZ || Intl.DateTimeFormat().resolvedOptions().timeZone;
