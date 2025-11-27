import pytest
from terrence.utils import *

class TestParseGitHubURL:
  def test_standard_https_url(self):
    result = parse_github_url("https://github.com/pytorch/pytorch")
    assert result == ("pytorch", "pytorch")
  def test_url_without_protocol(self):
    """Test parsing URL without https://"""
    result = parse_github_url("github.com/torvalds/linux")
    assert result == ("torvalds", "linux")

  def test_url_with_git_extension(self):
    """Test parsing URL with .git extension"""
    result = parse_github_url("https://github.com/microsoft/vscode.git")
    assert result == ("microsoft", "vscode")

  def test_url_with_trailing_slash(self):
    """Test parsing URL with trailing slash"""
    result = parse_github_url("https://github.com/python/cpython/")
    assert result == ("python", "cpython")

  def test_simple_owner_repo_format(self):
    """Test parsing simple owner/repo format"""
    result = parse_github_url("owner/repo")
    assert result == ("owner", "repo")

  def test_url_with_subdirectory(self):
    """Test that subdirectory URLs still extract correct repo"""
    result = parse_github_url("https://github.com/pytorch/pytorch/blob/main/README.md")
    assert result == ("pytorch", "pytorch")

  def test_invalid_url_raises_error(self):
    """Test that invalid URLs raise ValueError"""
    with pytest.raises(ValueError):
      parse_github_url("not-a-valid-url")

class TestShouldScanFile:
  def test_python_file_should_scan(self):
        """Test that .py files should be scanned"""
        assert should_scan_file("src/main.py") == True

  def test_javascript_file_should_scan(self):
    """Test that .js files should be scanned"""
    assert should_scan_file("app.js") == True

  def test_typescript_file_should_scan(self):
    """Test that .tsx files should be scanned"""
    assert should_scan_file("components/Header.tsx") == True

  def test_node_modules_should_not_scan(self):
    """Test that files in node_modules are excluded"""
    assert should_scan_file("node_modules/react/index.js") == False

  def test_venv_should_not_scan(self):
    """Test that files in venv are excluded"""
    assert should_scan_file("venv/lib/python3.9/site.py") == False

  def test_git_directory_should_not_scan(self):
    """Test that .git directory files are excluded"""
    assert should_scan_file(".git/config") == False

  def test_json_config_should_not_scan(self):
    """Test that config files are not scanned"""
    assert should_scan_file("package.json") == False

  def test_image_should_not_scan(self):
    """Test that image files are not scanned"""
    assert should_scan_file("image.png") == False

  def test_dist_directory_should_not_scan(self):
    """Test that build output is excluded"""
    assert should_scan_file("dist/bundle.js") == False