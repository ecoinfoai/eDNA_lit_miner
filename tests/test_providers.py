import pytest
from unittest.mock import MagicMock
from src.providers.base import SearchResult
from src.providers.pubmed import PubMedProvider
from src.providers.semantic_scholar import SemanticScholarProvider

# --- PubMed Tests ---

@pytest.fixture
def mock_entrez(mocker):
    return mocker.patch("src.providers.pubmed.Entrez")

def test_pubmed_init(mock_entrez):
    provider = PubMedProvider("test@email.com")
    assert mock_entrez.email == "test@email.com"

def test_pubmed_search_success(mock_entrez):
    provider = PubMedProvider("test@email.com")

    # Mock esearch
    mock_handle_search = MagicMock()
    mock_entrez.esearch.return_value = mock_handle_search
    mock_entrez.read.side_effect = [
        {"IdList": ["12345"]}, # esearch result
        { # efetch result
            "PubmedArticle": [{
                "MedlineCitation": {
                    "PMID": "12345",
                    "Article": {
                        "ArticleTitle": "Test Title",
                        "AuthorList": [
                            {"LastName": "Doe", "ForeName": "John"},
                            {"LastName": "Smith", "ForeName": "Jane"}
                        ],
                        "Journal": {
                            "JournalIssue": {
                                "PubDate": {"Year": "2023"}
                            }
                        },
                        "ELocationID": [
                            MagicMock(attributes={"EIdType": "doi"}, __str__=lambda x: "10.1000/12345")
                        ],
                        "Abstract": {
                            "AbstractText": ["Abstract part 1", " part 2"]
                        }
                    }
                }
            }]
        }
    ]

    results = provider.search("query")

    assert len(results) == 1
    res = results[0]
    assert res.title == "Test Title"
    assert res.authors == ["Doe, John", "Smith, Jane"]
    assert res.year == "2023"
    assert res.doi == "10.1000/12345"
    assert res.url == "https://pubmed.ncbi.nlm.nih.gov/12345/"
    assert res.abstract == "Abstract part 1  part 2" # space joined

def test_pubmed_search_no_ids(mock_entrez):
    provider = PubMedProvider("test@email.com")
    mock_entrez.read.return_value = {"IdList": []}
    
    results = provider.search("query")
    assert len(results) == 0

def test_pubmed_search_exception(mock_entrez):
    provider = PubMedProvider("test@email.com")
    mock_entrez.esearch.side_effect = Exception("Network Error")

    results = provider.search("query")
    assert len(results) == 0

def test_pubmed_search_abstract_string(mock_entrez):
    provider = PubMedProvider("test@email.com")
    mock_entrez.read.side_effect = [
        {"IdList": ["12345"]},
        {
            "PubmedArticle": [{
                "MedlineCitation": {
                    "PMID": "12345",
                    "Article": {
                        "ArticleTitle": "Title",
                        "AuthorList": [],
                        "Journal": {"JournalIssue": {"PubDate": {"Year": "2023"}}},
                        "Abstract": {"AbstractText": "Single string abstract"}
                    }
                }
            }]
        }
    ]
    results = provider.search("query")
    assert results[0].abstract == "Single string abstract"

# --- Semantic Scholar Tests ---

@pytest.fixture
def mock_sch(mocker):
    return mocker.patch("src.providers.semantic_scholar.SemanticScholar")

def test_semantic_init(mock_sch):
    provider = SemanticScholarProvider("api_key")
    mock_sch.assert_called_with(api_key="api_key")

def test_semantic_search_success(mock_sch):
    provider = SemanticScholarProvider()
    sch_instance = mock_sch.return_value
    
    # Mock Paper object
    paper = MagicMock()
    paper.title = "SS Title"
    paper.year = 2022
    paper.externalIds = {'DOI': '10.5555/ss'}
    paper.url = "http://ss.url"
    paper.abstract = "SS Abstract"
    author1 = MagicMock()
    author1.name = "Author One"
    paper.authors = [author1]
    
    sch_instance.search_paper.return_value = [paper]
    
    results = provider.search("query")
    
    assert len(results) == 1
    res = results[0]
    assert res.title == "SS Title"
    assert res.year == "2022"
    assert res.doi == "10.5555/ss"
    assert res.authors == ["Author One"]

def test_semantic_search_exception(mock_sch):
    provider = SemanticScholarProvider()
    sch_instance = mock_sch.return_value
    sch_instance.search_paper.side_effect = Exception("API Error")

    results = provider.search("query")
    assert len(results) == 0

def test_semantic_search_empty_fields(mock_sch):
    provider = SemanticScholarProvider()
    sch_instance = mock_sch.return_value

    paper = MagicMock()
    paper.title = None
    paper.year = None
    paper.externalIds = None
    paper.url = None
    paper.abstract = None
    paper.authors = None
    paper.publicationVenue = None # Forcing missing DOI path
    
    sch_instance.search_paper.return_value = [paper]

    results = provider.search("query")
    assert len(results) == 1
    res = results[0]
    assert res.title == ""
    assert res.year == ""
    assert res.doi == ""
    assert res.authors == []

def test_semantic_search_doi_fallback(mock_sch):
    provider = SemanticScholarProvider()
    sch_instance = mock_sch.return_value

    paper = MagicMock()
    paper.title = "Title"
    paper.year = 2023
    paper.externalIds = {} # Empty externalIds
    paper.authors = []

    # Trigger the pass line
    paper.publicationVenue = {"name": "Venue"}

    sch_instance.search_paper.return_value = [paper]

    results = provider.search("query")
    assert len(results) == 1
    assert results[0].doi == ""
