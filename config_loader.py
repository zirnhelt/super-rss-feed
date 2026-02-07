#!/usr/bin/env python3
"""
Configuration loader for Super RSS Feed Curator
Loads all configuration from config/ directory with validation
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

CONFIG_DIR = Path(__file__).parent / "config"

def load_system_config() -> Dict:
    """Load system configuration (URLs, cache settings)."""
    with open(CONFIG_DIR / "system.json", 'r') as f:
        return json.load(f)

def load_limits_config() -> Dict:
    """Load limits configuration (feed sizes, retention, scoring thresholds)."""
    with open(CONFIG_DIR / "limits.json", 'r') as f:
        return json.load(f)

def load_filters_config() -> Dict:
    """Load filters configuration (blocked sources and keywords)."""
    with open(CONFIG_DIR / "filters.json", 'r') as f:
        return json.load(f)

def load_categories_config() -> Dict:
    """Load categories configuration (category definitions and keywords)."""
    with open(CONFIG_DIR / "categories.json", 'r') as f:
        return json.load(f)

def load_feeds_config() -> Dict:
    """Load feeds configuration (feed metadata for output)."""
    with open(CONFIG_DIR / "feeds.json", 'r') as f:
        return json.load(f)

def load_source_preferences() -> Dict:
    """Load source preferences (source type classifications and per-type limits)."""
    with open(CONFIG_DIR / "source_preferences.json", 'r') as f:
        return json.load(f)

def load_scoring_interests() -> str:
    """Load Claude scoring interests as plain text."""
    with open(CONFIG_DIR / "scoring_interests.txt", 'r') as f:
        return f.read()

def get_category_keywords(category: str) -> List[str]:
    """Get keywords for a specific category."""
    categories = load_categories_config()
    return categories.get(category, {}).get('keywords', [])

def get_all_categories() -> List[str]:
    """Get list of all category keys."""
    categories = load_categories_config()
    return list(categories.keys())

def get_feed_title(category: str) -> str:
    """Get feed title for a category."""
    feeds = load_feeds_config()
    return feeds['feeds'].get(category, {}).get('title', category.title())

def get_feed_description(category: str) -> str:
    """Get feed description for a category."""
    feeds = load_feeds_config()
    return feeds['feeds'].get(category, {}).get('description', f'AI-curated {category} articles')

def get_blocked_sources() -> List[str]:
    """Get list of blocked sources."""
    filters = load_filters_config()
    return filters.get('blocked_sources', [])

def get_blocked_keywords() -> List[str]:
    """Get list of blocked keywords."""
    filters = load_filters_config()
    return filters.get('blocked_keywords', [])

def get_cache_file(cache_type: str) -> str:
    """Get cache filename for a specific type (scored_articles, wlt, shown_articles)."""
    system = load_system_config()
    return system['cache_files'].get(cache_type, f'{cache_type}_cache.json')

def get_source_type(source_name: str) -> Optional[str]:
    """Get the source type (print, broadcast, etc.) for a given source name."""
    prefs = load_source_preferences()
    return prefs.get('source_map', {}).get(source_name)

def get_source_type_config(source_type: str) -> Dict:
    """Get configuration for a source type (score_adjustment, max_per_source)."""
    prefs = load_source_preferences()
    return prefs.get('source_types', {}).get(source_type, {})

def get_all_config() -> Dict:
    """Load all configuration at once."""
    return {
        'system': load_system_config(),
        'limits': load_limits_config(),
        'filters': load_filters_config(),
        'categories': load_categories_config(),
        'feeds': load_feeds_config(),
        'scoring_interests': load_scoring_interests(),
        'source_preferences': load_source_preferences()
    }

def validate_config() -> Dict[str, List[str]]:
    """
    Validate all configuration files.
    Returns dict with any errors found, empty dict if all valid.
    """
    errors = {}
    
    try:
        system = load_system_config()
        
        # Check required keys
        required_system_keys = ['cache_files', 'cache_expiry', 'urls', 'lookback_hours']
        missing = [k for k in required_system_keys if k not in system]
        if missing:
            errors['system.json'] = [f"Missing required keys: {', '.join(missing)}"]
            
        # Check URLs are strings
        for url_key, url_value in system.get('urls', {}).items():
            if not isinstance(url_value, str):
                errors.setdefault('system.json', []).append(f"URL {url_key} must be string")
                
    except Exception as e:
        errors['system.json'] = [f"Failed to load: {str(e)}"]
    
    try:
        limits = load_limits_config()
        
        # Check all limits are positive integers
        for key, value in limits.items():
            if not isinstance(value, int) or value < 0:
                errors.setdefault('limits.json', []).append(f"{key} must be positive integer")
                
    except Exception as e:
        errors['limits.json'] = [f"Failed to load: {str(e)}"]
    
    try:
        filters = load_filters_config()
        
        # Check lists exist and contain strings
        for key in ['blocked_sources', 'blocked_keywords']:
            if key not in filters:
                errors.setdefault('filters.json', []).append(f"Missing {key}")
            elif not isinstance(filters[key], list):
                errors.setdefault('filters.json', []).append(f"{key} must be list")
            elif not all(isinstance(x, str) for x in filters[key]):
                errors.setdefault('filters.json', []).append(f"{key} must contain only strings")
                
    except Exception as e:
        errors['filters.json'] = [f"Failed to load: {str(e)}"]
    
    try:
        categories = load_categories_config()
        
        # Check each category has required fields
        for cat_name, cat_data in categories.items():
            required = ['name', 'description', 'emoji']
            missing = [k for k in required if k not in cat_data]
            if missing:
                errors.setdefault('categories.json', []).append(
                    f"Category {cat_name} missing: {', '.join(missing)}"
                )
            
            # Check keywords is a list
            if 'keywords' in cat_data and not isinstance(cat_data['keywords'], list):
                errors.setdefault('categories.json', []).append(
                    f"Category {cat_name} keywords must be list"
                )
                
    except Exception as e:
        errors['categories.json'] = [f"Failed to load: {str(e)}"]
    
    try:
        feeds = load_feeds_config()
        
        # Check feeds structure
        if 'feeds' not in feeds:
            errors['feeds.json'] = ["Missing 'feeds' key"]
        elif not isinstance(feeds['feeds'], dict):
            errors['feeds.json'] = ["'feeds' must be dict"]
            
    except Exception as e:
        errors['feeds.json'] = [f"Failed to load: {str(e)}"]
    
    try:
        interests = load_scoring_interests()

        # Check it's not empty
        if not interests.strip():
            errors['scoring_interests.txt'] = ["File is empty"]

    except Exception as e:
        errors['scoring_interests.txt'] = [f"Failed to load: {str(e)}"]

    try:
        prefs = load_source_preferences()

        # Check structure
        if 'source_types' not in prefs:
            errors.setdefault('source_preferences.json', []).append("Missing 'source_types' key")
        elif not isinstance(prefs['source_types'], dict):
            errors.setdefault('source_preferences.json', []).append("'source_types' must be dict")
        else:
            for type_name, type_config in prefs['source_types'].items():
                if 'score_adjustment' in type_config and not isinstance(type_config['score_adjustment'], (int, float)):
                    errors.setdefault('source_preferences.json', []).append(
                        f"source_types.{type_name}.score_adjustment must be a number"
                    )
                if 'max_per_source' in type_config and (not isinstance(type_config['max_per_source'], int) or type_config['max_per_source'] < 1):
                    errors.setdefault('source_preferences.json', []).append(
                        f"source_types.{type_name}.max_per_source must be a positive integer"
                    )

        if 'source_map' not in prefs:
            errors.setdefault('source_preferences.json', []).append("Missing 'source_map' key")
        elif not isinstance(prefs['source_map'], dict):
            errors.setdefault('source_preferences.json', []).append("'source_map' must be dict")
        else:
            valid_types = set(prefs.get('source_types', {}).keys())
            for source_name, source_type in prefs['source_map'].items():
                if source_type not in valid_types:
                    errors.setdefault('source_preferences.json', []).append(
                        f"Source '{source_name}' has unknown type '{source_type}'"
                    )

    except Exception as e:
        errors['source_preferences.json'] = [f"Failed to load: {str(e)}"]

    return errors

if __name__ == "__main__":
    # Test the config loader
    print("Testing configuration loader...")
    print("=" * 60)
    
    try:
        config = get_all_config()
        
        print(f"\n✅ System config loaded:")
        print(f"   Cache files: {len(config['system']['cache_files'])}")
        print(f"   Lookback hours: {config['system']['lookback_hours']}")
        
        print(f"\n✅ Limits config loaded:")
        print(f"   Max feed size: {config['limits']['max_feed_size']}")
        print(f"   Min Claude score: {config['limits']['min_claude_score']}")
        
        print(f"\n✅ Filters config loaded:")
        print(f"   Blocked sources: {len(config['filters']['blocked_sources'])}")
        print(f"   Blocked keywords: {len(config['filters']['blocked_keywords'])}")
        
        print(f"\n✅ Categories config loaded:")
        print(f"   Categories: {', '.join(config['categories'].keys())}")
        
        print(f"\n✅ Feeds config loaded:")
        print(f"   Feeds defined: {len(config['feeds']['feeds'])}")
        
        print(f"\n✅ Scoring interests loaded:")
        print(f"   Length: {len(config['scoring_interests'])} characters")
        
        print(f"\n🔍 Running validation...")
        errors = validate_config()
        
        if errors:
            print("\n❌ Validation errors found:")
            for file, error_list in errors.items():
                print(f"\n  {file}:")
                for error in error_list:
                    print(f"    - {error}")
        else:
            print("\n✅ All configuration files valid!")
        
        print("\n" + "=" * 60)
        print("Configuration loader test complete!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
