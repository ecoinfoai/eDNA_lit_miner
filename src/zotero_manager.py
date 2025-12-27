from pyzotero import zotero
from typing import List
from src.providers.base import SearchResult

class ZoteroManager:
    def __init__(self, library_id: str, api_key: str, library_type: str = 'group'):
        self.zot = zotero.Zotero(library_id, library_type, api_key)

    def create_or_get_collection(self, name: str) -> str:
        """
        Creates a collection if it doesn't exist, otherwise returns the ID of the existing one.
        """
        try:
            # 1. Fetch all collections
            collections = self.zot.collections()
            
            # 2. Check if name exists
            for col in collections:
                if col['data']['name'] == name:
                    return col['key']
            
            # 3. Create if not found
            resp = self.zot.create_collections([{'name': name}])
            if resp and 'successful' in resp and resp['successful']:
                # The response structure for create_collections returns a dict with 'successful' 
                # mapping 0 -> {'key': '...', ...}
                return resp['successful']['0']['key']
            else:
                raise Exception(f"Failed to create collection '{name}'. Response: {resp}")

        except Exception as e:
            print(f"Error in Zotero create_or_get_collection: {e}")
            raise

    def add_item(self, item: SearchResult, collection_id: str) -> str:
        """
        Adds a SearchResult to a specific collection. Returns the Item Key.
        """
        try:
            # Create a template item provided by pyzotero
            template = self.zot.item_template('journalArticle')
            
            template['title'] = item.title
            
            # Parse authors
            creators = []
            for author_name in item.authors:
                parts = author_name.split(',', 1)
                if len(parts) == 2:
                    creators.append({'creatorType': 'author', 'lastName': parts[0].strip(), 'firstName': parts[1].strip()})
                else:
                    creators.append({'creatorType': 'author', 'name': author_name.strip()})
            template['creators'] = creators
            
            template['date'] = item.year
            template['DOI'] = item.doi
            template['url'] = item.url
            template['abstractNote'] = item.abstract
            template['libraryCatalog'] = item.source
            
            # Add to collection
            template['collections'] = [collection_id]
            
            resp = self.zot.create_items([template])
            if resp and 'successful' in resp and resp['successful']:
                return resp['successful']['0']['key']
            else:
                # Need to handle duplicate check logic if needed, but for now simple add
                print(f"Failed to add item '{item.title}'. Response: {resp}")
                return None

        except Exception as e:
            print(f"Error in Zotero add_item: {e}")
            return None
