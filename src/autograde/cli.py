"""
Command-line interface for the Autograde tool.
"""

import sys
import json
from . import RepositoryValidator


def main():
    """Main entry point for the CLI."""
    if len(sys.argv) < 2:
        print("Usage: autograde <repository_url>")
        print("Example: autograde https://github.com/user/repo.git")
        sys.exit(1)

    repo_url = sys.argv[1]

    validator = RepositoryValidator(repo_url)
    summary = validator.get_summary()

    # Print results
    print(f"Repository: {summary['repository_url']}")
    print(f"Is valid repository: {summary['is_valid_repository']}")
    print(f"Main branch exists: {summary['main_branch_exists']}")
    print(f"Feature branch exists: {summary['feature_branch_exists']}")
    print(f"file1.txt on main: {summary['file1_on_main']}")
    print(f"All checks passed: {summary['all_checks_passed']}")

    # Exit with appropriate code
    sys.exit(0 if summary["all_checks_passed"] else 1)


if __name__ == "__main__":
    main()
