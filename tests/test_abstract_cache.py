import pytest
import yaml
from pathlib import Path
from src.abstract_cache import AbstractCache
from src.providers.base import SearchResult


@pytest.fixture
def temp_cache_file(tmp_path):
    """Create a temporary cache file for testing."""
    cache_file = tmp_path / "test_cache.yaml"
    return str(cache_file)


@pytest.fixture
def cache(temp_cache_file):
    """Create an AbstractCache instance with a temporary file."""
    return AbstractCache(cache_file=temp_cache_file)


@pytest.fixture
def sample_papers():
    """Create sample SearchResult objects for testing."""
    return [
        SearchResult(
            title="eDNA study of Gadus morhua",
            authors=["Smith, John", "Doe, Jane"],
            year="2023",
            doi="10.1234/test1",
            source="PubMed",
            abstract="This is a test abstract about eDNA detection.",
            url="https://pubmed.ncbi.nlm.nih.gov/12345/"
        ),
        SearchResult(
            title="Metabarcoding analysis",
            authors=["Johnson, A."],
            year="2024",
            doi="10.5678/test2",
            source="SemanticScholar",
            abstract="Another abstract about metabarcoding techniques.",
            url="https://www.semanticscholar.org/paper/abc123"
        )
    ]


def test_initialization_creates_file(temp_cache_file):
    """Test that initialization creates a cache file."""
    cache = AbstractCache(cache_file=temp_cache_file)
    assert Path(temp_cache_file).exists()


def test_initialization_creates_structure(temp_cache_file):
    """Test that initialization creates the correct YAML structure."""
    cache = AbstractCache(cache_file=temp_cache_file)

    with open(temp_cache_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    assert 'metadata' in data
    assert 'species' in data
    assert data['metadata']['total_species'] == 0
    assert data['metadata']['total_papers'] == 0


def test_add_papers_new_species(cache, sample_papers, temp_cache_file):
    """Test adding papers for a new species."""
    zotero_keys = ["ZOTERO123", "ZOTERO456"]
    keywords = ["eDNA", "metabarcoding"]

    cache.add_papers(
        species_name="Gadus morhua",
        papers=sample_papers,
        zotero_keys=zotero_keys,
        keywords=keywords
    )

    # Read the cache file
    with open(temp_cache_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    assert len(data['species']) == 1
    species = data['species'][0]
    assert species['name'] == "Gadus morhua"
    assert species['keywords'] == keywords
    assert len(species['papers']) == 2

    # Check paper data
    paper1 = species['papers'][0]
    assert paper1['zotero_key'] == "ZOTERO123"
    assert paper1['title'] == "eDNA study of Gadus morhua"
    assert paper1['doi'] == "10.1234/test1"
    assert paper1['abstract'] == "This is a test abstract about eDNA detection."


def test_add_papers_existing_species(cache, sample_papers):
    """Test adding more papers to an existing species."""
    zotero_keys1 = ["ZOTERO123"]
    cache.add_papers(
        species_name="Gadus morhua",
        papers=[sample_papers[0]],
        zotero_keys=zotero_keys1,
        keywords=["eDNA"]
    )

    zotero_keys2 = ["ZOTERO456"]
    cache.add_papers(
        species_name="Gadus morhua",
        papers=[sample_papers[1]],
        zotero_keys=zotero_keys2,
        keywords=["metabarcoding"]
    )

    species_data = cache.get_species_papers("Gadus morhua")
    assert species_data is not None
    assert len(species_data['papers']) == 2


def test_get_species_papers_existing(cache, sample_papers):
    """Test retrieving papers for an existing species."""
    zotero_keys = ["ZOTERO123", "ZOTERO456"]
    cache.add_papers(
        species_name="Salmo salar",
        papers=sample_papers,
        zotero_keys=zotero_keys
    )

    species_data = cache.get_species_papers("Salmo salar")
    assert species_data is not None
    assert species_data['name'] == "Salmo salar"
    assert len(species_data['papers']) == 2


def test_get_species_papers_nonexistent(cache):
    """Test retrieving papers for a non-existent species."""
    species_data = cache.get_species_papers("Nonexistent species")
    assert species_data is None


def test_get_all_abstracts_text(cache, sample_papers):
    """Test generating formatted text for LLM analysis."""
    zotero_keys = ["ZOTERO123", "ZOTERO456"]
    cache.add_papers(
        species_name="Gadus morhua",
        papers=sample_papers,
        zotero_keys=zotero_keys
    )

    text = cache.get_all_abstracts_text("Gadus morhua")

    assert "Species: Gadus morhua" in text
    assert "Total papers: 2" in text
    assert "Paper 1" in text
    assert "Paper 2" in text
    assert "eDNA study of Gadus morhua" in text
    assert "Metabarcoding analysis" in text
    assert "This is a test abstract about eDNA detection." in text
    assert "ZOTERO123" in text
    assert "ZOTERO456" in text


def test_get_all_abstracts_text_nonexistent(cache):
    """Test getting abstracts for non-existent species."""
    text = cache.get_all_abstracts_text("Nonexistent species")
    assert text == ""


def test_get_statistics(cache, sample_papers):
    """Test getting cache statistics."""
    # Add papers for two species
    cache.add_papers("Species 1", [sample_papers[0]], ["KEY1"])
    cache.add_papers("Species 2", [sample_papers[1]], ["KEY2"])

    stats = cache.get_statistics()

    assert stats['total_species'] == 2
    assert stats['total_papers'] == 2
    assert 'last_updated' in stats
    assert 'created_at' in stats


def test_metadata_updates(cache, sample_papers, temp_cache_file):
    """Test that metadata is updated correctly."""
    cache.add_papers("Species 1", [sample_papers[0]], ["KEY1"])

    with open(temp_cache_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    assert data['metadata']['total_species'] == 1
    assert data['metadata']['total_papers'] == 1

    # Add another species
    cache.add_papers("Species 2", [sample_papers[1]], ["KEY2"])

    with open(temp_cache_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    assert data['metadata']['total_species'] == 2
    assert data['metadata']['total_papers'] == 2


def test_multiple_species(cache, sample_papers):
    """Test handling multiple species in the cache."""
    cache.add_papers("Gadus morhua", [sample_papers[0]], ["KEY1"], ["eDNA"])
    cache.add_papers("Salmo salar", [sample_papers[1]], ["KEY2"], ["metabarcoding"])

    gadus_data = cache.get_species_papers("Gadus morhua")
    salmo_data = cache.get_species_papers("Salmo salar")

    assert gadus_data['name'] == "Gadus morhua"
    assert salmo_data['name'] == "Salmo salar"
    assert len(gadus_data['papers']) == 1
    assert len(salmo_data['papers']) == 1
