from github import Github, Auth
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
    return f"Terrence(token='***{self.token[-4:]}', files={len(self.results)})"

  def auth(self, token: str):
    self.token = token
    self._auth = Auth.Token(self.token)
    return self # Allows for chaining on initialization
  
  def scan_repository(self, repo_url: str, extensions: list = None):
    if not self._auth or not self.token:
      raise Exception("Not authenticated. Call Terrence.auth(token) first.")
    
    owner, repo_name = parse_github_url(repo_url)

    # Opens new Github instance, automatically closes at the end
    with Github(auth=self._auth) as g:
      repo = g.get_repo(f"{owner}/{repo_name}")
      self.results = self._get_files_recursive(repo, "", extensions) # Recursively traverse the repository tree
      self.last_repo_url = repo_url
  
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
  