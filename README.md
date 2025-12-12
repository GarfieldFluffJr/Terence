# Terrence (py) 🦅

# ![Terrence Picture](terrence.jpg)

Terrence is a Python package that makes it easy to scan and analyze GitHub repositories. It simplifies the GitHub API and processes the repo contents into a simple flat list that can be accessed by file path.


## Installation

### From PyPI

```bash
pip install terrence
```

## Quick Start

### 1. Get a GitHub Developer Token

Create a personal access token at: https://github.com/settings/tokens
- New token (classic)
- Only permission required: repo -> public_repo
- Additional permissions are optional

### 2. Basic Usage

```python
from terrence import Terrence

# Initialize a new Terrence instance
terrence = Terrence()

# Authenticate Terrence
terrence.auth("ghp_your_token_here")

# Scan a repository
terrence.scan_repository("https://github.com/pallets/flask")

# Access repo contents
print(f"Found {len(terrence.results)} files")
for file_path, content in terrence.results.items():
    print(f"{file_path}: {len(content)} characters")
```

## Usage Guide

### Authentication

You must authenticate Terrence with your GitHub API token before scanning any repository

```python
terrence = Terrence()
terrence.auth("ghp_your_token_here")
```

### Scanning Repositories

```python
# Scan entire repository
terrence.scan_repository("https://github.com/user/repo_name")
```

You also have the option to scan specific file types by providing the extension in a list argument

Extension can be prepended with "." but not required (py vs .py)
```python
# Scan only Python files
terrence.scan_repository("https://github.com/user/repo_name", ["py"])

# Scan multiple file types
terrence.scan_repository("https://github.com/user/repo_name", ["py", "js", "html"])
```

### Working with Branches

```python
# Scan a specific branch
terrence.branch("develop").scan_repository("https://github.com/pallets/flask")

# Scan a specific tag
terrence.branch("v2.0.0").scan_repository("https://github.com/pallets/flask")

# Scan a specific commit
terrence.branch("abc123def456").scan_repository("https://github.com/pallets/flask")

# Reset to default branch
terrence.clear_results()  # This also clears the branch
```

### Accessing Results

```python
terrence.scan_repository("https://github.com/pallets/click")

# Results is a dictionary: {file_path: file_content}
for file_path, content in terrence.results.items():
    print(f"\n{'='*60}")
    print(f"File: {file_path}")
    print(f"Lines: {len(content.splitlines())}")
    print(f"{'='*60}")
    print(content[:500])  # First 500 characters
```

### Repository Information

```python
terrence.scan_repository("https://github.com/pallets/click")

# Get repository metadata
repo_info = terrence.get_repo_info()
print(f"Owner: {repo_info['owner']}")
print(f"Repo: {repo_info['repo']}")
print(f"URL: {repo_info['url']}")

# Access last scanned URL directly
print(terrence.last_repo_url)
```

### Rate Limit Management

```python
# Check rate limit before scanning
rate = terrence.get_rate_limit()
print(f"Remaining: {rate['remaining']}/{rate['limit']}")
print(f"Resets at: {rate['reset']}")

# Terrence automatically checks rate limits during scanning
# and raises RateLimitException if running low
```

### Error Handling

```python
from terrence import Terrence, RateLimitException

terrence = Terrence().auth("ghp_your_token_here")

try:
    terrence.scan_repository("https://github.com/owner/repo")
    print(f"Success! Found {len(terrence.results)} files")

except RateLimitException as e:
    print(f"Rate limit reached: {e}")
    # Wait until reset time or use different token

except ValueError as e:
    print(f"Invalid input: {e}")
    # Check URL format or extension list

except Exception as e:
    print(f"Error: {e}")
    # Handle authentication, repo not found, etc.
```

### Clearing Data

```python
# Clear results but keep authentication and branch
terrence.clear_results()

# Clear everything (deauthenticate)
terrence.clear_all()
```

## API Reference

### `Terrence()`

Initialize a new Terrence instance.

```python
terrence = Terrence()
```

### `.auth(token: str) -> self`

Authenticate with a GitHub personal access token.

- **Parameters:**
  - `token` (str): GitHub personal access token
- **Returns:** self (for method chaining)

```python
terrence.auth("ghp_your_token_here")
```

### `.scan_repository(repo_url: str, extensions: list = None) -> None`

Scan a GitHub repository and store results.

- **Parameters:**
  - `repo_url` (str): GitHub repository URL
  - `extensions` (list, optional): List of file extensions to scan (e.g., `["py", "js"]`)
- **Raises:**
  - `Exception`: If not authenticated
  - `ValueError`: If URL is invalid or extensions are not allowed
  - `RateLimitException`: If rate limit is too low
  - `Exception`: If repository not found or other GitHub API errors

```python
terrence.scan_repository("https://github.com/pallets/flask")
terrence.scan_repository("https://github.com/pallets/flask", extensions=["py"])
```

### `.branch(branch_name: str) -> self`

Set the branch, tag, or commit to scan.

- **Parameters:**
  - `branch_name` (str): Branch name, tag, or commit SHA
- **Returns:** self (for method chaining)

```python
terrence.branch("develop")
terrence.branch("v1.0.0")
terrence.branch("abc123def")
```

### `.get_rate_limit() -> dict`

Get current GitHub API rate limit information.

- **Returns:** Dictionary with keys:
  - `remaining` (int): Requests remaining
  - `limit` (int): Total limit per hour
  - `reset` (datetime): When the limit resets

