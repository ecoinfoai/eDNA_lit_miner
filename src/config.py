import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    ZOTERO_LIBRARY_ID: str = None
    ZOTERO_API_KEY: str = None
    ZOTERO_LIBRARY_TYPE: str = None
    SEMANTIC_SCHOLAR_API_KEY: str = None
    EMAIL: str = None

    def __post_init__(self):
        if self.ZOTERO_LIBRARY_ID is None:
            self.ZOTERO_LIBRARY_ID = os.getenv("ZOTERO_LIBRARY_ID", "")
        if self.ZOTERO_API_KEY is None:
            self.ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY", "")
        if self.ZOTERO_LIBRARY_TYPE is None:
            self.ZOTERO_LIBRARY_TYPE = os.getenv("ZOTERO_LIBRARY_TYPE", "group")
        if self.SEMANTIC_SCHOLAR_API_KEY is None:
            self.SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
        if self.EMAIL is None:
            self.EMAIL = os.getenv("EMAIL", "")

    def validate(self):
        errors = []
        if not self.ZOTERO_LIBRARY_ID:
            errors.append("ZOTERO_LIBRARY_ID is missing")
        if not self.ZOTERO_API_KEY:
            errors.append("ZOTERO_API_KEY is missing")
        if not self.EMAIL:
            errors.append("EMAIL is missing (required for PubMed)")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
