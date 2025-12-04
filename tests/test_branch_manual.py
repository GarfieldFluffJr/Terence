"""Manual test for branch functionality"""
from terrence import Terrence
from dotenv import dotenv_values

# Load token
env = dotenv_values()
token = env.get('GitHubAccessToken')

if not token:
    print("❌ No GitHub token found in .env")
    exit(1)

print("=" * 70)
print("BRANCH FUNCTIONALITY TEST")
print("=" * 70)

# Configuration - Change these to test different repos/branches
TEST_REPO = "https://github.com/pallets/click"
BRANCH_1 = "main"  # Current development branch
BRANCH_2 = "stable"  # Stable release branch

print(f"\n📦 Test Repository: {TEST_REPO}")
print(f"🔀 Branch 1: {BRANCH_1}")
print(f"🔀 Branch 2: {BRANCH_2}")
print("=" * 70)

terrence = Terrence().auth(token)

# Test 1: Scan first branch
print(f"\n1️⃣  Scanning branch: {BRANCH_1}...")
try:
    terrence.branch(BRANCH_1)
    terrence.scan_repository(TEST_REPO)
    branch1_files = len(terrence.results)
    branch1_results = dict(terrence.results)  # Save a copy of branch 1 results
    print(f"   ✅ Found {branch1_files} files on '{BRANCH_1}' branch")
    print(f"   📁 Files: {sorted(list(terrence.results.keys()))[:5]}{'...' if branch1_files > 5 else ''}")

    # Show repo info
    info = terrence.get_repo_info()
    print(f"   ✅ Repo: {info['owner']}/{info['repo']}")

    # Show content of first file
    if branch1_results:
        first_file = sorted(list(branch1_results.keys()))[0]
        print(f"\n   📄 Content of '{first_file}' on '{BRANCH_1}' branch:")
        print("   " + "-" * 66)
        lines = branch1_results[first_file].splitlines()
        for i, line in enumerate(lines[:10], 1):  # Show first 10 lines
            print(f"   {i:3} | {line[:60]}")
        if len(lines) > 10:
            print(f"   ... ({len(lines) - 10} more lines)")
        print("   " + "-" * 66)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 2: Clear and scan second branch
print(f"\n2️⃣  Scanning branch: {BRANCH_2}...")
terrence.clear_results()

try:
    terrence.branch(BRANCH_2)
    print(f"   🔀 Set branch to: {terrence._branch}")

    terrence.scan_repository(TEST_REPO)
    branch2_files = len(terrence.results)
    branch2_results = dict(terrence.results)  # Save a copy of branch 2 results
    print(f"   ✅ Found {branch2_files} files on '{BRANCH_2}' branch")
    print(f"   📁 Files: {sorted(list(terrence.results.keys()))[:5]}{'...' if branch2_files > 5 else ''}")

    # Show content of first file from branch 2
    if branch2_results:
        first_file = sorted(list(branch2_results.keys()))[0]
        print(f"\n   📄 Content of '{first_file}' on '{BRANCH_2}' branch:")
        print("   " + "-" * 66)
        lines = branch2_results[first_file].splitlines()
        for i, line in enumerate(lines[:10], 1):  # Show first 10 lines
            print(f"   {i:3} | {line[:60]}")
        if len(lines) > 10:
            print(f"   ... ({len(lines) - 10} more lines)")
        print("   " + "-" * 66)

    # Compare branches
    print(f"\n   📊 Branch Comparison:")
    print(f"      {BRANCH_1}: {branch1_files} files")
    print(f"      {BRANCH_2}: {branch2_files} files")

    # Check if files are the same
    branch1_file_set = set(branch1_results.keys())
    branch2_file_set = set(branch2_results.keys())

    only_in_branch1 = branch1_file_set - branch2_file_set
    only_in_branch2 = branch2_file_set - branch1_file_set
    common_files = branch1_file_set & branch2_file_set

    if only_in_branch1:
        print(f"\n   📁 Files only in {BRANCH_1}: {sorted(list(only_in_branch1))[:5]}{'...' if len(only_in_branch1) > 5 else ''}")
    if only_in_branch2:
        print(f"   📁 Files only in {BRANCH_2}: {sorted(list(only_in_branch2))[:5]}{'...' if len(only_in_branch2) > 5 else ''}")

    # Compare content of common files
    if common_files:
        print(f"\n   🔍 Comparing content of {len(common_files)} common files:")
        different_count = 0
        for file_path in sorted(common_files)[:10]:  # Check first 10 files
            if branch1_results[file_path] == branch2_results[file_path]:
                print(f"      ✅ {file_path}: IDENTICAL")
            else:
                different_count += 1
                print(f"      ⚠️  {file_path}: DIFFERENT")

                # Show the difference for first different file
                if different_count == 1:
                    branch1_lines = branch1_results[file_path].splitlines()
                    branch2_lines = branch2_results[file_path].splitlines()

                    print(f"         ({len(branch1_lines)} lines in {BRANCH_1} vs {len(branch2_lines)} lines in {BRANCH_2})")

                    # Show first different line
                    for i, (b1_line, b2_line) in enumerate(zip(branch1_lines, branch2_lines), 1):
                        if b1_line != b2_line:
                            print(f"         First difference at line {i}:")
                            print(f"         {BRANCH_1}: {b1_line[:45]}")
                            print(f"         {BRANCH_2}: {b2_line[:45]}")
                            break

except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"   💡 This might mean the branch doesn't exist")

# Test 3: Method chaining
print("\n3️⃣  Testing method chaining...")
try:
    terrence2 = Terrence().auth(token).branch("main")
    print(f"   ✅ Method chaining works!")
    print(f"   ✅ Branch set to: {terrence2._branch}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Invalid branch handling
print("\n4️⃣  Testing invalid branch...")
try:
    terrence.clear_results()
    terrence.branch("nonexistent-branch-12345")
    terrence.scan_repository("https://github.com/octocat/Spoon-Knife")
    print(f"   ❌ Should have raised error for invalid branch")
except Exception as e:
    print(f"   ✅ Correctly raised error: {e}")

# Test 5: Resetting branch
print("\n5️⃣  Testing branch reset...")
terrence.clear_results()
print(f"   ✅ Branch after clear_results: {terrence._branch} (should be None)")

print("\n" + "=" * 70)
print("✅ BRANCH TEST COMPLETE")
print("=" * 70)
