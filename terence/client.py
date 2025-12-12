from github import Github, Auth, GithubException, BadCredentialsException, UnknownObjectException
from terence.utils import parse_github_url, should_scan_file

# Custom exception for rate limiting
class RateLimitException(Exception):
  """Raised when GitHub API rate limit is reached"""
  pass

class Terence:

  def __init__(self):
    self.token = None
    self._auth = None # private variable
    self.results = {}
    self.last_repo_url = None
    self._branch = None  # Private variable for branch/commit

  # Representation method so when user performs print(terence), they see info rather than memory address
  def __repr__(self):
    auth_status = "authenticated" if self._auth else "not authenticated"
    branch_info = f", branch={self._branch}" if self._branch else ""
    if self.results:
        return f"Terence({auth_status}{branch_info}, files={len(self.results)})"
    else:
        return f"Terence({auth_status}{branch_info}, no scans yet)"

  def auth(self, token: str):
    self.token = token
    self._auth = Auth.Token(self.token)
    return self # Allows for chaining on initialization
  
  def scan_repository(self, repo_url: str, extensions: list = None):
    if not self._auth or not self.token:
      raise Exception("Not authenticated. Call Terence.auth(token) first.")

    owner, repo_name = parse_github_url(repo_url)

    try:
      # Opens new Github instance, automatically closes at the end
      with Github(auth=self._auth) as g:
        # Check rate limit before starting scan
        rate_limit = g.get_rate_limit()
        remaining = rate_limit.rate.remaining
        reset_time = rate_limit.rate.reset

        # Need at least 10 requests to scan anything useful
        if remaining < 10:
          raise RateLimitException(f"Rate limit too low: {remaining} requests remaining. Resets at {reset_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

        repo = g.get_repo(f"{owner}/{repo_name}")
        # Pass Github instance to check rate limit during recursion
        self.results = self._get_files_recursive(repo, "", extensions, g)
        # Returns a flat dictionary of every file specified by the user so not nested
        self.last_repo_url = repo_url
    except RateLimitException as e:
      self.results = {}  # Clear results on rate limit error
      raise  # Re-raise the RateLimitException as-is
    except BadCredentialsException:
      self.results = {}  # Clear results on error
      raise Exception("Invalid GitHub token. Please check your token and try again.")
    except UnknownObjectException:
      self.results = {}  # Clear results on error
      raise Exception(f"Repository '{owner}/{repo_name}' not found. Check the URL or access permissions.")
    except GithubException as e:
      self.results = {}  # Clear results on error
      raise Exception(f"GitHub API error: {e.data.get('message', str(e))}")
    except Exception as e:
      self.results = {}  # Clear results on any error
      raise
  
  # Reset results but stay authenticated
  def clear_results(self):
    self.results = {}
    self.last_repo_url = None
    self._branch = None

  # Deauthenticate as well
  def clear_all(self):
    self.token = None
    self._auth = None
    self.results = {}
    self.last_repo_url = None
    self._branch = None

  # Check current rate limit status
  def get_rate_limit(self):
    """
    Get current GitHub API rate limit information

    Returns:
      dict: {
        'remaining': int,  # Requests remaining
        'limit': int,      # Total limit per hour
        'reset': datetime  # When the limit resets
      }
    """
    if not self._auth or not self.token:
      raise Exception("Not authenticated. Call Terence.auth(token) first.")

    with Github(auth=self._auth) as g:
      rate_limit = g.get_rate_limit()
      return {
        'remaining': rate_limit.rate.remaining,
        'limit': rate_limit.rate.limit,
        'reset': rate_limit.rate.reset
      }

  # Get repository owner and name from last scanned repo
  def get_repo_info(self):
    """
    Get owner and repository name from the last scanned repository

    Returns:
      dict: {
        'owner': str,
        'repo': str,
        'url': str
      } or None if no repository has been scanned yet
    """
    if not self.last_repo_url:
      return None

    owner, repo_name = parse_github_url(self.last_repo_url)
    return {
      'owner': owner,
      'repo': repo_name,
      'url': self.last_repo_url
    }
  
  # Recursively get all files into a flat dictionary
  def _get_files_recursive(self, repo, path="", extensions=None, github_instance=None):
    results = {}

    # Check rate limit before making API call
    if github_instance:
      rate_limit = github_instance.get_rate_limit()
      remaining = rate_limit.rate.remaining
      reset_time = rate_limit.rate.reset

      # If we're running low on requests, stop the scan
      if remaining < 10:
        raise RateLimitException(f"Rate limit reached during scan: {remaining} requests remaining. Resets at {reset_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Get contents at the current path from GitHub in the specified branch
    if self._branch:
      contents = repo.get_contents(path, ref=self._branch)
    else:
      contents = repo.get_contents(path)

    # Take care of edge case where contents is one object file, so wrap it in a single-element list
    if not isinstance(contents, list):
      contents = [contents]

    for content in contents:
      # Check if type is directory or file
      if content.type == "dir":
        # Pass github_instance to recursive call
        subdir_results = self._get_files_recursive(repo, content.path, extensions, github_instance)
        results.update(subdir_results) # Merge dictionaries together, in the format { path: content }
      elif content.type == "file":
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
  
  # Set the branch property
  def branch(self, branch_name: str):
    self._branch = branch_name
    return self  # Allow chaining
  
  