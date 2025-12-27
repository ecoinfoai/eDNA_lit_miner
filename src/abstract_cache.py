import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from src.providers.base import SearchResult


class AbstractCache:
    """
    Manages a YAML cache of paper abstracts and bibliographic information.
    All papers are stored in a single YAML file, organized by species.
    """

    def __init__(self, cache_file: str = "data/abstracts_cache.yaml"):
        """
        Initialize the AbstractCache.

        Args:
            cache_file: Path to the YAML cache file (default: data/abstracts_cache.yaml)
        """
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize cache file if it doesn't exist
        if not self.cache_file.exists():
            self._initialize_cache()

    def _initialize_cache(self):
        """Create an empty cache file with initial structure."""
        initial_data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_species': 0,
                'total_papers': 0
            },
            'species': []
        }
        self._write_cache(initial_data)

    def _read_cache(self) -> Dict:
        """Read and parse the YAML cache file."""
        with open(self.cache_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def _write_cache(self, data: Dict):
        """Write data to the YAML cache file."""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    def add_papers(self, species_name: str, papers: List[SearchResult], zotero_keys: List[str],
                   keywords: Optional[List[str]] = None):
        """
        Add papers to the cache for a specific species.

        Args:
            species_name: Name of the species
            papers: List of SearchResult objects
            zotero_keys: List of Zotero item keys corresponding to each paper
            keywords: Optional list of search keywords used
        """
        cache_data = self._read_cache()

        # Find or create species entry
        species_entry = None
        for sp in cache_data.get('species', []):
            if sp['name'] == species_name:
                species_entry = sp
                break

        if species_entry is None:
            species_entry = {
                'name': species_name,
                'keywords': keywords or [],
                'papers': [],
                'added_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            if 'species' not in cache_data:
                cache_data['species'] = []
            cache_data['species'].append(species_entry)
        else:
            species_entry['last_updated'] = datetime.now().isoformat()

        # Add papers to species entry
        for paper, zotero_key in zip(papers, zotero_keys):
            paper_entry = {
                'zotero_key': zotero_key,
                'title': paper.title,
                'authors': paper.authors,
                'year': paper.year,
                'doi': paper.doi,
                'source': paper.source,
                'url': paper.url,
                'abstract': paper.abstract,
                'added_at': datetime.now().isoformat()
            }
            species_entry['papers'].append(paper_entry)

        # Update metadata
        cache_data['metadata']['last_updated'] = datetime.now().isoformat()
        cache_data['metadata']['total_species'] = len(cache_data.get('species', []))
        cache_data['metadata']['total_papers'] = sum(
            len(sp.get('papers', [])) for sp in cache_data.get('species', [])
        )

        self._write_cache(cache_data)

    def get_species_papers(self, species_name: str) -> Optional[Dict]:
        """
        Retrieve all papers for a specific species.

        Args:
            species_name: Name of the species

        Returns:
            Dictionary containing species information and papers, or None if not found
        """
        cache_data = self._read_cache()
        for sp in cache_data.get('species', []):
            if sp['name'] == species_name:
                return sp
        return None

    def get_all_abstracts_text(self, species_name: str) -> str:
        """
        Get all abstracts for a species formatted as plain text for LLM analysis.

        Args:
            species_name: Name of the species

        Returns:
            Formatted string containing all abstracts
        """
        species_data = self.get_species_papers(species_name)
        if not species_data:
            return ""

        text = f"Species: {species_name}\n"
        text += f"Total papers: {len(species_data.get('papers', []))}\n\n"

        for i, paper in enumerate(species_data.get('papers', []), 1):
            text += f"--- Paper {i} ---\n"
            text += f"Title: {paper.get('title', 'N/A')}\n"
            text += f"Authors: {', '.join(paper.get('authors', []))}\n"
            text += f"Year: {paper.get('year', 'N/A')}\n"
            text += f"DOI: {paper.get('doi', 'N/A')}\n"
            text += f"Source: {paper.get('source', 'N/A')}\n"
            text += f"Zotero Key: {paper.get('zotero_key', 'N/A')}\n"
            text += f"\nAbstract:\n{paper.get('abstract', 'N/A')}\n\n"

        return text

    def get_statistics(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dictionary containing cache statistics
        """
        cache_data = self._read_cache()
        return cache_data.get('metadata', {})
