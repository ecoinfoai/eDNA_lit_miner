from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

@dataclass
class SearchResult:
    title: str
    authors: List[str]
    year: str
    doi: str
    source: str  # 'PubMed' or 'SemanticScholar'
    abstract: str = ""
    url: str = ""

class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        pass
