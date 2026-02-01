#!/usr/bin/env python
"""Compile translation files using Babel"""
import os
from pathlib import Path
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

# Get the project root
base_dir = Path(__file__).resolve().parent

# Paths to locale directories
locale_dir = base_dir / 'locale'

# Compile .po files to .mo files for each language
for lang_dir in locale_dir.iterdir():
    if not lang_dir.is_dir() or lang_dir.name.startswith('.'):
        continue
    
    messages_dir = lang_dir / 'LC_MESSAGES'
    po_file = messages_dir / 'django.po'
    mo_file = messages_dir / 'django.mo'
    
    if po_file.exists():
        print(f"Compiling {po_file}...")
        with open(po_file, 'rb') as f:
            catalog = read_po(f, locale=lang_dir.name)
        
        with open(mo_file, 'wb') as f:
            write_mo(f, catalog)
        
        print(f"✓ Created {mo_file}")

print("\nAll translations compiled successfully!")
