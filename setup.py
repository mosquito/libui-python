"""Build setup for libui package — builds libui-ng via meson, then compiles core.c."""

import subprocess
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext

LIBUI_SRC = Path(__file__).parent / "src" / "libui-ng"


class build_ext(_build_ext):
    def build_extension(self, ext):
        build_dir = Path(self.build_temp) / "libui-build"
        build_dir.mkdir(parents=True, exist_ok=True)

        # Configure meson
        if not (build_dir / "build.ninja").exists():
            subprocess.check_call([
                "meson", "setup",
                str(build_dir),
                str(LIBUI_SRC),
                "--default-library=static",
                "--buildtype=release",
                "-Dtests=false",
                "-Dexamples=false",
            ])

        # Build
        subprocess.check_call(["meson", "compile", "-C", str(build_dir)])

        # Find libui.a / libui.lib
        libui_a = build_dir / "libui.a"
        if not libui_a.exists():
            libui_a = build_dir / "libui.lib"
        if not libui_a.exists():
            # Search for it
            for f in build_dir.rglob("libui.*"):
                if f.suffix in (".a", ".lib"):
                    libui_a = f
                    break
        if not libui_a.exists():
            raise RuntimeError(f"Cannot find libui static library in {build_dir}")

        ext.extra_objects = [str(libui_a)]

        # Platform-specific flags
        if sys.platform == "linux":
            pkg_cflags = subprocess.check_output(
                ["pkg-config", "--cflags", "gtk+-3.0"],
                text=True,
            ).strip().split()
            pkg_libs = subprocess.check_output(
                ["pkg-config", "--libs", "gtk+-3.0"],
                text=True,
            ).strip().split()
            ext.extra_compile_args.extend(pkg_cflags)
            ext.extra_link_args.extend(pkg_libs)
            ext.extra_link_args.extend(["-lm", "-ldl", "-lstdc++"])
        elif sys.platform == "darwin":
            ext.extra_link_args.extend([
                "-framework", "Cocoa",
                "-lobjc",
                "-lstdc++",
            ])
        elif sys.platform == "win32":
            ext.libraries.extend([
                "user32", "kernel32", "gdi32", "comctl32",
                "uxtheme", "d2d1", "dwrite",
                "ole32", "oleaut32", "uuid",
            ])

        super().build_extension(ext)


setup(
    ext_modules=[
        Extension(
            "libui.core",
            sources=[
                "src/libui/module.c",
                "src/libui/enums.c",
                "src/libui/control.c",
                "src/libui/widget_window.c",
                "src/libui/widget_box.c",
                "src/libui/widget_button.c",
                "src/libui/widget_label.c",
                "src/libui/widget_entry.c",
                "src/libui/widget_checkbox.c",
                "src/libui/widget_combobox.c",
                "src/libui/widget_tab.c",
                "src/libui/widget_group.c",
                "src/libui/widget_spinbox.c",
                "src/libui/widget_slider.c",
                "src/libui/widget_progressbar.c",
                "src/libui/widget_separator.c",
                "src/libui/widget_editablecombobox.c",
                "src/libui/widget_radiobuttons.c",
                "src/libui/widget_datetimepicker.c",
                "src/libui/widget_multilineentry.c",
                "src/libui/widget_colorbutton.c",
                "src/libui/widget_fontbutton.c",
                "src/libui/widget_form.c",
                "src/libui/widget_grid.c",
                "src/libui/widget_menu.c",
                "src/libui/image.c",
                "src/libui/attribute.c",
                "src/libui/attributed_string.c",
                "src/libui/draw.c",
                "src/libui/widget_area.c",
                "src/libui/table_model.c",
                "src/libui/widget_table.c",
            ],
            include_dirs=[str(LIBUI_SRC), "src/libui"],
            extra_compile_args=["-D_UI_STATIC"],
        ),
    ],
    cmdclass={"build_ext": build_ext},
)
