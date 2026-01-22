#!/usr/bin/env python3
"""
Feed Integration Helper - Add discovered feeds to your OPML
Usage: python integrate_discoveries.py [--auto-add-threshold 80]
"""
import json
import sys
import argparse
from typing import List, Dict
import xml.etree.ElementTree as ET
from datetime import datetime

def load_discovery_report() -> Dict:
    """Load the latest discovery report"""
    try:
        with open('feed_discovery_report.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No discovery report found. Run feed_discovery.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading discovery report: {e}")
        sys.exit(1)

def load_opml(path: str = 'feeds.opml') -> ET.ElementTree:
    """Load existing OPML file"""
    try:
        return ET.parse(path)
    except Exception as e:
        print(f"❌ Error loading OPML file: {e}")
        sys.exit(1)

def get_existing_feeds(tree: ET.ElementTree) -> set:
    """Get set of existing feed URLs from OPML"""
    existing = set()
    for outline in tree.findall(".//outline[@type='rss']"):
        url = outline.get('xmlUrl')
        if url:
            existing.add(url.strip())
    return existing

def add_feeds_to_opml(tree: ET.ElementTree, feeds_to_add: List[Dict], category_name: str = "Discovered Feeds") -> int:
    """Add new feeds to OPML under a category"""
    if not feeds_to_add:
        return 0
    
    root = tree.getroot()
    body = root.find('body')
    if body is None:
        body = ET.SubElement(root, 'body')
    
    # Find or create category folder
    category_folder = None
    for outline in body.findall('outline'):
        if outline.get('text') == category_name:
            category_folder = outline
            break
    
    if category_folder is None:
        category_folder = ET.SubElement(body, 'outline', 
                                      text=category_name, 
                                      title=category_name)
    
    # Add feeds to category
    added_count = 0
    for feed in feeds_to_add:
        # Create feed entry
        ET.SubElement(category_folder, 'outline',
                     type='rss',
                     text=feed['title'],
                     title=feed['title'],
                     xmlUrl=feed['url'],
                     htmlUrl=feed.get('html_url', ''))
        added_count += 1
    
    return added_count

def interactive_selection(report: Dict) -> List[Dict]:
    """Interactively select feeds to add"""
    selected_feeds = []
    
    print("\n🔍 INTERACTIVE FEED SELECTION")
    print("=" * 50)
    
    # Go through each category
    for category, data in report['categories'].items():
        if not data['feeds']:
            continue
            
        print(f"\n📂 {category.upper()} ({data['count']} feeds)")
        print("-" * 30)
        
        for i, feed in enumerate(data['feeds']):
            print(f"\n{i+1}. {feed['title']}")
            print(f"   Score: {feed['average_score']} | Articles: {feed['sample_articles']}")
            print(f"   URL: {feed['url']}")
            print(f"   Reason: {feed['reason']}")
            
            while True:
                choice = input("   Add this feed? (y/n/s=skip category): ").strip().lower()
                if choice in ['y', 'yes']:
                    selected_feeds.append(feed)
                    print("   ✅ Added to selection")
                    break
                elif choice in ['n', 'no']:
                    print("   ❌ Skipped")
                    break
                elif choice in ['s', 'skip']:
                    print(f"   ⏭️  Skipping rest of {category} category")
                    return selected_feeds
                else:
                    print("   Please enter 'y' for yes, 'n' for no, or 's' to skip category")
    
    return selected_feeds

def main():
    parser = argparse.ArgumentParser(description='Integrate discovered feeds into OPML')
    parser.add_argument('--auto-add-threshold', type=float, default=None,
                       help='Automatically add feeds above this score threshold')
    parser.add_argument('--opml-path', default='feeds.opml',
                       help='Path to OPML file (default: feeds.opml)')
    parser.add_argument('--category-name', default='Discovered Feeds',
                       help='Category name for new feeds (default: Discovered Feeds)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be added without making changes')
    
    args = parser.parse_args()
    
    # Load discovery report
    report = load_discovery_report()
    
    # Load existing OPML
    opml_tree = load_opml(args.opml_path)
    existing_feeds = get_existing_feeds(opml_tree)
    
    print(f"📚 Loaded {len(existing_feeds)} existing feeds from {args.opml_path}")
    print(f"🎯 Discovery report has {report['recommended_feeds']} recommendations")
    
    # Collect feeds to add
    feeds_to_add = []
    
    if args.auto_add_threshold:
        # Automatic mode
        print(f"\n🤖 AUTO-ADD MODE (threshold: {args.auto_add_threshold})")
        for category, data in report['categories'].items():
            for feed in data['feeds']:
                if (feed['average_score'] >= args.auto_add_threshold and 
                    feed['url'] not in existing_feeds):
                    feeds_to_add.append(feed)
                    print(f"  ✅ Auto-selected: {feed['title']} (score: {feed['average_score']})")
    else:
        # Interactive mode
        if report['recommended_feeds'] == 0:
            print("❌ No feeds recommended (all below threshold)")
            return
        
        # Filter out feeds already in OPML
        for category, data in report['categories'].items():
            data['feeds'] = [f for f in data['feeds'] if f['url'] not in existing_feeds]
        
        feeds_to_add = interactive_selection(report)
    
    if not feeds_to_add:
        print("\n❌ No feeds selected for addition")
        return
    
    print(f"\n📝 Selected {len(feeds_to_add)} feeds to add:")
    for feed in feeds_to_add:
        print(f"  • {feed['title']} (score: {feed['average_score']})")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No changes made")
        return
    
    # Add feeds to OPML
    added_count = add_feeds_to_opml(opml_tree, feeds_to_add, args.category_name)
    
    # Update OPML metadata
    head = opml_tree.getroot().find('head')
    if head is not None:
        date_modified = head.find('dateModified')
        if date_modified is None:
            date_modified = ET.SubElement(head, 'dateModified')
        date_modified.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Save updated OPML
    opml_tree.write(args.opml_path, encoding='utf-8', xml_declaration=True)
    
    print(f"\n✅ Successfully added {added_count} feeds to {args.opml_path}")
    print(f"📂 Added under category: '{args.category_name}'")
    print(f"\n🚀 Next steps:")
    print(f"1. Review the new feeds in your OPML")
    print(f"2. Run your main curation script to test")
    print(f"3. Adjust categories or remove feeds as needed")

if __name__ == "__main__":
    main()
