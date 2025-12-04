"""Pytest tests for client module"""
import pytest
from terrence import Terrence
from dotenv import dotenv_values


# Fixture to load token from .env
@pytest.fixture
def github_token():
    """Load GitHub token from .env for tests"""
    env = dotenv_values()
    token = env.get('GitHubAccessToken')
    if not token:
        pytest.skip("No GitHub token found in .env")
    return token


@pytest.fixture
def terrence(github_token):
    """Create authenticated Terrence instance"""
    return Terrence().auth(github_token)


class TestTerrenceInitialization:
    """Test Terrence initialization"""

    def test_init_creates_empty_instance(self):
        """Test that __init__ creates empty instance"""
        terrence = Terrence()
        assert terrence.token is None
        assert terrence._auth is None
        assert terrence.results == {}
        assert terrence.last_repo_url is None

    def test_repr_not_authenticated(self):
        """Test __repr__ for unauthenticated instance"""
        terrence = Terrence()
        assert "not authenticated" in repr(terrence)
        assert "no scans yet" in repr(terrence)


class TestTerrenceAuthentication:
    """Test authentication"""

    def test_auth_sets_token(self, github_token):
        """Test that auth() sets token"""
        terrence = Terrence()
        terrence.auth(github_token)
        assert terrence.token == github_token
        assert terrence._auth is not None

    def test_auth_returns_self(self, github_token):
        """Test that auth() returns self for chaining"""
        terrence = Terrence()
        result = terrence.auth(github_token)
        assert result is terrence

    def test_auth_chaining(self, github_token):
        """Test method chaining works"""
        terrence = Terrence().auth(github_token)
        assert terrence.token == github_token

    def test_repr_authenticated(self, github_token):
        """Test __repr__ for authenticated instance"""
        terrence = Terrence().auth(github_token)
        assert "authenticated" in repr(terrence)


class TestTerrenceScanRepository:
    """Test repository scanning"""

    def test_scan_without_auth_raises_error(self):
        """Test that scanning without auth raises error"""
        terrence = Terrence()
        with pytest.raises(Exception, match="Not authenticated"):
            terrence.scan_repository("https://github.com/pallets/click")

    def test_scan_small_repo(self, terrence):
        """Test scanning a small repository with Python files"""
        terrence.scan_repository("https://github.com/pallets/click")

        assert len(terrence.results) > 0, "Expected to find files in repository"
        assert terrence.last_repo_url == "https://github.com/pallets/click"
        # Check that we found Python files (not README which has no extension)
        py_files = [path for path in terrence.results.keys() if path.endswith('.py')]
        assert len(py_files) > 0, f"Expected Python files, found: {list(terrence.results.keys())[:5]}"

    def test_scan_invalid_token_raises_error(self):
        """Test that invalid token raises error"""
        bad_terrence = Terrence().auth("ghp_invalid_token")
        with pytest.raises(Exception, match="Invalid GitHub token"):
            bad_terrence.scan_repository("https://github.com/pallets/click")

    def test_scan_nonexistent_repo_raises_error(self, terrence):
        """Test that nonexistent repo raises error"""
        with pytest.raises(Exception, match="not found"):
            terrence.scan_repository("https://github.com/nonexistent/repo12345")

    def test_scan_updates_repr(self, terrence):
        """Test that scanning updates __repr__"""
        before = repr(terrence)
        terrence.scan_repository("https://github.com/pallets/click")
        after = repr(terrence)

        assert "no scans yet" in before
        assert "files=" in after


class TestTerrenceClearMethods:
    """Test clear methods"""

    def test_clear_results(self, terrence):
        """Test clear_results() clears results but keeps auth"""
        terrence.scan_repository("https://github.com/pallets/click")

        assert len(terrence.results) > 0
        assert terrence.last_repo_url is not None

        terrence.clear_results()

        assert len(terrence.results) == 0
        assert terrence.last_repo_url is None
        assert terrence.token is not None  # Still authenticated
        assert terrence._auth is not None

    def test_clear_all(self, terrence):
        """Test clear_all() clears everything"""
        terrence.scan_repository("https://github.com/pallets/click")

        terrence.clear_all()

        assert terrence.token is None
        assert terrence._auth is None
        assert len(terrence.results) == 0
        assert terrence.last_repo_url is None


