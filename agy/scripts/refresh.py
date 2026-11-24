#!/usr/bin/env python3
"""Refresh the "models" key of ../routing/gemini_rows.json from Artificial Analysis.

Usage: python3 -I agy/scripts/refresh.py [--dry-run] [--force]
agy subagents pick only a tier (flash or pro); these rows inform the main-session
choice (`agy --model ... --effort ...`) and the flash/pro split.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aa

TRACK = ('gemini-4-neon', 'gemini-4-carbon', 'gemini-4-argon', 'gemini-4-hydrogen', 'gemini-3-8-flash')
DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'routing', 'gemini_rows.json')

if __name__ == '__main__':
    aa.refresh(DB, TRACK, 'gemini-', sys.argv)
