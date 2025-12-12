"""Comprehensive manual test for scanning a real repository"""
import os
from terence import Terence, RateLimitException
from dotenv import dotenv_values

# Load token from environment variable (CI) or .env (local)
token = os.environ.get('GitHubAccessToken')
if not token:
    env = dotenv_values()
    token = env.get('GitHubAccessToken')

# OLD CODE (local only):
# env = dotenv_values()
# token = env.get('GitHubAccessToken')

if not token:
    print("❌ No GitHub token found in environment or .env")
    exit(1)

print("=" * 70)
print("COMPREHENSIVE REPOSITORY SCAN TEST")
print("=" * 70)

# You can change this to any small repo you want to test
# Suggestions:
# - "https://github.com/github/gitignore" (simple, flat structure)
# - "https://github.com/octocat/Spoon-Knife" (very small)
# - "https://github.com/pallets/click" (medium, has nesting)
TEST_REPO_URL = "https://github.com/pallets/click"

terence = Terence().auth(token)

print(f"\n📦 Test Repository: {TEST_REPO_URL}")
print("=" * 70)

# Test 1: Check rate limit before scanning
print("\n1️⃣  Checking rate limit before scan...")
try:
    rate = terence.get_rate_limit()
    print(f"   ✅ Rate limit: {rate['remaining']}/{rate['limit']}")
    print(f"   ✅ Resets at: {rate['reset']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 2: Check initial state
print("\n2️⃣  Checking initial state...")
print(f"   ✅ Results: {len(terence.results)} files (should be 0)")
print(f"   ✅ Last repo: {terence.last_repo_url} (should be None)")
print(f"   ✅ Repo info: {terence.get_repo_info()} (should be None)")

# Test 3: Scan the repository
print("\n3️⃣  Scanning repository...")
try:
    terence.scan_repository(TEST_REPO_URL)
    print(f"   ✅ Scan completed successfully!")
    print(f"   ✅ Found {len(terence.results)} files")
except RateLimitException as e:
    print(f"   ❌ Rate limit error: {e}")
    exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 4: Verify results are populated
print("\n4️⃣  Verifying results...")
if len(terence.results) > 0:
    print(f"   ✅ Results populated: {len(terence.results)} files")

    # Show all file paths
    print("\n   📁 Files found:")
    for i, path in enumerate(sorted(terence.results.keys()), 1):
        print(f"      {i}. {path}")
else:
    print(f"   ❌ No files found (this might be expected if repo has only non-code files)")

# Test 5: Check file contents
print("\n5️⃣  Checking file contents...")
if len(terence.results) > 0:
    # Get first file
    first_file_path = list(terence.results.keys())[0]
    first_file_content = terence.results[first_file_path]

    print(f"   ✅ Sample file: {first_file_path}")
    print(f"   ✅ Content length: {len(first_file_content)} characters")
    print(f"   ✅ Content lines: {len(first_file_content.splitlines())} lines")

    # Show first 10 lines of content
    lines = first_file_content.splitlines()
    preview_lines = min(10, len(lines))
    print(f"\n   📄 First {preview_lines} lines of '{first_file_path}':")
    print("   " + "-" * 66)
    for i, line in enumerate(lines[:preview_lines], 1):
        print(f"   {i:3} | {line[:60]}")
    if len(lines) > 10:
        print(f"   ... ({len(lines) - 10} more lines)")
    print("   " + "-" * 66)
else:
    print("   ⚠️  No files to display content for")

# Test 6: Test get_repo_info()
print("\n6️⃣  Testing get_repo_info()...")
repo_info = terence.get_repo_info()
if repo_info:
    print(f"   ✅ Owner: {repo_info['owner']}")
    print(f"   ✅ Repo: {repo_info['repo']}")
    print(f"   ✅ URL: {repo_info['url']}")

    # Verify it matches what we scanned
    if repo_info['url'] == TEST_REPO_URL:
        print(f"   ✅ URL matches test repo")
    else:
        print(f"   ❌ URL mismatch: expected {TEST_REPO_URL}, got {repo_info['url']}")
else:
    print("   ❌ Repo info is None (should be populated after scan)")

# Test 7: Test last_repo_url
print("\n7️⃣  Testing last_repo_url...")
if terence.last_repo_url:
    print(f"   ✅ Last repo URL: {terence.last_repo_url}")
    if terence.last_repo_url == TEST_REPO_URL:
        print(f"   ✅ Matches test repo")
    else:
        print(f"   ❌ URL mismatch")
else:
    print("   ❌ Last repo URL is None (should be set after scan)")

# Test 8: Test clear_results()
print("\n8️⃣  Testing clear_results()...")
files_before = len(terence.results)
terence.clear_results()
files_after = len(terence.results)
print(f"   Files before: {files_before}")
print(f"   Files after: {files_after}")
if files_after == 0 and terence.last_repo_url is None:
    print(f"   ✅ clear_results() works correctly")
    print(f"   ✅ Repo info: {terence.get_repo_info()} (should be None)")
else:
    print(f"   ❌ clear_results() didn't clear properly")

# Test 9: Test that we're still authenticated
print("\n9️⃣  Verifying still authenticated...")
if terence.token and terence._auth:
    print(f"   ✅ Still authenticated after clear_results()")

    # Scan again to verify everything still works
    print(f"   🔄 Re-scanning to verify...")
    try:
        terence.scan_repository(TEST_REPO_URL)
        print(f"   ✅ Re-scan successful: {len(terence.results)} files")
    except Exception as e:
        print(f"   ❌ Re-scan failed: {e}")
else:
    print(f"   ❌ Not authenticated (should still be authenticated)")

# Test 10: Check rate limit after scanning
print("\n🔟 Checking rate limit after scan...")
try:
    rate_after = terence.get_rate_limit()
    print(f"   ✅ Rate limit: {rate_after['remaining']}/{rate_after['limit']}")

    # Calculate how many requests we used
    requests_used = rate['remaining'] - rate_after['remaining']
    print(f"   📊 Requests used: {requests_used}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Final summary
print("\n" + "=" * 70)
print("✅ COMPREHENSIVE TEST COMPLETE")
print("=" * 70)
print(f"\nFinal state:")
print(f"  - Files in results: {len(terence.results)}")
print(f"  - Last repo URL: {terence.last_repo_url}")
print(f"  - Repo info: {terence.get_repo_info()}")
print(f"  - Authenticated: {terence.token is not None}")
print("\n" + "=" * 70)
