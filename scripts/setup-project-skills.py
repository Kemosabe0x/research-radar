#!/usr/bin/env python3
"""
Thin wrapper for the standalone cursor-project-skills package.

Install once:
  pip install -e /path/to/Cursor-Project-Skills
  # or: pip install git+https://github.com/YOUR_USER/Cursor-Project-Skills.git

Then from this repo:
  cursor-project-skills apply --profile .cursor/skills-profile.yaml
  cursor-project-skills dry-run --preset backend-ui

See: https://github.com/YOUR_USER/Cursor-Project-Skills
Docs: docs/project-skills-workflow.md
"""

from __future__ import annotations

import sys


def main() -> None:
    try:
        from cursor_project_skills.cli import main as cps_main
    except ImportError:
        print(
            "cursor-project-skills is not installed.\n\n"
            "  pip install -e /path/to/Cursor-Project-Skills\n\n"
            "Or run directly after install:\n"
            "  cursor-project-skills apply --profile .cursor/skills-profile.yaml\n",
            file=sys.stderr,
        )
        sys.exit(1)
    cps_main()


if __name__ == "__main__":
    main()
