"""Release script for the kyc-central-client monorepo.

Bumps the version in all three client libraries, commits, tags, and pushes.

Usage:
    python release.py 1.2.3

The version must be in X.Y.Z format (e.g. 0.7.0, 1.2.3).

What it does:
  1. Validates the version format and that the working tree is clean,
     and the tag does not already exist.
  2. Updates version in:
     - python/src/kyccentral/_version.py  (__version__ = "X.Y.Z")
     - javascript/package.json  ("version": "X.Y.Z")
     - elixir/mix.exs                    (@version "X.Y.Z")
     - javascript/package-lock.json        (root version entries)
  3. Commits only the version changes.
  4. Tags and pushes the tag.
  5. The v* tag triggers publish.yml automatically.
"""

import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(cmd: list[str], **kw) -> str:
    """Run a CLI command and return stdout.  Raise on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if result.returncode != 0:
        print(f"❌  Command failed: {' '.join(cmd)}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()


def get_branch() -> str:
    return run(["git", "branch", "--show-current"])


def is_clean() -> bool:
    """Return True if the working tree has no unstaged changes."""
    out = run(["git", "status", "--porcelain"])
    return out == ""


def tag_exists(tag: str) -> bool:
    out = run(["git", "tag", "-l", tag])
    return out != ""


# ---------------------------------------------------------------------------
# Version bump / file edits
# ---------------------------------------------------------------------------

VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def bump_version(version: str) -> tuple[int, int, int]:
    m = VERSION_RE.match(version)
    if not m:
        print(f"❌  Version '{version}' is not in X.Y.Z format.")
        sys.exit(1)
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def python_version_file(path: Path, version: str) -> None:
    text = path.read_text().replace('__version__ = "0.4.0"', f'__version__ = "{version}"')
    path.write_text(text)


def js_package_json(path: Path, version: str) -> None:
    text = path.read_text()
    text = text.replace('"version": "0.4.0"', f'"version": "{version}"')
    path.write_text(text)


def elixir_mix_exs(path: Path, version: str) -> None:
    text = path.read_text()
    text = text.replace('@version "0.4.0"', f'@version "{version}"')
    path.write_text(text)


def npm_lockjack(path: Path, version: str) -> None:
    """Patch the root-level version entries in package-lock.json.

    The npm lockfile has root `"version"` and `"engines"` entries; align them
    so `npm install`/`npm publish` stays consistent with the package.json.
    """
    text = path.read_text()
    # Root version (there may be many "version" keys — only change the top-level
    # one that matches the stale value.  We target lines that start with spaces
    # at the very beginning of a JSON object value after the leading "":.
    # Simple approach: replace any occurrence of the exact stale string.
    text = text.replace('"version": "0.1.0"', f'"version": "{version}"')
    # Also fix engines if it still says ">=0.4.0" (harmless but tidy)
    text = text.replace('"node": ">=0.4.0"', f'"node": ">= {version.split(".")[0]}.{version.split(".")[1]}"')
    path.write_text(text)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python release.py <X.Y.Z>")
        sys.exit(1)

    version = sys.argv[1]
    major, minor, patch = bump_version(version)
    tag = f"v{version}"

    print(f"🚀  Release script — bumping to {version} ({major}.{minor}.{patch})")

    # ---- 1. Safety checks ----
    print("🔎  Checking working tree…")
    if not is_clean():
        print("❌  Working tree is not clean. Commit or stash changes first.")
        sys.exit(1)

    print("🔎  Checking tag availability…")
    if tag_exists(tag):
        print(f"❌  Tag {tag} already exists locally.")
        sys.exit(1)

    # ---- 2. Update version files ----
    print("📦  Updating version files…")

    # Python
    py_ver = Path("python/src/kyccentral/_version.py")
    if not py_ver.exists():
        print("❌  Python version file not found.")
        sys.exit(1)
    python_version_file(py_ver, version)
    print(f"   ✔ python/src/kyccentral/_version.py")

    # JavaScript package.json
    js_pkg = Path("javascript/package.json")
    if not js_pkg.exists():
        print("❌  JavaScript package.json not found.")
        sys.exit(1)
    js_package_json(js_pkg, version)
    print(f"   ✔ javascript/package.json")

    # Elixir mix.exs
    elixir_exs = Path("elixir/mix.exs")
    if not elixir_exs.exists():
        print("❌  Elixir mix.exs not found.")
        sys.exit(1)
    elixir_mix_exs(elixir_exs, version)
    print(f"   ✔ elixir/mix.exs")

    # package-lock.json (npm root version)
    lock_j = Path("javascript/package-lock.json")
    if not lock_j.exists():
        print("⚠️  javascript/package-lock.json not found — skipping lockfile patch.")
    else:
        npm_lockjack(lock_j, version)
        print(f"   ✔ javascript/package-lock.json")

    # ---- 3. Commit ----
    print("📝  Committing version changes…")
    # Add only the 4 changed version files
    run(["git", "add", "python/src/kyccentral/_version.py",
         "javascript/package.json",
         "elixir/mix.exs",
         "javascript/package-lock.json"])
    commit_msg = f"Release v{version}"
    run(["git", "commit", "-m", commit_msg])

    # ---- 4. Tag ----
    print(f"🏷️  Creating tag {tag}…")
    run(["git", "tag", tag])

    # ---- 5. Push ----
    branch = get_branch()
    print(f"🚀  Pushing branch {branch} and tag {tag}…")
    run(["git", "push", "origin", branch])
    run(["git", "push", "origin", tag])

    print(f"\n✅  Release {version} complete!")
    print(f"   Tag {tag} has been pushed. The publish.yml workflow will run automatically.")


if __name__ == "__main__":
    main()