import argparse
import sys
from typing import List

from src.config import Config
from src.input_manager import InputManager, SpeciesQuery
from src.providers.pubmed import PubMedProvider
from src.providers.semantic_scholar import SemanticScholarProvider
from src.zotero_manager import ZoteroManager
from src.providers.base import SearchResult
from src.abstract_cache import AbstractCache

def main():
    parser = argparse.ArgumentParser(description="eDNA Literature Miner")
    parser.add_argument("species_list", help="Path to YAML file containing species list")
    parser.add_argument("--dry-run", action="store_true", help="Perform search but do not save to Zotero")
    parser.add_argument("--limit", type=int, default=10, help="Number of results per provider per species")
    
    args = parser.parse_args()

    # 1. Load Config
    try:
        config = Config()
        if not args.dry_run:
            config.validate()
        print("Configuration loaded.")
    except Exception as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)

    # 2. Load Species List
    try:
        input_manager = InputManager(args.species_list)
        species_list = input_manager.load_species_list()
        print(f"Loaded {len(species_list)} species from {args.species_list}")
    except Exception as e:
        print(f"Input Error: {e}")
        sys.exit(1)

    # 3. Initialize Providers
    providers = []
    
    # PubMed
    if config.EMAIL:
        try:
            providers.append(PubMedProvider(email=config.EMAIL))
            print("PubMed Provider initialized.")
        except Exception as e:
             print(f"Failed to init PubMed Provider: {e}")
    elif args.dry_run:
        print("Dry Run: Using dummy email for PubMed.")
        providers.append(PubMedProvider(email="dryrun@example.com"))
    else:
         print("Warning: EMAIL env var not set, skipping PubMed.")

    # Semantic Scholar
    # API Key is optional but good to have
    try:
        providers.append(SemanticScholarProvider(api_key=config.SEMANTIC_SCHOLAR_API_KEY))
        print("Semantic Scholar Provider initialized.")
    except Exception as e:
        print(f"Failed to init Semantic Scholar Provider: {e}")

    if not providers:
        print("No search providers available. Exiting.")
        sys.exit(1)

    # 4. Initialize Zotero (if not dry run)
    zotero_manager = None
    if not args.dry_run:
        try:
            zotero_manager = ZoteroManager(
                library_id=config.ZOTERO_LIBRARY_ID,
                api_key=config.ZOTERO_API_KEY,
                library_type=config.ZOTERO_LIBRARY_TYPE
            )
            print("Zotero Manager initialized.")
        except Exception as e:
             print(f"Zotero Init Error: {e}")
             sys.exit(1)

    # 5. Initialize Abstract Cache
    abstract_cache = AbstractCache()
    print("Abstract Cache initialized.")

    # 6. Process Each Species
    for species in species_list:
        print(f"\nProcessing species: {species.species_name}")
        
        # Build Query
        # Simple strategy: Name OR Synonyms + Keywords
        # e.g. ("Gadus morhua" OR "Atlantic cod") AND ("eDNA" OR "environmental DNA")
        
        query_terms = [f'"{species.species_name}"'] + [f'"{syn}"' for syn in species.synonyms]
        if len(query_terms) > 1:
            name_part = "(" + " OR ".join(query_terms) + ")"
        else:
            name_part = query_terms[0]
            
        keyword_part = ""
        if species.keywords:
            kw_terms = [f'"{kw}"' for kw in species.keywords]
            if len(kw_terms) > 1:
                keyword_part = " AND (" + " OR ".join(kw_terms) + ")"
            else:
                keyword_part = f" AND {kw_terms[0]}"
        
        full_query = name_part + keyword_part
        print(f"  Query: {full_query}")
        
        all_results: List[SearchResult] = []
        
        for provider in providers:
            print(f"  Searching {provider.__class__.__name__}...")
            results = provider.search(full_query, limit=args.limit)
            print(f"    Found {len(results)} results.")
            all_results.extend(results)
            
        # Deduplication (by Title or DOI)
        unique_results = {}
        for res in all_results:
            key = res.doi if res.doi else res.title.lower().strip()
            if key not in unique_results:
                unique_results[key] = res
        
        deduplicated = list(unique_results.values())
        print(f"  Total unique results: {len(deduplicated)}")
        
        if args.dry_run:
            print("  Dry Run: Skipping Zotero upload and cache.")
            for res in deduplicated[:3]: # Print first 3
                 print(f"    - [{res.source}] {res.title} ({res.year})")
        else:
            if zotero_manager:
                collection_name = f"eDNA - {species.species_name}"
                try:
                    col_id = zotero_manager.create_or_get_collection(collection_name)
                    print(f"  Target Collection ID: {col_id}")

                    zotero_keys = []
                    count = 0
                    for item in deduplicated:
                        # Simple check might be needed here to avoid duplicates in Zotero if code runs twice
                        # But requires searching Zotero first. For MVP, we just add.
                        new_key = zotero_manager.add_item(item, col_id)
                        if new_key:
                            zotero_keys.append(new_key)
                            count += 1
                    print(f"  Added {count} items to Zotero.")

                    # Save to abstract cache
                    if zotero_keys:
                        papers_to_cache = [item for item, key in zip(deduplicated, zotero_keys) if key]
                        abstract_cache.add_papers(
                            species_name=species.species_name,
                            papers=papers_to_cache,
                            zotero_keys=zotero_keys,
                            keywords=species.keywords
                        )
                        print(f"  Cached {len(zotero_keys)} papers to abstracts_cache.yaml")

                except Exception as e:
                    print(f"  Error processing Zotero for {species.species_name}: {e}")

    print("\nProcessing Complete.")

if __name__ == "__main__":
    main()
