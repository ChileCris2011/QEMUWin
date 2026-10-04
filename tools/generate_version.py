"""Generate both packaging inputs from one resolved version."""

import argparse
import json
import os
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app_version import resolve_version


def generate(root=ROOT, release_tag=None):
    version = resolve_version(root, release_tag=release_tag, development=release_tag is None)
    output = root / "build" / "version"
    output.mkdir(parents=True, exist_ok=True)
    (output / "build_version.json").write_text(
        json.dumps({"version": version}) + "\n", encoding="utf-8", newline="\r\n"
    )
    (output / "version.iss").write_text(
        f'#define MyAppVersion "{version}"\n', encoding="utf-8", newline="\r\n"
    )
    return version


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-tag")
    args = parser.parse_args()
    try:
        version = generate(release_tag=args.release_tag)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Version generation failed: {error}\n")
    print(version)
    if output_file := os.environ.get("GITHUB_OUTPUT"):
        with open(output_file, "a", encoding="utf-8", newline="\n") as output:
            output.write(f"version={version}\nprerelease={str('-' in version).lower()}\n")
