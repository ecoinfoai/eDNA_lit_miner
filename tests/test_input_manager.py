import pytest
import os
import yaml
from src.input_manager import InputManager, SpeciesQuery

def test_init_file_not_found():
    with pytest.raises(FileNotFoundError):
        InputManager("non_existent_file.yaml")

def test_load_species_list_success(tmp_path):
    # Create a temporary yaml file
    yaml_content = """
species:
  - name: Gadus morhua
    synonyms:
      - Atlantic cod
    keywords:
      - eDNA
      - environmental DNA
    date_range: 2020:2024
  - name: Salmo salar
    # Defaults for optional fields
"""
    file_path = tmp_path / "species.yaml"
    file_path.write_text(yaml_content, encoding='utf-8')
    
    manager = InputManager(str(file_path))
    species_list = manager.load_species_list()
    
    assert len(species_list) == 2
    
    s1 = species_list[0]
    assert s1.species_name == "Gadus morhua"
    assert "Atlantic cod" in s1.synonyms
    assert "eDNA" in s1.keywords
    assert s1.date_range == "2020:2024"
    
    s2 = species_list[1]
    assert s2.species_name == "Salmo salar"
    assert s2.synonyms == []
    assert s2.keywords == []
    assert s2.date_range is None

def test_load_species_list_invalid_yaml(tmp_path):
    file_path = tmp_path / "invalid.yaml"
    file_path.write_text("species: [ unclosed list", encoding='utf-8')

    manager = InputManager(str(file_path))
    with pytest.raises(ValueError, match="Error parsing YAML file"):
        manager.load_species_list()

def test_load_species_list_missing_species_key(tmp_path):
    file_path = tmp_path / "empty.yaml"
    file_path.write_text("other_key: []", encoding='utf-8')
    
    manager = InputManager(str(file_path))
    with pytest.raises(ValueError, match="Invalid YAML format"):
        manager.load_species_list()

def test_load_species_list_skip_invalid_entries(tmp_path):
    yaml_content = """
species:
  - name: Valid Species
  - synonyms: ["Invalid because no name"]
  - name: Another Valid Species
"""
    file_path = tmp_path / "mixed.yaml"
    file_path.write_text(yaml_content, encoding='utf-8')

    manager = InputManager(str(file_path))
    species_list = manager.load_species_list()

    assert len(species_list) == 2
    assert species_list[0].species_name == "Valid Species"
    assert species_list[1].species_name == "Another Valid Species"
