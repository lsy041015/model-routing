#!/usr/bin/env python3
"""Refresh the "models" key of ../routing/routing.json from Artificial Analysis.

Usage: python3 -I claude/scripts/refresh.py [--dry-run] [--force]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aa

TRACK = ('claude-sonnet-5-5', 'claude-opus-5-5', 'claude-haiku-5-5', 'claude-fable-5-2')
DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'routing', 'routing.json')

if __name__ == '__main__':
    aa.refresh(DB, TRACK, 'claude-', sys.argv)
