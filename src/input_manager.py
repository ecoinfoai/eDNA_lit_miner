import yaml
from dataclasses import dataclass
from typing import List, Dict, Optional
import os

@dataclass
class SpeciesQuery:
    species_name: str
    synonyms: List[str]
    keywords: List[str]
    date_range: Optional[str] = None

class InputManager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Input file not found: {filepath}")

    def load_species_list(self) -> List[SpeciesQuery]:
        with open(self.filepath, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing YAML file: {e}")

        if not data or 'species' not in data:
            raise ValueError("Invalid YAML format: 'species' list is missing")

        species_list = []
        for item in data['species']:
            if 'name' not in item:
                continue # Skip invalid entries
            
            species_list.append(SpeciesQuery(
                species_name=item['name'],
                synonyms=item.get('synonyms', []),
                keywords=item.get('keywords', []),
                date_range=item.get('date_range')
            ))
        
        return species_list
