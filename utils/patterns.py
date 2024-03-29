"""
Patterns docstring.

This module defines regular expression patterns for extracting score info.
"""

import re

connections_pattern = re.compile(r"Connections.*\nPuzzle #[0-9]+")
mini_pattern = re.compile(r"badges\/games\/mini.+t=([0-9]+)")
# Mini scores are sent differently if using the app
mini_pattern_app = re.compile(r"I solved the .* New York Times Mini Crossword in (.+)!")
wordle_pattern = re.compile(r"Wordle.+(.)/[0-9]")
