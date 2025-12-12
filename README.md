# Terrence &nbsp;🦅

# ![Terrence Picture](terrence.jpg)

Terrence is a Python package that makes it easy to scan and analyze GitHub repositories. It simplifies the GitHub API and processes the repo contents into a simple flat dictionary that can be accessed by file path.


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
You can scan the contents of a specific branch rather than the default main/master branch

```python
# Scan a specific branch name
terrence.branch("develop")
terrence.scan_repository("https://github.com/user/repo_name")

# Scan a specific tag
terrence.branch("v2.0.0")
terrence.scan_repository("https://github.com/user/repo_name")

# Scan a specific commit (can chain methods)
terrence.branch("abc123def456").scan_repository("https://github.com/user/repo_name")
```
To reset to the default branch, simply clear the results and scan again
```python
# Reset to default branch
terrence.clear_results() 
terrence.scan_repository("https://github.com/user/repo_name")
```

### Accessing Results

Once a scan is performed, the repository's file contents are stored in a flat dictionary in `terrence.results`.

```python
results = terrence.results

# List all files:
for path in results.keys():
    print(f" - {path}")

# Print the first 200 characters of a specific file
if "frontend/app/page.tsx" in results:
    print(results["frontend/app/page.tsx"][:200])

# Search content across files
for file_path, content in results.items():
    if "def main" in content:
        print(f"Found 'def main' in: {file_path})
```

### Sample Results Output

Results is a flat dictionary with each key being the path to the file including the file name and the value is the raw contents of the file

```python
terrence.results = {
    'frontend/app/index.html': '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n</head></html>...',
    'frontend/app/styles/globals.css': 'body {\n  font-family: Arial, sans-serif;\n...}\nh1 {\n  color: #333;\n}'
}
```

### Repository Information

```python
terrence.scan_repository("https://github.com/user/repo_name")

repo_info = terrence.get_repo_info()

repo_info = {
    'owner': 'user',
    'repo': 'repo_name',
    'url': 'https://github.com/user/repo_name'
}
```

### Rate Limit Management

GitHub API allows for 5000 requests per hour per authenticated API token or 60 for unauthenticated.

Terrence automatically flags a `RateLimitError` if rate limit is too low to make a new repository scan request.

```python
rate = terrence.get_rate_limit()

rate = {
    'remaining': 4102,
    'limit': 5000, # GitHub limit
    # Date format yyyy-mm-dd hr:min:sec+00:00 timezone
    'reset': datetime.datetime(2025, 12, 4, 18, 30, 0, tzinfo=datetime.timezone.utc)
}
```

### Clearing Data

```python
# Clear results but stay authenticated
terrence.clear_results()

# Clear everything (deauthenticate)
terrence.clear_all()
```

### Sample Error Handling

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

## Requirements

- Python 3.7+
- PyGithub >= 2.1.1
- python-dotenv >= 1.0.0

## License

MIT License - see LICENSE file for details

## Contributions & Support

Contributions are welcome! Feel free to fork and submit a pull request.

For any questions or concerns, please reach out to me at [louieyin6@gmail.com](mailto:louieyin6@gmail.com)

## Author

Created by Louie Yin (GarfieldFluffJr)
