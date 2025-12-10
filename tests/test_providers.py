import pytest
from unittest.mock import MagicMock, patch
from src.providers.pubmed import PubMedProvider
from src.providers.semantic_scholar import SemanticScholarProvider
from src.providers.base import SearchResult

# --- PubMed Tests ---

@patch('src.providers.pubmed.Entrez')
def test_pubmed_search(mock_entrez):
    # Mock esearch response
    mock_entrez.esearch.return_value = MagicMock()
    mock_entrez.read.side_effect = [
        {"IdList": ["12345", "67890"]},  # First call for esearch
        { # Second call for efetch
            "PubmedArticle": [
                {
                    "MedlineCitation": {
                        "PMID": "12345",
                        "Article": {
                            "ArticleTitle": "Test Title 1",
                            "AuthorList": [{"LastName": "Doe", "ForeName": "John"}],
                            "Journal": {"JournalIssue": {"PubDate": {"Year": "2023"}}},
                            "ELocationID": [],
                            "Abstract": {"AbstractText": ["Abstract 1"]}
                        }
                    }
                }
            ]
        } 
    ]

    provider = PubMedProvider(email="test@example.com")
    results = provider.search("eDNA")

    assert len(results) == 1
    assert results[0].title == "Test Title 1"
    assert results[0].authors == ["Doe, John"]
    assert results[0].year == "2023"
    assert results[0].source == "PubMed"

@patch('src.providers.pubmed.Entrez')
def test_pubmed_search_no_results(mock_entrez):
    mock_entrez.esearch.return_value = MagicMock()
    mock_entrez.read.return_value = {"IdList": []}
    
    provider = PubMedProvider(email="test@example.com")
    results = provider.search("empty")
    assert len(results) == 0

# --- Semantic Scholar Tests ---

@patch('src.providers.semantic_scholar.SemanticScholar')
def test_semantic_scholar_search(mock_sch_cls):
    mock_sch_instance = mock_sch_cls.return_value
    
    # Mock Paper object
    mock_paper = MagicMock()
    mock_paper.title = "Test Paper"
    mock_paper.year = 2022
    mock_paper.externalIds = {'DOI': '10.1234/test'}
    mock_paper.url = "http://test.com"
    mock_paper.abstract = "Abstract test"
    
    mock_author = MagicMock()
    mock_author.name = "Jane Doe"
    mock_paper.authors = [mock_author]
    
    mock_sch_instance.search_paper.return_value = [mock_paper]
    
    provider = SemanticScholarProvider()
    results = provider.search("query")
    
    assert len(results) == 1
    assert results[0].title == "Test Paper"
    assert results[0].authors == ["Jane Doe"]
    assert results[0].doi == "10.1234/test"
    assert results[0].source == "SemanticScholar"

@patch('src.providers.semantic_scholar.SemanticScholar')
def test_semantic_scholar_error(mock_sch_cls):
    mock_sch_instance = mock_sch_cls.return_value
    mock_sch_instance.search_paper.side_effect = Exception("API Error")
    
    provider = SemanticScholarProvider()
    results = provider.search("error_query")
    assert len(results) == 0
