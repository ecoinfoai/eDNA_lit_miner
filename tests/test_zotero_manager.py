import pytest
from unittest.mock import MagicMock
from src.zotero_manager import ZoteroManager
from src.providers.base import SearchResult

@pytest.fixture
def mock_zotero(mocker):
    return mocker.patch("src.zotero_manager.zotero.Zotero")

def test_init(mock_zotero):
    manager = ZoteroManager("lib_id", "key", "user")
    mock_zotero.assert_called_with("lib_id", "user", "key")

def test_create_or_get_collection_existing(mock_zotero):
    zot_instance = mock_zotero.return_value
    zot_instance.collections.return_value = [
        {'data': {'name': 'Existing Collection'}, 'key': 'EXISTING_KEY'}
    ]
    
    manager = ZoteroManager("id", "key")
    key = manager.create_or_get_collection("Existing Collection")
    
    assert key == "EXISTING_KEY"
    zot_instance.create_collections.assert_not_called()

def test_create_or_get_collection_new_success(mock_zotero):
    zot_instance = mock_zotero.return_value
    zot_instance.collections.return_value = []
    zot_instance.create_collections.return_value = {
        'successful': {'0': {'key': 'NEW_KEY'}}
    }
    
    manager = ZoteroManager("id", "key")
    key = manager.create_or_get_collection("New Collection")
    
    assert key == "NEW_KEY"
    zot_instance.create_collections.assert_called_with([{'name': 'New Collection'}])

def test_create_or_get_collection_fail(mock_zotero):
    zot_instance = mock_zotero.return_value
    zot_instance.collections.return_value = []
    zot_instance.create_collections.return_value = {'successful': {}}

    manager = ZoteroManager("id", "key")
    
    with pytest.raises(Exception, match="Failed to create collection"):
        manager.create_or_get_collection("Fail Collection")

def test_create_or_get_collection_exception(mock_zotero):
    zot_instance = mock_zotero.return_value
    zot_instance.collections.side_effect = Exception("API Error")

    manager = ZoteroManager("id", "key")
    with pytest.raises(Exception, match="API Error"):
        manager.create_or_get_collection("Col")

def test_add_item_success(mock_zotero):
    zot_instance = mock_zotero.return_value
    zot_instance.item_template.return_value = {}
    zot_instance.create_items.return_value = {
        'successful': {'0': {'key': 'ITEM_KEY'}}
    }
    
    manager = ZoteroManager("id", "key")
    item = SearchResult(
        title="Title",
        authors=["Doe, John", "Smith, Jane", "SingleName"],
        year="2023",
        doi="10.1000/1",
        source="PubMed",
        abstract="Abstract",
        url="http://url"
    )
    
    key = manager.add_item(item, "COL_ID")
    
    assert key == "ITEM_KEY"
    
    # Check if template was populated correctly
    call_args = zot_instance.create_items.call_args
    created_item = call_args[0][0][0]

    assert created_item['title'] == "Title"
    assert created_item['date'] == "2023"
    assert created_item['DOI'] == "10.1000/1"
    assert created_item['collections'] == ["COL_ID"]
    assert len(created_item['creators']) == 3
    assert created_item['creators'][0] == {'creatorType': 'author', 'lastName': 'Doe', 'firstName': 'John'}
    assert created_item['creators'][2] == {'creatorType': 'author', 'name': 'SingleName'}

def test_add_item_fail_response(mock_zotero):
    zot_instance = mock_zotero.return_value
    zot_instance.item_template.return_value = {}
    zot_instance.create_items.return_value = {'successful': {}}

    manager = ZoteroManager("id", "key")
    item = SearchResult(title="Title", authors=[], year="", doi="", source="", abstract="", url="")

    key = manager.add_item(item, "COL_ID")
    assert key is None

def test_add_item_exception(mock_zotero):
    zot_instance = mock_zotero.return_value
    zot_instance.item_template.side_effect = Exception("Template Error")

    manager = ZoteroManager("id", "key")
    item = SearchResult(title="Title", authors=[], year="", doi="", source="", abstract="", url="")

    key = manager.add_item(item, "COL_ID")
    assert key is None
