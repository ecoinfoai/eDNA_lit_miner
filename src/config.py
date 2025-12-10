import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    ZOTERO_LIBRARY_ID: str = os.getenv("ZOTERO_LIBRARY_ID", "")
    ZOTERO_API_KEY: str = os.getenv("ZOTERO_API_KEY", "")
    ZOTERO_LIBRARY_TYPE: str = os.getenv("ZOTERO_LIBRARY_TYPE", "group")
    SEMANTIC_SCHOLAR_API_KEY: str = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    EMAIL: str = os.getenv("EMAIL", "")

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
