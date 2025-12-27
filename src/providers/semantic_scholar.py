from typing import List
from semanticscholar import SemanticScholar
from src.providers.base import SearchProvider, SearchResult

class SemanticScholarProvider(SearchProvider):
    def __init__(self, api_key: str = None):
        if not api_key:
            api_key = None
        self.sch = SemanticScholar(api_key=api_key)

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        try:
            # search_paper returns a PaginatedResults object
            results = self.sch.search_paper(query, limit=limit)
            
            search_results = []
            for item in results:
                # item is a Paper object
                authors = [author.name for author in item.authors] if item.authors else []
                
                # Handling potentially missing fields gracefully
                title = item.title if item.title else ""
                year = str(item.year) if item.year else ""
                doi = item.externalIds.get('DOI') if item.externalIds else ""
                url = item.url if item.url else ""
                abstract = item.abstract if item.abstract else ""

                search_results.append(SearchResult(
                    title=title,
                    authors=authors,
                    year=year,
                    doi=doi if doi else "",
                    source="SemanticScholar",
                    abstract=abstract,
                    url=url
                ))
            
            return search_results

        except Exception as e:
            print(f"Error searching Semantic Scholar: {e}")
            return []
