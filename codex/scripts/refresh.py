#!/usr/bin/env python3
"""Refresh the "models" key of ../routing/gpt_rows.json from Artificial Analysis.

Usage: python3 -I codex/scripts/refresh.py [--dry-run] [--force]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aa

TRACK = ('gpt-6-2-sol', 'gpt-6-2-astra', 'gpt-6-1-terra', 'gpt-6-1-sol', 'gpt-6-astra', 'gpt-6-sol', 'gpt-6-luna')
DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'routing', 'gpt_rows.json')

if __name__ == '__main__':
    aa.refresh(DB, TRACK, 'gpt-', sys.argv)
