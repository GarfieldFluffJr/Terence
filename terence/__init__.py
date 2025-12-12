"""
Terence - GitHub Repository Scanner

A Python package to scan and retrieve contents from public GitHub repositories.

Usage:
    from terence import Terence

    terence = Terence()
    terence.auth("ghp_your_token")
    terence.scan_repository("https://github.com/owner/repo")

    print(f"Found {len(terence.results)} files")
"""

from terence.client import Terence, RateLimitException
from terence.utils import parse_github_url, should_scan_file

__version__ = "1.0.0"
__all__ = ["Terence", "RateLimitException", "parse_github_url", "should_scan_file"]
