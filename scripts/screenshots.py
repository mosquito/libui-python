"""Take screenshots of all tutorial examples (macOS only).

Usage: python scripts/screenshots.py [--output-dir docs/tutorial/screenshots]

Launches each example, waits for its window, captures a screenshot
with native macOS window shadow via screencapture -l. No extra
dependencies — uses ctypes + CoreGraphics to find the CGWindowID.
"""

import argparse
import ctypes
import ctypes.util
import re
import subprocess
import sys
import time
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "docs" / "tutorial" / "examples"

# Examples that require user interaction or won't render a static window
SKIP = {
    "16-dialogs.py",  # opens system dialogs
}

# --- CoreGraphics / CoreFoundation ctypes bindings (macOS only) ---

if sys.platform == "darwin":
    _cg = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreGraphics"))
    _cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreFoundation"))

    _cg.CGWindowListCopyWindowInfo.restype = ctypes.c_void_p
    _cg.CGWindowListCopyWindowInfo.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    _cf.CFArrayGetCount.restype = ctypes.c_long
    _cf.CFArrayGetCount.argtypes = [ctypes.c_void_p]
    _cf.CFArrayGetValueAtIndex.restype = ctypes.c_void_p
    _cf.CFArrayGetValueAtIndex.argtypes = [ctypes.c_void_p, ctypes.c_long]
    _cf.CFDictionaryGetValue.restype = ctypes.c_void_p
    _cf.CFDictionaryGetValue.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _cf.CFStringCreateWithCString.restype = ctypes.c_void_p
    _cf.CFStringCreateWithCString.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_uint32,
    ]
    _cf.CFNumberGetValue.restype = ctypes.c_bool
    _cf.CFNumberGetValue.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]

    _kCFStringEncodingUTF8 = 0x08000100
    _kCFNumberIntType = 9

    def _cfstr(s: bytes) -> ctypes.c_void_p:
        return _cf.CFStringCreateWithCString(None, s, _kCFStringEncodingUTF8)

    _kPID = _cfstr(b"kCGWindowOwnerPID")
    _kNum = _cfstr(b"kCGWindowNumber")
    _kLayer = _cfstr(b"kCGWindowLayer")
    _kBounds = _cfstr(b"kCGWindowBounds")
    _kOnScreen = _cfstr(b"kCGWindowIsOnscreen")

    _cf.CFBooleanGetValue.restype = ctypes.c_bool
    _cf.CFBooleanGetValue.argtypes = [ctypes.c_void_p]

    _cf.CFDictionaryGetValue.restype = ctypes.c_void_p
    _cf.CFDictionaryGetValue.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    # CGRectMakeWithDictionaryRepresentation
    class _CGRect(ctypes.Structure):
        class _CGPoint(ctypes.Structure):
            _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

        class _CGSize(ctypes.Structure):
            _fields_ = [("width", ctypes.c_double), ("height", ctypes.c_double)]

        _fields_ = [("origin", _CGPoint), ("size", _CGSize)]

    _cg.CGRectMakeWithDictionaryRepresentation.restype = ctypes.c_bool
    _cg.CGRectMakeWithDictionaryRepresentation.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(_CGRect),
    ]


def find_window_id(pid: int, timeout: float = 8.0) -> int | None:
    """Find CGWindowID for the main (layer 0) window owned by pid."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        wl = _cg.CGWindowListCopyWindowInfo(0, 0)  # kCGWindowListOptionAll
        n = _cf.CFArrayGetCount(wl)
        for i in range(n):
            d = _cf.CFArrayGetValueAtIndex(wl, i)
            # Match PID
            pv = _cf.CFDictionaryGetValue(d, _kPID)
            if not pv:
                continue
            p = ctypes.c_int()
            _cf.CFNumberGetValue(pv, _kCFNumberIntType, ctypes.byref(p))
            if p.value != pid:
                continue
            # Only layer 0 (normal windows)
            lv = _cf.CFDictionaryGetValue(d, _kLayer)
            if lv:
                layer = ctypes.c_int()
                _cf.CFNumberGetValue(lv, _kCFNumberIntType, ctypes.byref(layer))
                if layer.value != 0:
                    continue
            # Must be on screen
            osv = _cf.CFDictionaryGetValue(d, _kOnScreen)
            if not osv or not _cf.CFBooleanGetValue(osv):
                continue
            # Skip zero-size windows (hidden/utility)
            bv = _cf.CFDictionaryGetValue(d, _kBounds)
            if bv:
                rect = _CGRect()
                if _cg.CGRectMakeWithDictionaryRepresentation(bv, ctypes.byref(rect)):
                    if rect.size.width < 10 or rect.size.height < 10:
                        continue
            wnum = _cf.CFDictionaryGetValue(d, _kNum)
            wid = ctypes.c_int()
            _cf.CFNumberGetValue(wnum, _kCFNumberIntType, ctypes.byref(wid))
            return wid.value
        time.sleep(0.5)
    return None


def extract_window_title(script: Path) -> str | None:
    """Extract the first Window() title string from a script."""
    text = script.read_text()
    m = re.search(r'Window\(\s*"([^"]+)"', text)
    return m.group(1) if m else None


def main():
    if sys.platform != "darwin":
        print("This script only works on macOS.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "docs"
        / "tutorial"
        / "screenshots",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Seconds to wait after window appears before capture",
    )
    parser.add_argument(
        "examples",
        nargs="*",
        help="Specific example filenames (e.g. 00-hello-world.py). Default: all.",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    scripts = sorted(EXAMPLES_DIR.glob("*.py"))
    if args.examples:
        names = set(args.examples)
        scripts = [s for s in scripts if s.name in names]

    for script in scripts:
        if script.name in SKIP:
            print(f"  SKIP {script.name}")
            continue

        title = extract_window_title(script)
        if not title:
            print(f"  SKIP {script.name} (no Window title found)")
            continue

        output = args.output_dir / f"{script.stem}.png"
        print(f"  {script.name} -> {output.name} ...", end=" ", flush=True)

        proc = subprocess.Popen(
            [sys.executable, str(script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            wid = find_window_id(proc.pid)
            if wid is None:
                print("FAIL (window not found)")
                proc.kill()
                continue

            time.sleep(args.delay)

            subprocess.check_call(
                [
                    "screencapture",
                    "-l",
                    str(wid),
                    str(output),
                ]
            )
            print("OK")
        finally:
            proc.kill()
            proc.wait()


if __name__ == "__main__":
    main()
