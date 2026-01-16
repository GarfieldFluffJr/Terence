from typing import List, Optional

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

def should_scan_file(file_path: str, extensions: Optional[List[str]] = None) -> bool:
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

  excluded_files = [
    '__init__.py',
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

  for excluded_file in excluded_files:
    if file_path.endswith(excluded_file):
      return False
  
  if extensions is not None:
    normalized_extensions = []
    # Go through loop of extensions, add . in front of them if not present
    for ext in extensions:
      if not ext.startswith('.'):
        ext = f'.{ext}'
      normalized_extensions.append(ext)
    
    # Ensure each extension is valid
    for ext in normalized_extensions:
      if ext not in allowed_extensions:
        raise ValueError(f"Extension '{ext}' is not in allowed extensions. ")
    
    # Return true for each file that ends with one of the provided extensions that are verified
    return file_path.endswith(tuple(normalized_extensions))

  return file_path.endswith(allowed_extensions)