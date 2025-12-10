import pytest
from src.providers.base import SearchResult, SearchProvider

def test_search_result_creation():
    res = SearchResult("Title", ["Author"], "2023", "doi", "Source")
    assert res.title == "Title"
    assert res.authors == ["Author"]
    assert res.year == "2023"
    assert res.doi == "doi"
    assert res.source == "Source"
    assert res.abstract == ""
    assert res.url == ""

def test_search_provider_abstract():
    # This is to cover the abstract method in ABC which is usually skipped but let's see
    class ConcreteProvider(SearchProvider):
        def search(self, query: str, limit: int = 10):
            return []

    provider = ConcreteProvider()
    assert provider.search("query") == []

    # Check that abstract method raises error if not implemented
    class BadProvider(SearchProvider):
        pass

    with pytest.raises(TypeError):
        BadProvider()

def test_search_provider_base_method():
    # Attempt to call the abstract method directly on a mock object that inherits from it?
    # No, we need to call SearchProvider.search(obj, ...) to hit the line 'pass'

    # Actually, the line 18 'pass' inside @abstractmethod is almost impossible to cover
    # because abstract methods are overridden or the class cannot be instantiated.
    # However, if we define a class that calls super().search(), we might hit it?
    # But ABC abstract methods might raise if called.

    class SuperCallingProvider(SearchProvider):
        def search(self, query: str, limit: int = 10):
            super().search(query, limit)
            return []

    provider = SuperCallingProvider()
    # Calling the abstract method usually does nothing (it's empty body)
    provider.search("q")
