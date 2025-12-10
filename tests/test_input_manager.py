import pytest
from src.input_manager import InputManager, SpeciesQuery
import yaml
import os

def test_load_species_list(tmp_path):
    # Create a dummy YAML file
    data = {
        'species': [
            {
                'name': 'Gadus morhua',
                'synonyms': ['Atlantic cod'],
                'keywords': ['eDNA', 'barcoding'],
                'date_range': '2020-2024'
            },
            {
                'name': 'Salmo salar',
                # Missing synonyms and keywords to test valid optional fields
            }
        ]
    }
    
    p = tmp_path / "species.yaml"
    with open(p, "w") as f:
        yaml.dump(data, f)
        
    manager = InputManager(str(p))
    species_list = manager.load_species_list()
    
    assert len(species_list) == 2
    
    # Check first item
    assert species_list[0].species_name == 'Gadus morhua'
    assert 'Atlantic cod' in species_list[0].synonyms
    assert 'eDNA' in species_list[0].keywords
    assert species_list[0].date_range == '2020-2024'
    
    # Check second item (defaults)
    assert species_list[1].species_name == 'Salmo salar'
    assert species_list[1].synonyms == []
    assert species_list[1].keywords == []
    assert species_list[1].date_range is None

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        InputManager("non_existent_file.yaml")

def test_invalid_yaml(tmp_path):
    p = tmp_path / "invalid.yaml"
    p.write_text("species: [ unclosed list", encoding="utf-8")
    
    manager = InputManager(str(p))
    with pytest.raises(ValueError, match="Error parsing YAML"):
        manager.load_species_list()
