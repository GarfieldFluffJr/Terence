# Takes in the github url and parses it into owner and repo name / path
def parse_github_url(url: str):
  # Returns original string if prefix isn't found
  url = url.replace("https://", "").replace("http://", "")
  url = url.replace("github.com/", "")

  if url.endswith(".git"):
    url = url[:-4]
  
  url = url.rstrip("/") # Remove trailing slash if present

  parts = url.split("/")

  if len(parts) >= 2:
    owner = parts[0]
    repo = parts[1]
    return (owner, repo)
  else:
    raise ValueError(f"Invalid GitHub URL: {url}")

# Python special variable __name__, so it will only run if utils.py is executed since this is the main file, but if utils is imported into another function, then utils is called utils, not main
if __name__ == "__main__":
  test_urls = [
    "https://github.com/pytorch/pytorch",
    "github.com/torvalds/linux",
    "https://github.com/microsoft/vscode.git",
    "microsoft/typescript/main/tree.git",
    "https://github.com/python/cpython/",
  ]
  print("Testing URL parser:")
  for url in test_urls:
    try:
      result = parse_github_url(url)
      print(f"{url:50s} -> {result}")
    except ValueError as e:
      print(f"{e}")