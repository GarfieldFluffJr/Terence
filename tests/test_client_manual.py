"""Manual tests for client module - run with: python tests/test_client_manual.py"""
from terrence import Terrence
from dotenv import dotenv_values


if __name__ == "__main__":
    env = dotenv_values()
    token = env.get('GitHubAccessToken')

    if not token:
        print("Error: No token found in .env")
        exit(1)

    print("="*70)
    print("Test 1: Basic Authentication and Scanning")
    print("="*70)

    # Test valid authentication
    terrence = Terrence()
    terrence.auth(token)
    print(f"Created: {terrence}\n")

    # Test scanning with nested directories
    test_url = "https://github.com/github/gitignore"
    print(f"Scanning {test_url}...")

    try:
        terrence.scan_repository(test_url)
        print(f"\n{terrence}")
        print(f"Found {len(terrence.results)} files")

        # Show first 10 files
        print("\nFirst 10 files found:")
        for path in list(terrence.results.keys())[:10]:
            print(f"  - {path}")
    except Exception as e:
        print(f" Error: {e}")

    print("\n" + "="*70)
    print("Test 2: Invalid Token")
    print("="*70)

    bad_terrence = Terrence()
    bad_terrence.auth("ghp_invalid_token_12345")

    try:
        bad_terrence.scan_repository(test_url)
        print(" Should have raised an error!")
    except Exception as e:
        print(f" Caught error as expected: {e}")

    print("\n" + "="*70)
    print("Test 3: Invalid Repository URL")
    print("="*70)

    terrence_test3 = Terrence().auth(token)

    try:
        terrence_test3.scan_repository("https://github.com/nonexistent/repo12345")
        print(" Should have raised an error!")
    except Exception as e:
        print(f" Caught error as expected: {e}")

    print("\n" + "="*70)
    print("Test 4: Clear Methods")
    print("="*70)

    terrence_test4 = Terrence().auth(token)
    terrence_test4.scan_repository("https://github.com/pallets/click")

    print(f"Before clear: {terrence_test4}")
    terrence_test4.clear_results()
    print(f"After clear_results: {terrence_test4}")

    terrence_test4.clear_all()
    print(f"After clear_all: {terrence_test4}")

    print("\n" + "="*70)
    print("All manual tests completed!")
    print("="*70)
