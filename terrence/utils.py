# Takes in the github url and parses it into owner and repo name / path
def parse_github_url(url: str):
  # Returns original string if prefix isn't found
  url = url.replace("https://", "").replace("http://", "")
  url = url.replace("github.com/", "")

  if url.endswith(".git"):
    url = url[:-4]
  
  url = url.rstrip("/") # Remove trailing slash if present

  parts = url.split("/")

  # Will only return the owner and repo, even if the url is in a subdirectory
  if len(parts) >= 2:
    owner = parts[0]
    repo = parts[1]
    return (owner, repo)
  else:
    raise ValueError(f"Invalid GitHub URL: {url}")

def should_scan_file(file_path: str) -> bool:
  excluded_dirs = [
    'node_modules/',
    '.git/',
    'venv/', 'env/', '.venv/',
    '__pycache__/',
    'dist/', 'build/',
    '.next/', '.nuxt/',
    'target/',
    'bin/', 'obj/',
    'test/', 'tests/',
    '.pytest_cache/',
    'coverage/', 
  ]

  # Put in a tuple since endsWith accepts a tuple and checks for any of the items
  allowed_extensions = (
    # Python
    '.py',
    # JavaScript/TypeScript
    '.js', '.jsx', '.ts', '.tsx',
    # Web
    '.html', '.htm', '.css', '.scss', '.sass',
    '.vue', '.svelte',
    # Java
    '.java',
    # C/C++
    '.c', '.cpp', '.h', '.hpp', '.cc',
    # Other languages
    '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.cs',
  )

  for excluded_dir in excluded_dirs:
    if excluded_dir in file_path:
      return False
  
  if file_path.endswith(allowed_extensions):
    return True

  return False

# Python special variable __name__, so it will only run if utils.py is executed since this is the main file, but if utils is imported into another function, then utils is called utils, not main
if __name__ == "__main__":
  test_urls = [
    "https://github.com/pytorch/pytorch",
    "github.com/torvalds/linux",
    "https://github.com/microsoft/vscode.git",
    "microsoft/typescript/main/tree.git",
    "https://github.com/python/cpython/",
  ]
  print("\n" + "="*60)
  print("Testing URL parser:")
  print("="*60)
  for url in test_urls:
    try:
      result = parse_github_url(url)
      print(f"{url:50s} -> {result}")
    except ValueError as e:
      print(f"{e}")
  
  # File filtering tests
  print("\n" + "="*60)
  print("Testing file filter:")
  print("="*60)

  test_files = [
      ("src/main.py", True),
      ("app.js", True),
      ("components/Header.tsx", True),
      ("styles/main.css", True),
      ("server.go", True),
      ("node_modules/react/index.js", False),
      (".git/config", False),
      ("venv/lib/python3.9/site.py", False),
      ("package.json", False),
      ("README.md", False),
      ("image.png", False),
      ("dist/bundle.js", False),
      ("__pycache__/utils.pyc", False),
  ]

  for file_path, expected in test_files:
      result = should_scan_file(file_path)
      status = "✓" if result == expected else "✗"
      print(f"{status} {file_path:40s} -> {str(result):5s} (expected: {expected})")