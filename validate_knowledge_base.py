#!/usr/bin/env python3
"""
Validation script for the NovaTech HR knowledge base.

Loads all knowledge JSON files, parses them, and validates each entry
against the KnowledgeEntry Pydantic model. Reports any errors and
provides a summary of entry counts per file.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from src.hrbot.knowledge.schema import KnowledgeEntry


def validate_file(file_path: Path) -> Dict[str, Any]:
    """
    Load and validate a single knowledge base JSON file.
    
    Returns:
        Dict with keys:
            - 'success': bool, True if all entries are valid
            - 'entry_count': int, number of entries in the file
            - 'errors': List[str], validation error messages
            - 'entries': List[KnowledgeEntry], valid entries
    """
    result = {
        'success': True,
        'entry_count': 0,
        'errors': [],
        'entries': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result['success'] = False
        result['errors'].append(f"JSON parsing error: {str(e)}")
        return result
    except FileNotFoundError:
        result['success'] = False
        result['errors'].append(f"File not found: {file_path}")
        return result
    
    if not isinstance(data, list):
        result['success'] = False
        result['errors'].append(f"Expected JSON array at top level, got {type(data).__name__}")
        return result
    
    result['entry_count'] = len(data)
    
    for idx, entry_data in enumerate(data):
        try:
            entry = KnowledgeEntry(**entry_data)
            result['entries'].append(entry)
        except Exception as e:
            result['success'] = False
            result['errors'].append(
                f"Entry {idx} (id: {entry_data.get('id', 'UNKNOWN')}): {str(e)}"
            )
    
    return result


def main():
    """Run validation on all knowledge base files."""
    knowledge_dir = Path(__file__).parent / 'knowledge'
    files = [
        'company.json',
        'onboarding.json',
        'leave.json',
        'attendance.json',
        'workplace.json',
        'contacts.json'
    ]
    
    print("=" * 80)
    print("NOVATECH HR KNOWLEDGE BASE VALIDATION")
    print("=" * 80)
    
    all_valid = True
    total_entries = 0
    results = {}
    
    for file_name in files:
        file_path = knowledge_dir / file_name
        result = validate_file(file_path)
        results[file_name] = result
        total_entries += result['entry_count']
        
        if result['success']:
            status = "✓ PASS"
        else:
            status = "✗ FAIL"
            all_valid = False
        
        print(f"\n{status} {file_name}")
        print(f"   Entries: {result['entry_count']}")
        
        if result['errors']:
            print(f"   Errors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"     - {error}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for file_name in files:
        result = results[file_name]
        print(f"{file_name:25} {result['entry_count']:3d} entries  {'✓ VALID' if result['success'] else '✗ INVALID'}")
    
    print("-" * 80)
    print(f"{'TOTAL':25} {total_entries:3d} entries")
    print("=" * 80)
    
    if all_valid:
        print("\n✓ All knowledge base entries are VALID and ready for retrieval!")
        return 0
    else:
        print("\n✗ Some entries failed validation. Please review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
