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

  # Tests with extension filters

  def test_python_file_with_py_filter(self):
    """Test that .py file matches py filter"""
    assert should_scan_file("src/main.py", extensions=["py"]) == True

  def test_python_file_with_js_filter(self):
    """Test that .py file does not match js filter"""
    assert should_scan_file("src/main.py", extensions=["js"]) == False

  def test_javascript_file_with_js_filter(self):
    """Test that .js file matches js filter"""
    assert should_scan_file("app.js", extensions=["js"]) == True

  def test_file_with_multiple_filters_match(self):
    """Test that file matches one of multiple filters"""
    assert should_scan_file("app.js", extensions=["py", "js"]) == True

  def test_file_with_multiple_filters_no_match(self):
    """Test that file doesn't match any of multiple filters"""
    assert should_scan_file("app.js", extensions=["py", "go"]) == False

  def test_typescript_with_ts_filters(self):
    """Test TypeScript file with TS filters"""
    assert should_scan_file("app.ts", extensions=["js", "ts", "tsx"]) == True

  def test_tsx_file_with_tsx_filter(self):
    """Test TSX file with tsx filter"""
    assert should_scan_file("component.tsx", extensions=["tsx"]) == True

  def test_css_file_with_css_scss_filters(self):
    """Test CSS file with CSS and SCSS filters"""
    assert should_scan_file("style.css", extensions=["css", "scss"]) == True

  def test_scss_file_with_css_filter_only(self):
    """Test SCSS file with CSS filter only - should not match"""
    assert should_scan_file("style.scss", extensions=["css"]) == False

  def test_excluded_dir_with_matching_filter(self):
    """Test that excluded dirs are excluded even with matching filter"""
    assert should_scan_file("node_modules/react/index.js", extensions=["js"]) == False

  def test_go_file_with_go_filter(self):
    """Test Go file with go filter"""
    assert should_scan_file("main.go", extensions=["go"]) == True

  def test_rust_file_with_rs_filter(self):
    """Test Rust file with rs filter"""
    assert should_scan_file("lib.rs", extensions=["rs"]) == True

  # Tests with invalid extensions

  def test_invalid_extension_raises_error(self):
    """Test that invalid extension raises ValueError"""
    with pytest.raises(ValueError, match="not in allowed extensions"):
      should_scan_file("file.txt", extensions=["txt"])

  def test_invalid_extension_in_list_raises_error(self):
    """Test that invalid extension in list raises ValueError"""
    with pytest.raises(ValueError, match="not in allowed extensions"):
      should_scan_file("file.py", extensions=["py", "invalid"])

  def test_json_filter_raises_error(self):
    """Test that json filter raises error (not allowed)"""
    with pytest.raises(ValueError, match="not in allowed extensions"):
      should_scan_file("data.json", extensions=["json"])

  # Tests with extension normalization

  def test_extension_without_dot(self):
    """Test that extension without dot is normalized"""
    assert should_scan_file("main.py", extensions=["py"]) == True

  def test_extension_with_dot(self):
    """Test that extension with dot works"""
    assert should_scan_file("main.py", extensions=[".py"]) == True

  def test_mixed_dot_notation(self):
    """Test that mixed dot notation works"""
    assert should_scan_file("app.js", extensions=["py", ".js"]) == True

  # Edge cases

  def test_empty_extensions_list(self):
    """Test behavior with empty extensions list"""
    assert should_scan_file("main.py", extensions=[]) == False