class TestTerrenceEdgeCases:
    """Test edge cases"""

    def test_scan_twice_overwrites_results(self, terrence):
        """Test that scanning twice overwrites previous results"""
        terrence.scan_repository("https://github.com/pallets/click")
        first_results = dict(terrence.results)

        terrence.scan_repository("https://github.com/pallets/click")
        second_results = dict(terrence.results)

        # Results should be the same (same repo)
        assert first_results == second_results

    # Edge Case 1: Malformed URLs
    def test_malformed_url_raises_error(self, terrence):
        """Test that malformed URLs raise ValueError"""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            terrence.scan_repository("not-a-url")

    def test_malformed_url_missing_parts(self, terrence):
        """Test that incomplete URLs raise ValueError"""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            terrence.scan_repository("https://github.com/only-owner")

    def test_malformed_url_just_slash(self, terrence):
        """Test that just a slash raises ValueError"""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            terrence.scan_repository("/")

    # Edge Case 2: Binary Files
    def test_binary_files_excluded(self, terrence):
        """Test that binary files are excluded from results"""
        # Flask repo has code files and potentially images in docs
        terrence.scan_repository("https://github.com/pallets/flask")

        # Should have some files (Python files)
        assert len(terrence.results) > 0

        # Check that no binary file extensions are in results
        binary_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.exe']
        for path in terrence.results.keys():
            for ext in binary_extensions:
                assert not path.endswith(ext), f"Binary file {path} should have been excluded"

    def test_only_text_files_included(self, terrence):
        """Test that only text/code files are included"""
        terrence.scan_repository("https://github.com/pallets/click")

        # All results should be text-decodable (we already decoded them)
        for path, content in terrence.results.items():
            assert isinstance(content, str), f"{path} content should be string"
            assert len(content) >= 0, f"{path} should have content"

    # Edge Case 3: Empty Repositories
    def test_empty_repository_results(self, terrence):
        """Test scanning repository with no code files"""
        # This is a repo with only README (no extension, so filtered out)
        terrence.scan_repository("https://github.com/octocat/Hello-World")

        # Should be empty because README has no extension and gets filtered
        assert terrence.results == {}, "Repository with only README should have empty results"

    # Edge Case 4: Extension Filtering
    def test_extension_filtering_single(self, terrence):
        """Test filtering by single extension"""
        terrence.scan_repository("https://github.com/pallets/click", extensions=["py"])

        assert len(terrence.results) > 0, "Should find Python files"

        # All files should be .py
        for path in terrence.results.keys():
            assert path.endswith('.py'), f"{path} should be a Python file"

    def test_extension_filtering_multiple(self, terrence):
        """Test filtering by multiple extensions"""
        # Find a repo with multiple file types
        terrence.scan_repository("https://github.com/pallets/flask", extensions=["py", "html", "css"])

        assert len(terrence.results) > 0, "Should find files"

        # All files should end with one of the specified extensions
        for path in terrence.results.keys():
            assert any(path.endswith(f'.{ext}') for ext in ["py", "html", "css"]), \
                f"{path} should be .py, .html, or .css"

    def test_extension_filtering_no_matches(self, terrence):
        """Test filtering with extension that doesn't exist in repo"""
        # Python repo, filter for Go files
        terrence.scan_repository("https://github.com/pallets/click", extensions=["go"])

        # Should be empty - no Go files in Python repo
        assert terrence.results == {}, "Should find no Go files in Python repository"

    def test_extension_filtering_none_gets_all(self, terrence):
        """Test that extensions=None gets all allowed files"""
        terrence.scan_repository("https://github.com/pallets/click", extensions=None)
        all_files_count = len(terrence.results)

        terrence.clear_results()
        terrence.scan_repository("https://github.com/pallets/click", extensions=["py"])
        py_only_count = len(terrence.results)

        # Without filter should get more files than with filter
        assert all_files_count >= py_only_count, "No filter should get at least as many files as filtered"

    # Edge Case 5: Network Errors
    def test_network_error_invalid_domain(self, terrence):
        """Test handling of network errors with invalid domain"""
        # This will fail at DNS resolution or connection level
        with pytest.raises(Exception):
            terrence.scan_repository("https://github.fake/owner/repo")

    # Edge Case 6: Deep Directory Nesting
    def test_deep_directory_nesting(self, terrence):
        """Test scanning repository with deeply nested directories"""
        # Flask has reasonably deep nesting (src/flask/json/...)
        terrence.scan_repository("https://github.com/pallets/flask")

        # Check that we found deeply nested files
        max_depth = 0
        for path in terrence.results.keys():
            depth = path.count('/')
            max_depth = max(max_depth, depth)

        assert max_depth >= 2, f"Should find files at least 2 levels deep, found {max_depth}"
        assert len(terrence.results) > 0, "Should successfully scan deeply nested repository"


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