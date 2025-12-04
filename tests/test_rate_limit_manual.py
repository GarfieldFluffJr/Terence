"""Manual test for rate limit error handling"""
from terrence import Terrence, RateLimitException
from dotenv import dotenv_values

# Load token from .env
env = dotenv_values()
token = env.get('GitHubAccessToken')

if not token:
    print("❌ No GitHub token found in .env")
    exit(1)

print("=" * 60)
print("Testing Rate Limit Error Handling")
print("=" * 60)

terrence = Terrence().auth(token)

# Test 1: Check current rate limit
print("\n1️⃣  Checking current rate limit...")
try:
    rate_info = terrence.get_rate_limit()
    print(f"   ✅ Remaining: {rate_info['remaining']}/{rate_info['limit']}")
    print(f"   ✅ Resets at: {rate_info['reset']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Try to scan a repo (should fail with rate limit)
print("\n2️⃣  Attempting to scan repository...")
print("   (This should fail because threshold is set to 4000)")
try:
    terrence.scan_repository("https://github.com/pallets/click")
    print(f"   ✅ Success! Found {len(terrence.results)} files")
except RateLimitException as e:
    print(f"   ⚠️  RateLimitException caught!")
    print(f"   ⚠️  Message: {e}")
    print(f"   ✅ Results cleared: {len(terrence.results)} files (should be 0)")
except Exception as e:
    print(f"   ❌ Other error: {e}")

# Test 3: Verify results are empty
print("\n3️⃣  Verifying results are empty after error...")
if len(terrence.results) == 0:
    print("   ✅ Results are empty (as expected)")
else:
    print(f"   ❌ Results not empty: {len(terrence.results)} files")

# Test 4: Check repo info (should be None since scan failed)
print("\n4️⃣  Checking repo info...")
repo_info = terrence.get_repo_info()
if repo_info is None:
    print("   ✅ Repo info is None (as expected, scan failed)")
else:
    print(f"   ❌ Repo info exists: {repo_info}")

# Test 5: Demonstrate proper error handling pattern
print("\n5️⃣  Demonstrating proper error handling pattern...")
def safe_scan(terrence_instance, url):
    """Example of how external programs should handle errors"""
    try:
        print(f"   📡 Attempting to scan: {url}")
        terrence_instance.scan_repository(url)
        print(f"   ✅ Success! Found {len(terrence_instance.results)} files")

        # Get repo info
        info = terrence_instance.get_repo_info()
        print(f"   ✅ Scanned: {info['owner']}/{info['repo']}")

    except RateLimitException as e:
        print(f"   ⚠️  Rate limit reached: {e}")
        print("   💡 Suggestion: Wait until reset time or use different token")

    except ValueError as e:
        print(f"   ❌ Invalid input: {e}")
        print("   💡 Suggestion: Check URL format and extensions")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   💡 Suggestion: Check token and repository access")

safe_scan(terrence, "https://github.com/pallets/click")

print("\n" + "=" * 60)
print("✅ Test complete!")
print("=" * 60)
print("\n💡 Remember to change the threshold back to 10 after testing:")
print("   - client.py line ~53: change 5001 back to 10")
print("   - client.py line ~145: change 5001 back to 10")
print("=" * 60)
