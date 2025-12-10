import pytest
from unittest.mock import MagicMock, patch
from src.zotero_manager import ZoteroManager
from src.providers.base import SearchResult

@patch('src.zotero_manager.zotero.Zotero')
def test_create_or_get_collection_existing(mock_zotero):
    mock_instance = mock_zotero.return_value
    mock_instance.collections.return_value = [
        {'data': {'name': 'ExistingCollection'}, 'key': 'EXISTING_KEY'},
        {'data': {'name': 'OtherCollection'}, 'key': 'OTHER_KEY'}
    ]
    
    manager = ZoteroManager("123", "key")
    key = manager.create_or_get_collection("ExistingCollection")
    
    assert key == "EXISTING_KEY"
    mock_instance.create_collections.assert_not_called()

@patch('src.zotero_manager.zotero.Zotero')
def test_create_or_get_collection_new(mock_zotero):
    mock_instance = mock_zotero.return_value
    mock_instance.collections.return_value = []
    
    # Mock create response
    mock_instance.create_collections.return_value = {
        'successful': {'0': {'key': 'NEW_KEY'}}
    }
    
    manager = ZoteroManager("123", "key")
    key = manager.create_or_get_collection("NewCollection")
    
    assert key == "NEW_KEY"
    mock_instance.create_collections.assert_called_once()

@patch('src.zotero_manager.zotero.Zotero')
def test_add_item(mock_zotero):
    mock_instance = mock_zotero.return_value
    mock_instance.item_template.return_value = {} # Return empty dict as template
    
    mock_instance.create_items.return_value = {
        'successful': {'0': {'key': 'ITEM_KEY'}}
    }
    
    manager = ZoteroManager("123", "key")
    item = SearchResult(
        title="Test Title",
        authors=["Doe, John"],
        year="2023",
        doi="10.1000/1",
        source="PubMed"
    )
    
    item_key = manager.add_item(item, "COL_KEY")
    
    assert item_key == "ITEM_KEY"
    mock_instance.item_template.assert_called_with('journalArticle')
    mock_instance.create_items.assert_called_once()
    
    # Check if template was populated correctly (arguments passed to create_items)
    call_args = mock_instance.create_items.call_args[0][0] # List of items
    created_item = call_args[0]
    assert created_item['title'] == "Test Title"
    assert created_item['DOI'] == "10.1000/1"
    assert "COL_KEY" in created_item['collections']
