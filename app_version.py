"""Resolve source versions from Git and frozen versions from build metadata."""

import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
SNAPSHOT = "build_version.json"
_NUMBER = r"(?:0|[1-9][0-9]*)"
_IDENTIFIER = r"(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
TAG_PATTERN = re.compile(
    rf"v({_NUMBER}\.{_NUMBER}\.{_NUMBER}(?:-{_IDENTIFIER}(?:\.{_IDENTIFIER})*)?)"
)


def version_from_tag(tag):
    match = TAG_PATTERN.fullmatch(tag)
    if not match:
        raise ValueError(f"Invalid release tag {tag!r}; expected vMAJOR.MINOR.PATCH with optional SemVer prerelease")
    return match.group(1)


def _git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True, capture_output=True, text=True, timeout=10,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    ).stdout.strip()


def resolve_version(root=ROOT, release_tag=None, development=False):
    """Explicit release tags must identify HEAD; ordinary source runs detect tags."""
    if release_tag is not None:
        version = version_from_tag(release_tag)
        if _git(root, "rev-parse", f"refs/tags/{release_tag}^{{commit}}") != _git(root, "rev-parse", "HEAD"):
            raise ValueError("Release tag does not identify the checked-out commit")
        if _git(root, "status", "--porcelain"):
            raise ValueError("Release builds require a clean working tree")
        return version
    try:
        sha = _git(root, "rev-parse", "--short", "HEAD")
        dirty = bool(_git(root, "status", "--porcelain"))
        tags = [tag for tag in _git(root, "tag", "--merged", "HEAD").splitlines()
                if TAG_PATTERN.fullmatch(tag)]
        if tags:
            description = _git(root, "describe", "--tags", "--long", "--abbrev=7",
                               *[arg for tag in tags for arg in ("--match", tag)], "HEAD")
            tag, distance, _ = description.rsplit("-", 2)
            base = version_from_tag(tag)
            if distance == "0" and not dirty and not development:
                return base
        else:
            base = "0.0.0"
            distance = _git(root, "rev-list", "--count", "HEAD")
        separator = "." if "-" in base else "-"
        return f"{base}{separator}dev.{distance}+{sha}" + (".dirty" if dirty else "")
    except (OSError, subprocess.SubprocessError):
        return "0.0.0-dev"


def get_app_version():
    if getattr(sys, "frozen", False):
        # Never consult Git or the working directory from an installed build.
        return json.loads((ROOT / SNAPSHOT).read_text(encoding="utf-8"))["version"]
    return resolve_version()


APP_VERSION = get_app_version()
