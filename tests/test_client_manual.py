"""Manual tests for client module - run with: python tests/test_client_manual.py"""
from terence import Terence
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
    terence = Terence()
    terence.auth(token)
    print(f"Created: {terence}\n")

    # Test scanning with nested directories
    test_url = "https://github.com/github/gitignore"
    print(f"Scanning {test_url}...")

    try:
        terence.scan_repository(test_url)
        print(f"\n{terence}")
        print(f"Found {len(terence.results)} files")

        # Show first 10 files
        print("\nFirst 10 files found:")
        for path in list(terence.results.keys())[:10]:
            print(f"  - {path}")
    except Exception as e:
        print(f" Error: {e}")

    print("\n" + "="*70)
    print("Test 2: Invalid Token")
    print("="*70)

    bad_terence = Terence()
    bad_terence.auth("ghp_invalid_token_12345")

    try:
        bad_terence.scan_repository(test_url)
        print(" Should have raised an error!")
    except Exception as e:
        print(f" Caught error as expected: {e}")

    print("\n" + "="*70)
    print("Test 3: Invalid Repository URL")
    print("="*70)

    terence_test3 = Terence().auth(token)

    try:
        terence_test3.scan_repository("https://github.com/nonexistent/repo12345")
        print(" Should have raised an error!")
    except Exception as e:
        print(f" Caught error as expected: {e}")

    print("\n" + "="*70)
    print("Test 4: Clear Methods")
    print("="*70)

    terence_test4 = Terence().auth(token)
    terence_test4.scan_repository("https://github.com/pallets/click")

    print(f"Before clear: {terence_test4}")
    terence_test4.clear_results()
    print(f"After clear_results: {terence_test4}")

    terence_test4.clear_all()
    print(f"After clear_all: {terence_test4}")

    print("\n" + "="*70)
    print("All manual tests completed!")
    print("="*70)
