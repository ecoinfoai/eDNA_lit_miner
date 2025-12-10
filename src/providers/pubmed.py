from typing import List
from Bio import Entrez
from src.providers.base import SearchProvider, SearchResult

class PubMedProvider(SearchProvider):
    def __init__(self, email: str):
        Entrez.email = email

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        try:
            # 1. Search for IDs
            handle = Entrez.esearch(db="pubmed", term=query, retmax=limit)
            record = Entrez.read(handle)
            handle.close()
            
            id_list = record.get("IdList", [])
            if not id_list:
                return []

            # 2. Fetch details for IDs
            handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="text")
            # We use Medline parser or simply parse xml. let's use xml for better structured data, 
            # but usually Medline format is good for parsing. 
            # Actually, let's use retmode='xml' and Entrez.read for easier parsing of multiple items.
            handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
            papers = Entrez.read(handle)
            handle.close()

            results = []
            # 'PubmedArticle' usually contains the list
            article_list = papers.get("PubmedArticle", [])
            
            for article in article_list:
                medline_citation = article.get("MedlineCitation", {})
                article_data = medline_citation.get("Article", {})
                
                # Title
                title = article_data.get("ArticleTitle", "")
                
                # Authors
                author_list = article_data.get("AuthorList", [])
                authors = []
                for author in author_list:
                    last_name = author.get("LastName", "")
                    fore_name = author.get("ForeName", "")
                    if last_name or fore_name:
                        authors.append(f"{last_name}, {fore_name}")

                # Year
                journal = article_data.get("Journal", {})
                journal_issue = journal.get("JournalIssue", {})
                pub_date = journal_issue.get("PubDate", {})
                year = pub_date.get("Year", "")
                
                # DOI and URL
                doi = ""
                elocation_id = article_data.get("ELocationID", [])
                for eid in elocation_id:
                    if eid.attributes.get("EIdType") == "doi":
                        doi = str(eid)
                        break
                
                url = f"https://pubmed.ncbi.nlm.nih.gov/{medline_citation.get('PMID', '')}/"

                # Abstract
                abstract_text = ""
                abstract = article_data.get("Abstract", {})
                if "AbstractText" in abstract:
                    # AbstractText can be a list or single string
                    abstract_parts = abstract["AbstractText"]
                    if isinstance(abstract_parts, list):
                         abstract_text = " ".join([str(x) for x in abstract_parts])
                    else:
                        abstract_text = str(abstract_parts)


                results.append(SearchResult(
                    title=title,
                    authors=authors,
                    year=year,
                    doi=doi,
                    source="PubMed",
                    abstract=abstract_text,
                    url=url
                ))
                
            return results

        except Exception as e:
            print(f"Error searching PubMed: {e}")
            return []
