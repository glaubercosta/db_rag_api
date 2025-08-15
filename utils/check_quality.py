#!/usr/bin/env python3
"""
Code quality verification script
Runs tests, formatting and linting
"""
import subprocess
import sys


def run_command(command, description):
    """Run a shell command and display the result"""
    print(f"\n{'=' * 60}")
    print(f"Tool: {description}")
    print(f"{'=' * 60}")
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    if result.returncode != 0:
        print(f"FAILED: {description}")
        return False
    print(f"SUCCESS: {description}")
    return True


def main():
    """Main entry point"""
    print("Starting code quality checks...")
    checks = [
        ("python -m pytest tests/ -v", "Running tests"),
        ("python -m black --check .", "Checking formatting (Black)"),
        ("python -m flake8 .", "Checking style (Flake8)"),
    ]
    passed = 0
    total = len(checks)
    for command, description in checks:
        if run_command(command, description):
            passed += 1
    print(f"\n{'=' * 60}")
    print("FINAL RESULT")
    print(f"{'=' * 60}")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    if passed == total:
        print("All checks passed!")
        sys.exit(0)
    print("Some checks failed. See errors above.")
    sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
