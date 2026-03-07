"""Apply patches from patches/ to the libui-ng submodule (idempotent)."""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PATCHES_DIR = REPO_ROOT / "patches"
LIBUI_DIR = REPO_ROOT / "src" / "libui-ng"


def main():
    if not PATCHES_DIR.is_dir():
        return
    for patch in sorted(PATCHES_DIR.glob("*.patch")):
        # Check if already applied
        result = subprocess.run(
            ["git", "apply", "--reverse", "--check", str(patch)],
            cwd=LIBUI_DIR,
            capture_output=True,
        )
        if result.returncode == 0:
            continue
        print(f"Applying {patch.name}")
        subprocess.check_call(
            ["git", "apply", str(patch)],
            cwd=LIBUI_DIR,
        )


if __name__ == "__main__":
    main()
