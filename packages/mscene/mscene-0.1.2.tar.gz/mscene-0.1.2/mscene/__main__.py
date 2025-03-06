from pathlib import Path
import subprocess
import sys

try:
    from IPython.display import display, HTML, clear_output
except ImportError:
    pass
    # print("IPython is missing, so some features may not work.\nTo install, run: pip install ipython")


def progress(value, max):
    p = int(100 * value / max)
    html = f"<div style='font-size: 18px; display: flex; justify-content: space-between; width:25%;'><span>Manim Installation</span><span>{p}%</span></div><progress value='{value}' max='{max}' style='width: 25%; accent-color: #41FDFE;'></progress>"
    return HTML(html)


def find_package(pkg):
    cmd = ("dpkg", "-s", pkg)
    process = subprocess.run(cmd)
    found = process.returncode == 0
    return found


def install_manim(lite=False):

    cmd = [("apt-get", "-qq", "update")]

    if not lite and not find_package("texlive"):
        latex_pkg = (
            "texlive",
            "texlive-latex-extra",
            "texlive-science",
            "texlive-fonts-extra",
        )
        for pkg in latex_pkg:
            cmd.append(("apt-get", "-qq", "install", "-y", pkg))

    if "manim" not in sys.modules:
        cmd.append(("apt-get", "-qq", "install", "-y", "libpango1.0-dev"))
        cmd.append(("uv", "pip", "install", "-q", "--system", "manim"))
        # cmd.append(("uv", "pip", "install", "-q", "--system", "IPython==8.21.0"))

    n = len(cmd)

    if n > 1:
        # [optional font] STIX Two Text (stixfonts.org)
        font_url = "https://raw.githubusercontent.com/stipub/stixfonts/master/fonts/static_ttf/STIXTwoText-Regular.ttf"
        font_path = "/usr/share/fonts/truetype/stixfonts"
        font_cmd = ("wget", "-nv", "-nc", "-P", font_path, font_url)
        subprocess.run(font_cmd)

        output = display(progress(0, n), display_id=True)

        for i, c in enumerate(cmd, 1):
            subprocess.run(c)
            output.update(progress(i, n))


def config_manim(about=True):

    config.disable_caching = True
    config.verbosity = "WARNING"
    config.media_width = "50%"
    config.media_embed = True

    Text.set_default(font="STIX Two Text")

    if about:
        info = f"Manim – Mathematical Animation Framework (Version {version('manim')})\nhttps://www.manim.community"

        clear_output()

        print(info)


def add_plugins():

    mscene_path = Path(__file__).parent

    release = mscene_path / "RELEASE"

    plugin_url = "https://raw.githubusercontent.com/curiouswalk/mscene/refs/heads/main/plugins/source"

    release_url = f"{plugin_url}/RELEASE"
    release_file = f"{mscene_path}/RELEASE"

    cmd = ("curl", "-s", release_url)
    stdout = subprocess.run(cmd, capture_output=True, text=True).stdout.split()

    version = stdout[0]

    if release.exists():
        with open(release, "r") as rel:
            lines = rel.read().split()
            plugins = stdout[1:] if lines[0] != version else None
    else:
        plugins = stdout[1:]

    if plugins:
        cmd = ("curl", "-s", "-o", release_file, release_url)
        subprocess.run(cmd)
        for p in plugins:
            url = f"{plugin_url}/{p}.py"
            filename = f"{mscene_path}/{p}.py"
            cmd = ("curl", "-s", "-o", filename, url)
            subprocess.run(cmd)


def main():

    args = sys.argv[1:]

    if "plugins" in args and len(args) == 1:
        add_plugins()
        print("Plugins are up to date.")
    else:
        print("Error: Invalid Command")


if __name__ == "__main__":

    args = sys.argv[1:]

    if "-h" in args and len(args) == 1:

        cmd_info = (
            "- Run '%mscene -l manim' to install and import Manim without LaTeX.",
            "- Run '%mscene manim' to install and import Manim with LaTeX.",
            "- Run '%mscene plugins' to add and import Mscene plugins.",
            "- Run '%mscene mscene' to render an example scene.",
        )

        print("Commands", "-" * 8, *cmd_info, sep="\n")

    elif "plugins" in args and len(args) == 1:

        add_plugins()

        try:
            from mscene.plugins import *
        except ImportError:
            pass

    elif "manim" in args and len(args) == 1:

        install_manim()

        from manim import *

        config_manim()

    elif all(i in args for i in ("manim", "plugins")) and len(args) == 2:

        install_manim()

        from manim import *

        config_manim()

        add_plugins()

        from mscene.plugins import *

    elif all(i in args for i in ("-l", "manim")) and len(args) == 2:

        install_manim(lite=True)

        from manim import *

        config_manim()

    elif all(i in args for i in ("-l", "manim", "plugins")) and len(args) == 3:

        install_manim(lite=True)

        from manim import *

        config_manim()

        add_plugins()

        from mscene.plugins import *

    elif "mscene" in args and len(args) == 1:

        if "manim" not in sys.modules:
            install_manim(lite=True)

        from manim import *

        config_manim(about=False)

        from IPython import get_ipython

        ipy = get_ipython()

        class ExampleScene(Scene):
            def construct(self):
                banner = ManimBanner()
                self.play(banner.create())
                self.play(banner.expand())
                self.wait(1.5)

        ipy.run_line_magic("manim", "-qm ExampleScene")

    else:

        print("Error: Invalid Command\nRun '%mscene -h' to view commands.")
