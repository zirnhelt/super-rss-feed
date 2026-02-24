#!/usr/bin/env python3
"""
Quick test script to verify RSS curator setup
"""

import os
import sys

def check_file(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import feedparser
        import feedgen
        import fuzzywuzzy
        import anthropic
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def check_api_key():
    """Check if API key is set"""
    if os.getenv('ANTHROPIC_API_KEY'):
        print("✅ ANTHROPIC_API_KEY is set")
        return True
    else:
        print("❌ ANTHROPIC_API_KEY not set")
        print("   Run: export ANTHROPIC_API_KEY='your-key-here'")
        return False

def main():
    print("🔍 Super RSS Curator - Setup Check\n")
    
    all_good = True
    
    # Check files
    all_good &= check_file('super_rss_curator_json.py', 'Main script')
    all_good &= check_file('requirements.txt', 'Dependencies file')
    all_good &= check_file('feeds.opml', 'OPML feed list')
    all_good &= check_file('.github/workflows/generate-feed.yml', 'GitHub Actions workflow')
    all_good &= check_file('index.html', 'Landing page')
    all_good &= check_file('README.md', 'README')
    
    print()
    
    # Check dependencies
    all_good &= check_dependencies()
    
    print()
    
    # Check API key
    all_good &= check_api_key()
    
    print("\n" + "="*50)
    
    if all_good:
        print("✅ All checks passed! You're ready to run:")
        print("   python super_rss_curator_json.py feeds.opml")
    else:
        print("❌ Some checks failed. Fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
