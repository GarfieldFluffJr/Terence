"""Manual tests for utils module - run with: python tests/test_utils_manual.py"""
from terrence.utils import parse_github_url, should_scan_file


if __name__ == "__main__":
  print("="*70)
  print("Testing parse_github_url:")
  print("="*70)

  url_test_cases = [
    ("https://github.com/pytorch/pytorch", ("pytorch", "pytorch")),
    ("github.com/torvalds/linux", ("torvalds", "linux")),
    ("https://github.com/microsoft/vscode.git", ("microsoft", "vscode")),
    ("microsoft/typescript", ("microsoft", "typescript")),
    ("https://github.com/python/cpython/", ("python", "cpython")),
    ("https://github.com/pytorch/pytorch/blob/main/README.md", ("pytorch", "pytorch")),
  ]

  for url, expected in url_test_cases:
    try:
      result = parse_github_url(url)
      status = "✓" if result == expected else "✗"
      print(f"{status} {url:60s} -> {result}")
    except ValueError as e:
      print(f"✗ {url:60s} -> Error: {e}")

  print("\n" + "="*70)
  print("Testing should_scan_file (no extension filter):")
  print("="*70)

  basic_test_cases = [
    ("src/main.py", None, True, "Python file"),
    ("app.js", None, True, "JavaScript file"),
    ("components/Header.tsx", None, True, "TypeScript file"),
    ("styles/main.css", None, True, "CSS file"),
    ("server.go", None, True, "Go file"),
    ("lib.rs", None, True, "Rust file"),
    ("node_modules/react/index.js", None, False, "Excluded: node_modules"),
    (".git/config", None, False, "Excluded: .git"),
    ("venv/lib/python3.9/site.py", None, False, "Excluded: venv"),
    ("package.json", None, False, "Not allowed: .json"),
    ("README.md", None, False, "Not allowed: .md"),
    ("image.png", None, False, "Not allowed: .png"),
    ("dist/bundle.js", None, False, "Excluded: dist"),
    ("__pycache__/utils.pyc", None, False, "Excluded: __pycache__"),
  ]

  for file_path, exts, expected, description in basic_test_cases:
    result = should_scan_file(file_path, extensions=exts)
    status = "✓" if result == expected else "✗"
    print(f"{status} {file_path:40s} -> {str(result):5s} | {description}")

  print("\n" + "="*70)
  print("Testing should_scan_file (with extension filters):")
  print("="*70)

  extension_test_cases = [
    ("src/main.py", ["py"], True, "Python file, py filter"),
    ("src/main.py", ["js"], False, "Python file, js filter"),
    ("app.js", ["js"], True, "JavaScript file, js filter"),
    ("app.js", ["py", "js"], True, "JavaScript file, multiple filters"),
    ("app.ts", ["js", "ts", "tsx"], True, "TypeScript file, TS filters"),
    ("component.tsx", ["tsx"], True, "TSX file, tsx filter"),
    ("style.css", ["css", "scss"], True, "CSS file, CSS filters"),
    ("style.scss", ["css"], False, "SCSS file, CSS filter only"),
    ("index.html", ["html", "css"], True, "HTML file, web filters"),
    ("main.go", ["go"], True, "Go file, go filter"),
    ("lib.rs", ["rs"], True, "Rust file, rs filter"),
    ("node_modules/react/index.js", ["js"], False, "Excluded dir, even with filter"),
    ("venv/lib/python.py", ["py"], False, "Venv dir, excluded"),
    ("dist/bundle.js", ["js"], False, "Dist dir, excluded"),
  ]

  for file_path, exts, expected, description in extension_test_cases:
    try:
      result = should_scan_file(file_path, extensions=exts)
      status = "✓" if result == expected else "✗"
      ext_str = str(exts) if exts else "all"
      print(f"{status} {file_path:35s} ext={ext_str:20s} -> {str(result):5s} | {description}")
    except ValueError as e:
      print(f"✗ {file_path:35s} ext={str(exts):20s} -> Error: {e}")

  print("\n" + "="*70)
  print("Testing extension normalization (with/without dot):")
  print("="*70)

  normalization_tests = [
    ("main.py", ["py"], True, "Extension without dot"),
    ("main.py", [".py"], True, "Extension with dot"),
    ("app.js", ["py", ".js"], True, "Mixed dot notation"),
  ]

  for file_path, exts, expected, description in normalization_tests:
    result = should_scan_file(file_path, extensions=exts)
    status = "✓" if result == expected else "✗"
    print(f"{status} {file_path:35s} ext={str(exts):20s} -> {str(result):5s} | {description}")

  print("\n" + "="*70)
  print("Testing invalid extensions (should raise errors):")
  print("="*70)

  invalid_test_cases = [
    ("file.txt", ["txt"], "txt not in allowed extensions"),
    ("file.pdf", ["pdf"], "pdf not in allowed extensions"),
    ("file.py", ["py", "invalid"], "invalid extension in list"),
    ("data.json", ["json"], "json not in allowed extensions"),
  ]

  for file_path, exts, description in invalid_test_cases:
    try:
      result = should_scan_file(file_path, extensions=exts)
      print(f"✗ {file_path:35s} ext={str(exts):20s} -> Should have raised error | {description}")
    except ValueError as e:
      print(f"✓ {file_path:35s} ext={str(exts):20s} -> Raised ValueError | {description}")

  print("\n" + "="*70)
  print("All manual tests completed!")
  print("="*70)