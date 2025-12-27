import sys
from unittest.mock import MagicMock, patch
import pytest
from src.main import main
from src.input_manager import SpeciesQuery
from src.providers.base import SearchResult

@pytest.fixture
def mock_args():
    with patch('argparse.ArgumentParser.parse_args') as mock_parse:
        yield mock_parse

@pytest.fixture
def mock_config():
    with patch('src.main.Config') as mock:
        yield mock

@pytest.fixture
def mock_input_manager():
    with patch('src.main.InputManager') as mock:
        yield mock

@pytest.fixture
def mock_providers():
    with patch('src.main.PubMedProvider') as mock_pubmed, \
         patch('src.main.SemanticScholarProvider') as mock_semantic:
        yield mock_pubmed, mock_semantic

@pytest.fixture
def mock_zotero_manager():
    with patch('src.main.ZoteroManager') as mock:
        yield mock

def test_main_dry_run_success(mock_args, mock_config, mock_input_manager, mock_providers, capsys):
    # Setup mocks
    args = MagicMock()
    args.species_list = "species.yaml"
    args.dry_run = True
    args.limit = 10
    mock_args.return_value = args

    config_instance = mock_config.return_value
    config_instance.EMAIL = None

    input_instance = mock_input_manager.return_value
    input_instance.load_species_list.return_value = [
        SpeciesQuery(species_name="Gadus morhua", synonyms=["Atlantic cod"], keywords=["eDNA"])
    ]

    mock_pubmed_cls, mock_semantic_cls = mock_providers
    mock_pubmed = mock_pubmed_cls.return_value
    mock_semantic = mock_semantic_cls.return_value

    mock_pubmed.search.return_value = [
        SearchResult(source="PubMed", title="Title 1", doi="10.1234/1", year="2023", url="http://url1", authors=["Author A"])
    ]
    mock_semantic.search.return_value = [
        SearchResult(source="Semantic Scholar", title="Title 2", doi="10.1234/2", year="2023", url="http://url2", authors=["Author B"])
    ]

    # Run main
    main()

    # Assertions
    captured = capsys.readouterr()
    assert "Configuration loaded." in captured.out
    assert "Loaded 1 species" in captured.out
    assert "Dry Run: Using dummy email for PubMed." in captured.out
    assert "Processing species: Gadus morhua" in captured.out
    assert "Dry Run: Skipping Zotero upload and cache." in captured.out
    assert "Processing Complete." in captured.out

    config_instance.validate.assert_not_called()

def test_main_full_run_success(mock_args, mock_config, mock_input_manager, mock_providers, mock_zotero_manager, capsys):
    # Setup mocks
    args = MagicMock()
    args.species_list = "species.yaml"
    args.dry_run = False
    args.limit = 5
    mock_args.return_value = args

    config_instance = mock_config.return_value
    config_instance.EMAIL = "test@example.com"
    config_instance.ZOTERO_LIBRARY_ID = "123"
    config_instance.ZOTERO_API_KEY = "key"
    config_instance.ZOTERO_LIBRARY_TYPE = "group"
    config_instance.SEMANTIC_SCHOLAR_API_KEY = "semkey"

    input_instance = mock_input_manager.return_value
    input_instance.load_species_list.return_value = [
        SpeciesQuery(species_name="Gadus morhua", synonyms=[], keywords=[])
    ]

    mock_pubmed_cls, mock_semantic_cls = mock_providers
    mock_pubmed = mock_pubmed_cls.return_value
    mock_semantic = mock_semantic_cls.return_value

    mock_pubmed.search.return_value = [
        SearchResult(source="PubMed", title="T1", doi="d1", year="2023", url="u1", authors=["A1"])
    ]
    mock_semantic.search.return_value = []

    zotero_instance = mock_zotero_manager.return_value
    zotero_instance.create_or_get_collection.return_value = "col123"
    zotero_instance.add_item.return_value = "item123"

    # Run main
    main()

    # Assertions
    captured = capsys.readouterr()
    assert "Configuration loaded." in captured.out
    assert "PubMed Provider initialized." in captured.out
    assert "Zotero Manager initialized." in captured.out
    assert "Target Collection ID: col123" in captured.out

    config_instance.validate.assert_called_once()
    zotero_instance.create_or_get_collection.assert_called()
    zotero_instance.add_item.assert_called()

def test_main_config_error(mock_args, mock_config, capsys):
    args = MagicMock()
    args.species_list = "species.yaml"
    args.dry_run = False
    mock_args.return_value = args

    mock_config.side_effect = Exception("Config init failed")

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "Configuration Error: Config init failed" in captured.out

def test_main_input_error(mock_args, mock_config, mock_input_manager, capsys):
    args = MagicMock()
    args.species_list = "species.yaml"
    args.dry_run = False
    mock_args.return_value = args

    mock_input_manager.side_effect = Exception("File not found")

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "Input Error: File not found" in captured.out

def test_main_no_providers(mock_args, mock_config, mock_input_manager, mock_providers, capsys):
    args = MagicMock()
    args.species_list = "species.yaml"
    args.dry_run = False
    mock_args.return_value = args

    config_instance = mock_config.return_value
    config_instance.EMAIL = None # No email for PubMed

    mock_pubmed_cls, mock_semantic_cls = mock_providers
    mock_semantic_cls.side_effect = Exception("Semantic Scholar failed")

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "Warning: EMAIL env var not set, skipping PubMed." in captured.out
    assert "Failed to init Semantic Scholar Provider" in captured.out
    assert "No search providers available. Exiting." in captured.out

