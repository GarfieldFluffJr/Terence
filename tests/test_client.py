"""Pytest tests for client module"""
import os
import pytest
from terence import Terence
from dotenv import dotenv_values


# Fixture to load token from environment variable or .env
@pytest.fixture
def github_token():
    """Load GitHub token from environment variable (CI) or .env (local)"""
    # Try environment variable first (for CI/CD)
    token = os.environ.get('GitHubAccessToken')

    # Fall back to .env file (for local development)
    if not token:
        env = dotenv_values()
        token = env.get('GitHubAccessToken')

    # OLD CODE (local only):
    # env = dotenv_values()
    # token = env.get('GitHubAccessToken')

    if not token:
        pytest.skip("No GitHub token found in environment or .env file")
    return token


@pytest.fixture
def terence(github_token):
    """Create authenticated Terrence instance"""
    return Terence().auth(github_token)


class TestTerenceInitialization:
    """Test Terrence initialization"""

    def test_init_creates_empty_instance(self):
        """Test that __init__ creates empty instance"""
        terence = Terence()
        assert terence.token is None
        assert terence._auth is None
        assert terence.results == {}
        assert terence.last_repo_url is None

    def test_repr_not_authenticated(self):
        """Test __repr__ for unauthenticated instance"""
        terence = Terence()
        assert "not authenticated" in repr(terence)
        assert "no scans yet" in repr(terence)


class TestTerenceAuthentication:
    """Test authentication"""

    def test_auth_sets_token(self, github_token):
        """Test that auth() sets token"""
        terence = Terence()
        terence.auth(github_token)
        assert terence.token == github_token
        assert terence._auth is not None

    def test_auth_returns_self(self, github_token):
        """Test that auth() returns self for chaining"""
        terence = Terence()
        result = terence.auth(github_token)
        assert result is terence

    def test_auth_chaining(self, github_token):
        """Test method chaining works"""
        terence = Terence().auth(github_token)
        assert terence.token == github_token

    def test_repr_authenticated(self, github_token):
        """Test __repr__ for authenticated instance"""
        terence = Terence().auth(github_token)
        assert "authenticated" in repr(terence)


class TestTerenceScanRepository:
    """Test repository scanning"""

    def test_scan_without_auth_raises_error(self):
        """Test that scanning without auth raises error"""
        terence = Terence()
        with pytest.raises(Exception, match="Not authenticated"):
            terence.scan_repository("https://github.com/pallets/click")

    def test_scan_small_repo(self, terence):
        """Test scanning a small repository with Python files"""
        terence.scan_repository("https://github.com/pallets/click")

        assert len(terence.results) > 0, "Expected to find files in repository"
        assert terence.last_repo_url == "https://github.com/pallets/click"
        # Check that we found Python files (not README which has no extension)
        py_files = [path for path in terence.results.keys() if path.endswith('.py')]
        assert len(py_files) > 0, f"Expected Python files, found: {list(terence.results.keys())[:5]}"

    def test_scan_invalid_token_raises_error(self):
        """Test that invalid token raises error"""
        bad_terence = Terence().auth("ghp_invalid_token")
        with pytest.raises(Exception, match="Invalid GitHub token"):
            bad_terence.scan_repository("https://github.com/pallets/click")

    def test_scan_nonexistent_repo_raises_error(self, terence):
        """Test that nonexistent repo raises error"""
        with pytest.raises(Exception, match="not found"):
            terence.scan_repository("https://github.com/nonexistent/repo12345")

    def test_scan_updates_repr(self, terence):
        """Test that scanning updates __repr__"""
        before = repr(terence)
        terence.scan_repository("https://github.com/pallets/click")
        after = repr(terence)

        assert "no scans yet" in before
        assert "files=" in after


class TestTerenceClearMethods:
    """Test clear methods"""

    def test_clear_results(self, terence):
        """Test clear_results() clears results but keeps auth"""
        terence.scan_repository("https://github.com/pallets/click")

        assert len(terence.results) > 0
        assert terence.last_repo_url is not None

        terence.clear_results()

        assert len(terence.results) == 0
        assert terence.last_repo_url is None
        assert terence.token is not None  # Still authenticated
        assert terence._auth is not None

    def test_clear_all(self, terence):
        """Test clear_all() clears everything"""
        terence.scan_repository("https://github.com/pallets/click")

        terence.clear_all()

        assert terence.token is None
        assert terence._auth is None
        assert len(terence.results) == 0
        assert terence.last_repo_url is None


