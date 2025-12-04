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
            terrence.scan_repository("https://github.com/octocat/Hello-World")

    def test_scan_small_repo(self, terrence):
        """Test scanning a small repository"""
        terrence.scan_repository("https://github.com/psf/requests")

        assert len(terrence.results) > 0
        assert terrence.last_repo_url == "https://github.com/psf/requests"
        assert "README" in terrence.results

    def test_scan_invalid_token_raises_error(self):
        """Test that invalid token raises error"""
        bad_terrence = Terrence().auth("ghp_invalid_token")
        with pytest.raises(Exception, match="Invalid GitHub token"):
            bad_terrence.scan_repository("https://github.com/octocat/Hello-World")

    def test_scan_nonexistent_repo_raises_error(self, terrence):
        """Test that nonexistent repo raises error"""
        with pytest.raises(Exception, match="not found"):
            terrence.scan_repository("https://github.com/nonexistent/repo12345")

    def test_scan_updates_repr(self, terrence):
        """Test that scanning updates __repr__"""
        before = repr(terrence)
        terrence.scan_repository("https://github.com/octocat/Hello-World")
        after = repr(terrence)

        assert "no scans yet" in before
        assert "files=" in after


class TestTerrenceClearMethods:
    """Test clear methods"""

    def test_clear_results(self, terrence):
        """Test clear_results() clears results but keeps auth"""
        terrence.scan_repository("https://github.com/octocat/Hello-World")

        assert len(terrence.results) > 0
        assert terrence.last_repo_url is not None

        terrence.clear_results()

        assert len(terrence.results) == 0
        assert terrence.last_repo_url is None
        assert terrence.token is not None  # Still authenticated
        assert terrence._auth is not None

    def test_clear_all(self, terrence):
        """Test clear_all() clears everything"""
        terrence.scan_repository("https://github.com/octocat/Hello-World")

        terrence.clear_all()

        assert terrence.token is None
        assert terrence._auth is None
        assert len(terrence.results) == 0
        assert terrence.last_repo_url is None


class TestTerrenceEdgeCases:
    """Test edge cases"""

    def test_scan_twice_overwrites_results(self, terrence):
        """Test that scanning twice overwrites previous results"""
        terrence.scan_repository("https://github.com/octocat/Hello-World")
        first_results = dict(terrence.results)

        terrence.scan_repository("https://github.com/octocat/Hello-World")
        second_results = dict(terrence.results)

        # Results should be the same (same repo)
        assert first_results == second_results
