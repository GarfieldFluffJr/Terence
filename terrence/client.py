from github import Github, Auth, GithubException, BadCredentialsException, UnknownObjectException
from terrence.utils import parse_github_url, should_scan_file

class Terrence:
  """
    Class that scans public repositories and stores results in each instance

    Usage:
      terrence = Terrence() <- Initialize the class
      terrence.auth("ghp_token") <- Authenticate with GitHub
      terrence.scan_repository("url") <- Scan a repository (must be public)
  """

  def __init__(self):
    self.token = None
    self._auth = None # private variable
    self.results = {}
    self.last_repo_url = None

  # Representation method so when user performs print(terrence), they see info rather than memory address
  def __repr__(self):
    auth_status = "authenticated" if self._auth else "not authenticated"
    if self.results:
        return f"Terrence({auth_status}, files={len(self.results)})"
    else:
        return f"Terrence({auth_status}, no scans yet)"

  def auth(self, token: str):
    self.token = token
    self._auth = Auth.Token(self.token)
    return self # Allows for chaining on initialization
  
  def scan_repository(self, repo_url: str, extensions: list = None):
    if not self._auth or not self.token:
      raise Exception("Not authenticated. Call Terrence.auth(token) first.")
    
    owner, repo_name = parse_github_url(repo_url)

    try:
      # Opens new Github instance, automatically closes at the end
      with Github(auth=self._auth) as g:
        repo = g.get_repo(f"{owner}/{repo_name}")
        self.results = self._get_files_recursive(repo, "", extensions) # Recursively traverse the repository tree
        # Returns a flat dictionary of every file specified by the user so not nested
        self.last_repo_url = repo_url
    except BadCredentialsException:
      raise Exception("Invalid GitHub token. Please check your token and try again.")
    except UnknownObjectException:
      raise Exception(f"Repository '{owner}/{repo_name}' not found. Check the URL or access permissions.")
    except GithubException as e:
      raise Exception(f"GitHub API error: {e.data.get('message', str(e))}")
  
  # Reset results but stay authenticated
  def clear_results(self):
    self.results = {}
    self.last_repo_url = None
  
  # Deauthenticate as well
  def clear_all(self):
    self.token = None
    self._auth = None
    self.results = {}
    self.last_repo_url = None
  
  # Recursively get all files into a flat dictionary 
  def _get_files_recursive(self, repo, path="", extensions=None):
    results = {}
    contents = repo.get_contents(path) # Get contents at the current path from GitHub
    
    # Take care of edge case where contents is one object file, so wrap it in a single-element list
    if not isinstance(contents, list):
      contents = [contents]
    
    for content in contents:
      # Check if type is directory or file
      if content.type == "dir":
        print(f"Found directory: {content.path}")
        subdir_results = self._get_files_recursive(repo, content.path, extensions)
        results.update(subdir_results) # Merge dictionaries together, in the format { path: content }
      elif content.type == "file":
        print(f"Found file: {content.path}")
        # Check if we should scan the file
        if should_scan_file(content.path, extensions):
          try:
            #  Decode the content of the file into readable string since GitHub encodes it as base64
            file_content = content.decoded_content.decode('utf-8')
            results[content.path] = file_content # Add entry to dictionary
          except (UnicodeDecodeError, Exception):
            # Anything that is an exception, just skip the file (images, PDFs, etc)
            pass
      
    return results
  
""" Possible edge cases
  - Invalid GitHub URL
  - Private repository access
  - Rate limiting from GitHub API
  - Large repositories causing timeouts
  - Token doesn't have necessary permissions
"""