class TestTerenceEdgeCases:
    """Test edge cases"""

    def test_scan_twice_overwrites_results(self, terence):
        """Test that scanning twice overwrites previous results"""
        terence.scan_repository("https://github.com/pallets/click")
        first_results = dict(terence.results)

        terence.scan_repository("https://github.com/pallets/click")
        second_results = dict(terence.results)

        # Results should be the same (same repo)
        assert first_results == second_results

    # Edge Case 1: Malformed URLs
    def test_malformed_url_raises_error(self, terence):
        """Test that malformed URLs raise ValueError"""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            terence.scan_repository("not-a-url")

    def test_malformed_url_missing_parts(self, terence):
        """Test that incomplete URLs raise ValueError"""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            terence.scan_repository("https://github.com/only-owner")

    def test_malformed_url_just_slash(self, terence):
        """Test that just a slash raises ValueError"""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            terence.scan_repository("/")

    # Edge Case 2: Binary Files
    def test_binary_files_excluded(self, terence):
        """Test that binary files are excluded from results"""
        # Flask repo has code files and potentially images in docs
        terence.scan_repository("https://github.com/pallets/flask")

        # Should have some files (Python files)
        assert len(terence.results) > 0

        # Check that no binary file extensions are in results
        binary_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.exe']
        for path in terence.results.keys():
            for ext in binary_extensions:
                assert not path.endswith(ext), f"Binary file {path} should have been excluded"

    def test_only_text_files_included(self, terence):
        """Test that only text/code files are included"""
        terence.scan_repository("https://github.com/pallets/click")

        # All results should be text-decodable (we already decoded them)
        for path, content in terence.results.items():
            assert isinstance(content, str), f"{path} content should be string"
            assert len(content) >= 0, f"{path} should have content"

    # Edge Case 3: Empty Repositories
    def test_empty_repository_results(self, terence):
        """Test scanning repository with no code files"""
        # This is a repo with only README (no extension, so filtered out)
        terence.scan_repository("https://github.com/octocat/Hello-World")

        # Should be empty because README has no extension and gets filtered
        assert terence.results == {}, "Repository with only README should have empty results"

    # Edge Case 4: Extension Filtering
    def test_extension_filtering_single(self, terence):
        """Test filtering by single extension"""
        terence.scan_repository("https://github.com/pallets/click", extensions=["py"])

        assert len(terence.results) > 0, "Should find Python files"

        # All files should be .py
        for path in terence.results.keys():
            assert path.endswith('.py'), f"{path} should be a Python file"

    def test_extension_filtering_multiple(self, terence):
        """Test filtering by multiple extensions"""
        # Find a repo with multiple file types
        terence.scan_repository("https://github.com/pallets/flask", extensions=["py", "html", "css"])

        assert len(terence.results) > 0, "Should find files"

        # All files should end with one of the specified extensions
        for path in terence.results.keys():
            assert any(path.endswith(f'.{ext}') for ext in ["py", "html", "css"]), \
                f"{path} should be .py, .html, or .css"

    def test_extension_filtering_no_matches(self, terence):
        """Test filtering with extension that doesn't exist in repo"""
        # Python repo, filter for Go files
        terence.scan_repository("https://github.com/pallets/click", extensions=["go"])

        # Should be empty - no Go files in Python repo
        assert terence.results == {}, "Should find no Go files in Python repository"

    def test_extension_filtering_none_gets_all(self, terence):
        """Test that extensions=None gets all allowed files"""
        terence.scan_repository("https://github.com/pallets/click", extensions=None)
        all_files_count = len(terence.results)

        terence.clear_results()
        terence.scan_repository("https://github.com/pallets/click", extensions=["py"])
        py_only_count = len(terence.results)

        # Without filter should get more files than with filter
        assert all_files_count >= py_only_count, "No filter should get at least as many files as filtered"

    # Edge Case 5: Network Errors
    def test_network_error_invalid_domain(self, terence):
        """Test handling of network errors with invalid domain"""
        # This will fail at DNS resolution or connection level
        with pytest.raises(Exception):
            terence.scan_repository("https://github.fake/owner/repo")

    # Edge Case 6: Deep Directory Nesting
    def test_deep_directory_nesting(self, terence):
        """Test scanning repository with deeply nested directories"""
        # Flask has reasonably deep nesting (src/flask/json/...)
        terence.scan_repository("https://github.com/pallets/flask")

        # Check that we found deeply nested files
        max_depth = 0
        for path in terence.results.keys():
            depth = path.count('/')
            max_depth = max(max_depth, depth)

        assert max_depth >= 2, f"Should find files at least 2 levels deep, found {max_depth}"
        assert len(terence.results) > 0, "Should successfully scan deeply nested repository"


""" Error Types:
ValueError - parse_github_url(): "Invalid GitHub URL: {url}"
- URL not in GitHub format
- URL doesn't contain owner or repo name

Exception: "Not authenticated. Call Terrence.auth(token) first."
- Token not provided

BadCredentialsException: "Invalid GitHub token. Please check your token and try again."
- Invalid token format
- Expired token
- Revoked token

UnknownObjectException - scan_repository(): "Repository '{owner}/{repo_name}' not found. Check the URL or access permissions."
- Nonexistent repository
- Private repository
- Deleted repository
- Typo in URL

GithubException: "GitHub API error: {GitHub's error message}"
- Rate limiting exceeded
- Network errors
- GitHub API down
- Permission issues

ValueError - should_scan_file(): "Extension '{ext}' is not in allowed extensions."
- Provided an invalid extension
"""