```python
rate = terrence.get_rate_limit()
print(f"Remaining: {rate['remaining']}/{rate['limit']}")
```

### `.get_repo_info() -> dict | None`

Get information about the last scanned repository.

- **Returns:** Dictionary with keys `owner`, `repo`, `url` or `None` if no repository scanned

```python
info = terrence.get_repo_info()
if info:
    print(f"{info['owner']}/{info['repo']}")
```

### `.clear_results() -> None`

Clear scan results and reset branch, but stay authenticated.

```python
terrence.clear_results()
```

### `.clear_all() -> None`

Clear everything including authentication.

```python
terrence.clear_all()
```

### Instance Variables

- **`results`** (dict): Dictionary mapping file paths to file contents
- **`last_repo_url`** (str | None): URL of last scanned repository
- **`token`** (str | None): GitHub authentication token

## File Filtering

### Allowed Extensions

By default, Terrence scans these file types:

- **Python:** `.py`
- **JavaScript/TypeScript:** `.js`, `.jsx`, `.ts`, `.tsx`
- **Web:** `.html`, `.htm`, `.css`, `.scss`, `.sass`, `.vue`, `.svelte`
- **Java:** `.java`
- **C/C++:** `.c`, `.cpp`, `.h`, `.hpp`, `.cc`
- **Other:** `.go`, `.rs`, `.rb`, `.php`, `.swift`, `.kt`, `.cs`

### Excluded Directories

The following directories are automatically excluded:

- `node_modules/`, `.git/`, `venv/`, `env/`, `.venv/`
- `__pycache__/`, `dist/`, `build/`
- `.next/`, `.nuxt/`, `target/`, `bin/`, `obj/`
- `test/`, `tests/`, `.pytest_cache/`, `coverage/`

## Error Types

### `RateLimitException`

Raised when GitHub API rate limit is too low (< 10 requests remaining).

```python
from terrence import RateLimitException

try:
    terrence.scan_repository(url)
except RateLimitException as e:
    print(f"Rate limit reached: {e}")
```

### `ValueError`

Raised when:
- Invalid GitHub URL format
- Extension not in allowed extensions list

### `Exception`

Raised for:
- Not authenticated
- Invalid GitHub token
- Repository not found (or private)
- Other GitHub API errors

## Examples

### Example 1: Compare Branches

```python
from terrence import Terrence

terrence = Terrence().auth("ghp_your_token_here")

# Scan main branch
terrence.branch("main").scan_repository("https://github.com/pallets/click")
main_files = set(terrence.results.keys())

# Scan develop branch
terrence.branch("develop").scan_repository("https://github.com/pallets/click")
develop_files = set(terrence.results.keys())

# Compare
new_files = develop_files - main_files
removed_files = main_files - develop_files

print(f"New files in develop: {len(new_files)}")
print(f"Removed from develop: {len(removed_files)}")
```

### Example 2: Analyze Code Distribution

```python
from terrence import Terrence
from collections import Counter

terrence = Terrence().auth("ghp_your_token_here")
terrence.scan_repository("https://github.com/pallets/flask")

# Count files by extension
extensions = Counter()
for file_path in terrence.results.keys():
    ext = file_path.split('.')[-1]
    extensions[ext] += 1

print("Code distribution:")
for ext, count in extensions.most_common():
    print(f"  .{ext}: {count} files")
```

### Example 3: Search for Patterns

```python
import re
from terrence import Terrence

terrence = Terrence().auth("ghp_your_token_here")
terrence.scan_repository("https://github.com/pallets/click")

# Find all TODO comments
pattern = re.compile(r'#\s*TODO:?\s*(.+)', re.IGNORECASE)

todos = []
for file_path, content in terrence.results.items():
    for line_num, line in enumerate(content.splitlines(), 1):
        match = pattern.search(line)
        if match:
            todos.append({
                'file': file_path,
                'line': line_num,
                'todo': match.group(1).strip()
            })

print(f"Found {len(todos)} TODOs:")
for todo in todos[:10]:  # Show first 10
    print(f"  {todo['file']}:{todo['line']} - {todo['todo']}")
```

## Development

### Setup

```bash
git clone https://github.com/yourusername/terrence.git
cd terrence
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest tests/test_client.py -v

# Run specific test
pytest tests/test_client.py::TestTerrence::test_auth -v

# Run with coverage
pytest tests/test_client.py --cov=terrence --cov-report=html
```

### Project Structure

```
terrence/
├── terrence/              # Main package
│   ├── __init__.py       # Package exports
│   ├── client.py         # Terrence class & RateLimitException
│   └── utils.py          # Helper functions
├── tests/                # Test suite
│   ├── test_client.py    # Pytest tests
│   └── test_*_manual.py  # Manual testing scripts
├── setup.py              # Package configuration
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Requirements

- Python 3.7+
- PyGithub >= 2.1.1
- python-dotenv >= 1.0.0

## Rate Limits

GitHub API rate limits:
- **Authenticated:** 5,000 requests per hour
- **Unauthenticated:** 60 requests per hour

Terrence automatically monitors your rate limit and will raise `RateLimitException` if you have fewer than 10 requests remaining.

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

- **Issues:** https://github.com/yourusername/terrence/issues
- **Documentation:** https://github.com/yourusername/terrence

## Author

Created by [Your Name]

## Changelog

### v0.1.0 (Initial Release)

- GitHub repository scanning
- Smart file filtering
- Branch/commit support
- Rate limit protection
- Extension filtering
- Repository metadata access
