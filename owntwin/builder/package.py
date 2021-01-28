from pathlib import Path


class Package(object):
    def __init__(self, cwd):
        self.cwd = Path(cwd)
        if not self.cwd.exists():
            self.cwd.mkdir()
        assert self.cwd.is_dir()

        self.assets = self.cwd.joinpath("./assets/")
        if not self.assets.exists():
            self.assets.mkdir()
