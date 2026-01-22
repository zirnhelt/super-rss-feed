#!/usr/bin/env python3
"""Fix smart quotes in Python files"""
import sys

def fix_quotes(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace smart quotes with regular quotes
    replacements = {
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark  
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '--', # Em dash
    }
    
    original = content
    for smart, regular in replacements.items():
        content = content.replace(smart, regular)
    
    if content != original:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed smart quotes in {filename}")
        return True
    else:
        print(f"ℹ️  No smart quotes found in {filename}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 fix_quotes.py <file>")
        sys.exit(1)
    
    fix_quotes(sys.argv[1])