def test_main_zotero_init_error(mock_args, mock_config, mock_input_manager, mock_providers, mock_zotero_manager, capsys):
    args = MagicMock()
    args.species_list = "species.yaml"
    args.dry_run = False
    mock_args.return_value = args

    config_instance = mock_config.return_value
    config_instance.EMAIL = "test@example.com"

    mock_zotero_manager.side_effect = Exception("Zotero Login failed")

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "Zotero Init Error: Zotero Login failed" in captured.out

def test_main_zotero_process_error(mock_args, mock_config, mock_input_manager, mock_providers, mock_zotero_manager, capsys):
    args = MagicMock()
    args.species_list = "species.yaml"
    args.dry_run = False
    mock_args.return_value = args

    config_instance = mock_config.return_value
    config_instance.EMAIL = "test@example.com"

    input_instance = mock_input_manager.return_value
    input_instance.load_species_list.return_value = [
         SpeciesQuery(species_name="Gadus morhua", synonyms=[], keywords=[])
    ]

    mock_pubmed_cls, mock_semantic_cls = mock_providers
    mock_pubmed = mock_pubmed_cls.return_value
    mock_pubmed.search.return_value = [SearchResult(source="PubMed", title="T1", doi="d1", year="2023", url="u1", authors=["A1"])]

    zotero_instance = mock_zotero_manager.return_value
    zotero_instance.create_or_get_collection.side_effect = Exception("Collection error")

    main()

    captured = capsys.readouterr()
    assert "Error processing Zotero for Gadus morhua: Collection error" in captured.out

def test_query_building(mock_args, mock_config, mock_input_manager, mock_providers, capsys):
    args = MagicMock()
    args.species_list = "species.yaml"
    args.dry_run = True
    mock_args.return_value = args

    input_instance = mock_input_manager.return_value
    input_instance.load_species_list.return_value = [
        SpeciesQuery(species_name="Sp1", synonyms=["Syn1", "Syn2"], keywords=["Kw1", "Kw2"], date_range="2020:2024")
    ]

    mock_pubmed_cls, _ = mock_providers
    mock_pubmed = mock_pubmed_cls.return_value
    mock_pubmed.search.return_value = []

    main()

    captured = capsys.readouterr()
    # Check if the query is printed
    # Query should be: ("Sp1" OR "Syn1" OR "Syn2") AND ("Kw1" OR "Kw2")
    # Note: The code wraps each term in quotes
    expected_query = '("Sp1" OR "Syn1" OR "Syn2") AND ("Kw1" OR "Kw2")'
    assert f"Query: {expected_query}" in captured.out

def test_deduplication(mock_args, mock_config, mock_input_manager, mock_providers, capsys):
    args = MagicMock()
    args.species_list = "species.yaml"
    args.dry_run = True
    mock_args.return_value = args

    input_instance = mock_input_manager.return_value
    input_instance.load_species_list.return_value = [SpeciesQuery(species_name="Sp1", synonyms=[], keywords=[])]

    mock_pubmed_cls, mock_semantic_cls = mock_providers
    mock_pubmed = mock_pubmed_cls.return_value
    mock_semantic = mock_semantic_cls.return_value

    # Same DOI
    res1 = SearchResult(source="S1", title="Title 1", doi="doi1", year="2023", url="u1", authors=["A1"])
    res2 = SearchResult(source="S2", title="Title 1 Diff", doi="doi1", year="2023", url="u2", authors=["A2"])
    # Different DOI, same title (normalized)
    res3 = SearchResult(source="S3", title="  Unique Title  ", doi=None, year="2023", url="u3", authors=["A3"])
    res4 = SearchResult(source="S4", title="unique title", doi=None, year="2023", url="u4", authors=["A4"])

    mock_pubmed.search.return_value = [res1, res3]
    mock_semantic.search.return_value = [res2, res4]

    main()

    captured = capsys.readouterr()
    assert "Found 2 results." in captured.out
    # Total unique results should be 2: one for doi1, one for "unique title"
    assert "Total unique results: 2" in captured.out

def test_provider_init_fail(mock_args, mock_config, mock_input_manager, mock_providers, capsys):
    args = MagicMock()
    args.species_list = "species.yaml"
    args.dry_run = True
    mock_args.return_value = args

    config_instance = mock_config.return_value
    config_instance.EMAIL = "email@test.com"

    mock_pubmed_cls, mock_semantic_cls = mock_providers
    mock_pubmed_cls.side_effect = Exception("PubMed Fail")

    # Semantic succeeds
    mock_semantic = mock_semantic_cls.return_value
    mock_semantic.search.return_value = []

    input_instance = mock_input_manager.return_value
    input_instance.load_species_list.return_value = [SpeciesQuery(species_name="Sp1", synonyms=[], keywords=[])]

    main()

    captured = capsys.readouterr()
    assert "Failed to init PubMed Provider: PubMed Fail" in captured.out
    assert "Semantic Scholar Provider initialized." in captured.out

def test_keyword_single(mock_args, mock_config, mock_input_manager, mock_providers, capsys):
    args = MagicMock()
    args.species_list = "species.yaml"
    args.dry_run = True
    mock_args.return_value = args

    input_instance = mock_input_manager.return_value
    input_instance.load_species_list.return_value = [
        SpeciesQuery(species_name="Sp1", synonyms=[], keywords=["SingleKW"])
    ]

    mock_pubmed_cls, _ = mock_providers
    mock_pubmed = mock_pubmed_cls.return_value
    mock_pubmed.search.return_value = []

    main()

    captured = capsys.readouterr()
    expected_query = '"Sp1" AND "SingleKW"'
    assert f"Query: {expected_query}" in captured.out
