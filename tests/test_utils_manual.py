from terrence.utils import *

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