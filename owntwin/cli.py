import os
import posixpath
import re
import sys
import urllib
from functools import partial
from pathlib import Path

import importlib.resources
import typer
from loguru import logger

import owntwin.builder.cli

logger.remove()
logger.add(sys.stderr, format="{message}", level="ERROR", backtrace=True, diagnose=True)
# logger.add(sys.stderr, format="{message}", level="INFO")

app = typer.Typer()

# app.add_typer(owntwin.builder.cli.app, name="builder")

app.command("init")(owntwin.builder.cli.init)
app.command("add-terrain")(owntwin.builder.cli.add_terrain)
app.command("add")(owntwin.builder.cli.add)
app.command("export")(owntwin.builder.cli.export)


@app.command("view")
def view(
    dirname: str = typer.Argument("."),
    port: int = typer.Option(8000),
    no_terrain: bool = typer.Option(False, "--no-terrain", help="Disable terrain"),
):
    import socketserver
    from http.server import SimpleHTTPRequestHandler

    class RequestHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            SimpleHTTPRequestHandler.end_headers(self)

        def translate_path(self, path):
            if path.startswith("/__/"):
                path = re.sub(r"^/__/", "/", path)
                directory = str(Path(dirname))
            else:
                directory = self.directory
            # print(path, directory)
            # abandon query parameters
            path = path.split("?", 1)[0]
            path = path.split("#", 1)[0]
            # Don't forget explicit trailing slash when normalizing. Issue17324
            trailing_slash = path.rstrip().endswith("/")
            try:
                path = urllib.parse.unquote(path, errors="surrogatepass")
            except UnicodeDecodeError:
                path = urllib.parse.unquote(path)
            path = posixpath.normpath(path)
            words = path.split("/")
            words = filter(None, words)
            path = directory
            for word in words:
                if os.path.dirname(word) or word in (os.curdir, os.pardir):
                    # Ignore components that are not a simple file/directory name
                    continue
                path = os.path.join(path, word)
            if trailing_slash:
                path += "/"
            return path

    viewer_dir = importlib.resources.files("owntwin.viewer.owntwin").joinpath("")

    Handler = partial(
        RequestHandler,
        # directory=Path(__file__).parent.joinpath("./viewer/owntwin/"),
        directory=viewer_dir,
    )

    Server = socketserver.TCPServer
    Server.allow_reuse_address = True

    with Server(("localhost", port), Handler) as httpd:
        print(
            f"Started preview on http://localhost:{port}/?twin=http://localhost:{port}/__/{'&no-terrain' if no_terrain else ''}"
        )
        httpd.serve_forever()


@app.callback()
def main(verbose: int = typer.Option(0, "--verbose", "-v", count=True)):
    if verbose == 1:
        logger.remove()
        logger.add(
            sys.stderr, format="{message}", level="INFO", backtrace=True, diagnose=True
        )
    elif verbose == 2 or verbose > 2:
        logger.remove()
        logger.add(
            sys.stderr, format="{message}", level="DEBUG", backtrace=True, diagnose=True
        )


if __name__ == "__main__":
    app()
