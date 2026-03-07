# Installation

## From PyPI

```bash
pip install libui
```

Pre-built wheels are published for **Python 3.10 – 3.14** on **macOS**, **Linux** (manylinux) and **Windows**. The wheel bundles the compiled C extension and a statically linked libui-ng, so no compiler or system libraries are needed — just `pip install` and go.

If a wheel isn't available for your platform, pip will fall back to building from the source distribution (see below).

## From source

```bash
git clone --recurse-submodules https://github.com/mosquito/libui-python.git
cd libui-python
pip install -e ".[dev]"
```

## Build prerequisites

libui-python includes a C extension that wraps the libui-ng library. Building from source requires:

- Python >= 3.10
- A C/C++ compiler (gcc, clang, or MSVC)
- [Meson](https://mesonbuild.com/) >= 1.0
- [Ninja](https://ninja-build.org/)

### macOS

Xcode command-line tools provide everything except Meson/Ninja:

```bash
xcode-select --install
pip install meson ninja
```

The Cocoa framework is built-in — no extra libraries needed.

### Linux

Install GTK+3 development headers and a compiler:

```bash
# Debian / Ubuntu
sudo apt install build-essential libgtk-3-dev
pip install meson ninja

# Fedora
sudo dnf install gcc gcc-c++ gtk3-devel
pip install meson ninja

# Arch
sudo pacman -S base-devel gtk3
pip install meson ninja
```

### Windows

Install Visual Studio Build Tools (or full Visual Studio) with the "Desktop development with C++" workload. Then:

```bash
pip install meson ninja
```

The Win32 API is built-in — no extra libraries needed.

## Verifying the installation

```python
import libui
print(libui.core)  # <module 'libui.core' from '...'>
```
