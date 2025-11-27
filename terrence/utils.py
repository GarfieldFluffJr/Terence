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