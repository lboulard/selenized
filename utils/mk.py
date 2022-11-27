import io
import json
import re
import sys
from pathlib import Path

from diagram import Diagram
from evaluate_template import MARKER_RE, load_palette_from_path

DEFAULT_OUTPUT_DIR = "output"

palettes = [
    load_palette_from_path(path)
    for path in [
        Path("palettes/selenized_black.py"),
        Path("palettes/selenized_dark.py"),
        Path("palettes/selenized_light.py"),
        Path("palettes/selenized_white.py"),
        Path("palettes/personalized/michal_pawluk.py"),
        Path("palettes/personalized/michal_sochon.py"),
        Path("palettes/personalized/piotr_kowalczyk.py"),
        Path("palettes/personalized/tomek_madycki.py"),
    ]
]


class Template:
    marker = re.compile(MARKER_RE)

    def __init__(self, path):
        self.lines = path.read_text().splitlines(keepends=True)

    def execute(self, palette, writer):
        def repl(matcher):
            return matcher.group("format").format(**palette)

        marker = self.marker
        for line in self.lines:
            try:
                writer.write(marker.sub(repl, line))
            except TypeError as ex:
                print(f"ERROR: attribute not available in palette: {ex}")
                raise


class Writer:
    def __init__(self, out):
        if isinstance(out, str) or isinstance(out, Path):
            self._path = Path(out)
            self._out = None
        elif out is None:
            self._path = None
            self._out = sys.stdout
        else:
            raise Exception("out shall be None, string or Path object")

    @property
    def path(self):
        return self._path or self._out.__name__

    @property
    def out(self):
        if self._out is None:
            self._out = self._path.open("w")
        return self._out

    def write(self, s):
        self.out.write(s)

    def close(self):
        if self.outpath:
            self._out.close()


class ColorListing:
    def __init__(self, out=None):
        self.template = Template(Path("templates/color-listing.template"))
        self.writer = io.StringIO()
        self.out = Writer(out)

    def run(self, palette):
        name = palette["name"]
        if self.writer.tell() > 0:
            print("_" * 66, file=self.writer)
            print(file=self.writer)
        self.template.execute(palette, self.writer)

    def finish(self):
        print(f"{self.out.path}")
        print(self.writer.getvalue(), file=self.out)


class Mintty:
    def __init__(self, outdir: Path):
        self.template = Template(Path("templates/mintty.minttyrc.template"))
        self.outdir = outdir
        outdir.mkdir(exist_ok=True)

    def run(self, palette):
        name = palette["name"]
        outpath = self.outdir / name
        print(f"{outpath}")
        with outpath.open("w") as writer:
            self.template.execute(palette, writer)

    def finish(self):
        pass


class MSTerminal:
    def __init__(self, out=None):
        self.template = Template(Path("templates/msterminal.json.template"))
        self.out = Writer(out)
        self.schemes = []

    def run(self, palette):
        name = palette["name"]
        writer = io.StringIO()
        self.template.execute(palette, writer)
        writer.seek(0)
        self.schemes.extend(json.load(writer)["schemes"])

    def finish(self):
        print(f"{self.out.path}")
        schemes = sorted(self.schemes, key=lambda x: x["name"])
        json.dump(dict(schemes=schemes), self.out, indent="  ")
        self.out.write("\n")


class Svg:
    def __init__(self, outdir: Path):
        self.diagram = Diagram()
        self.outdir = outdir
        outdir.mkdir(exist_ok=True)

    def run(self, palette):
        name = palette["name"]
        outpath = self.outdir / (name + ".svg")
        print(f"{outpath}")
        with outpath.open("w") as writer:
            self.diagram.write(palette, writer)

    def finish(self):
        pass


OUTPUT_DIR = Path(DEFAULT_OUTPUT_DIR)
OUTPUT_DIR.mkdir(exist_ok=True)

templates = [
    ColorListing(out=OUTPUT_DIR / "selenized.txt"),
    Mintty(outdir=OUTPUT_DIR / "mintty"),
    MSTerminal(out=OUTPUT_DIR / "selenized.msterminal-schemes.json"),
    Svg(outdir=OUTPUT_DIR / "svg"),
]

for template in templates:
    for palette in palettes:
        template.run(palette)
    template.finish()
