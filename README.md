# eDNA Literature Miner

![CI](https://github.com/ecoinfoai/eDNA_lit_miner/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.8--3.13-blue)
![Coverage](./coverage.svg)
![License](https://img.shields.io/github/license/ecoinfoai/eDNA_lit_miner)
![Last Commit](https://img.shields.io/github/last-commit/ecoinfoai/eDNA_lit_miner)

This tool automates the search for environmental DNA (eDNA) studies related to specific species across multiple literature providers (PubMed, Semantic Scholar) and saves the results to Zotero.

## Features

- **Multi-Provider Search**: Searches PubMed and Semantic Scholar.
- **Zotero Integration**: Automatically saves unique results to species-specific collections in Zotero.
- **Abstract Cache**: Saves bibliographic information and abstracts to a YAML file for LLM analysis.
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

## Output Files

When the tool runs successfully, it creates:

1. **Zotero Collections**: Papers are organized in species-specific collections (e.g., "eDNA - Gadus morhua")
2. **Abstract Cache** (`data/abstracts_cache.yaml`): A single YAML file containing all papers with:
   - Bibliographic information (title, authors, year, DOI, URL)
   - Full abstracts
   - Zotero keys for reference
   - Search keywords used
   - Timestamps

### Abstract Cache Structure

```yaml
metadata:
  created_at: '2025-12-26T10:30:00'
  last_updated: '2025-12-26T10:35:00'
  total_species: 2
  total_papers: 15

species:
  - name: Gadus morhua
    keywords:
      - eDNA
      - metabarcoding
    papers:
      - zotero_key: ABC123XYZ
        title: "eDNA monitoring of Atlantic cod..."
        authors:
          - Smith, John
          - Doe, Jane
        year: '2023'
        doi: 10.1234/example
        source: PubMed
        url: https://pubmed.ncbi.nlm.nih.gov/12345/
        abstract: "This study presents..."
        added_at: '2025-12-26T10:30:00'
```

### Using the Abstract Cache for LLM Analysis

The abstract cache is designed for easy integration with LLM workflows:

```python
from src.abstract_cache import AbstractCache

cache = AbstractCache()

# Get formatted text for LLM analysis
abstracts_text = cache.get_all_abstracts_text("Gadus morhua")

# Send to LLM for analysis
# Example: Analyze species characteristics, summarize findings, etc.
```
