"""
Terrence - GitHub Repository Scanner

A Python package to scan and retrieve contents from public GitHub repositories.

Usage:
    from terrence import Terrence

    terrence = Terrence()
    terrence.auth("ghp_your_token")
    terrence.scan_repository("https://github.com/owner/repo")

    print(f"Found {len(terrence.results)} files")
"""

from terrence.client import Terrence, RateLimitException
from terrence.utils import parse_github_url, should_scan_file

__version__ = "0.1.0"
__all__ = ["Terrence", "RateLimitException", "parse_github_url", "should_scan_file"]
