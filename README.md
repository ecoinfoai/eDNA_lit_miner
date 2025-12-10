# eDNA Literature Miner

[![Stable Build](https://github.com/ecoinfoai/eDNA_lit_miner/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/ecoinfoai/eDNA_lit_miner/actions/workflows/ci.yml)
[![Dev Build](https://github.com/ecoinfoai/eDNA_lit_miner/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/ecoinfoai/eDNA_lit_miner/actions/workflows/ci.yml)
[![Build Status](https://github.com/ecoinfoai/eDNA_lit_miner/actions/workflows/ci.yml/badge.svg)](https://github.com/ecoinfoai/eDNA_lit_miner/actions/workflows/ci.yml)
[![Coverage](coverage.svg)](https://github.com/ecoinfoai/eDNA_lit_miner/actions)

This tool automates the search for environmental DNA (eDNA) studies related to specific species across multiple literature providers (PubMed, Semantic Scholar) and saves the results to Zotero.

## Features

- **Multi-Provider Search**: Searches PubMed and Semantic Scholar.
- **Zotero Integration**: Automatically saves unique results to species-specific collections in Zotero.
- **Duplicate Removal**: Deduplicates results based on DOI or Title.
- **Configurable**: Uses `.env` for API keys and configuration.
- **YAML Input**: specific species, synonyms, and keywords defined in a simple YAML format.

## Prerequisites

- Python 3.8+
- [Zotero Account](https://www.zotero.org/) (for library ID and API key)
- PubMed Email (required for PubMed API usage)

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy `.env.template` to `.env`:
   ```bash
   cp .env.template .env  # On Windows: copy .env.template .env
   ```
2. Edit `.env` and fill in your details:
   ```env
   ZOTERO_LIBRARY_ID=your_library_id
   ZOTERO_API_KEY=your_api_key
   ZOTERO_LIBRARY_TYPE=user  # or 'group'
   EMAIL=your_email@example.com
   SEMANTIC_SCHOLAR_API_KEY=your_api_key # Optional but recommended
   ```

## Usage

Run the miner by providing a species list YAML file:

```bash
python -m src.main path/to/species_list.yaml
```

### Options

- `--dry-run`: Perform searches but do not upload to Zotero. Prints results to console.
- `--limit <number>`: Limit results per provider per species (default: 10).

Example:
```bash
python -m src.main test_species.yaml --dry-run --limit 5
```

## Input Format (YAML)

The species list should be a YAML file with the following structure:

```yaml
species:
  - name: Species Name
    synonyms:
      - Synonym 1
      - Synonym 2
    keywords:
      - eDNA
      - metabarcoding
```

See `test_species.yaml` for a working example.
