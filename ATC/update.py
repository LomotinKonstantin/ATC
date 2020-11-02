from contextlib import contextmanager
import os
from pathlib import Path
import sys

from git import Repo


URL = "https://github.com/LomotinKonstantin/ATC"


@contextmanager
def push_path(p: str):
    old_path = os.getenv("Path")
    os.environ["Path"] += f";{p};"
    try:
        yield
    finally:
        os.environ["Path"] = old_path


def to_version() -> {str, None}:
    msg = "Usage:\n\nUpdate to the latest version:\n$ python update.py\n"
    msg += "\nUpdate to the specific version:\n$ python update.py v1.7.0\n"
    if len(sys.argv) > 2:
        print(msg)
        exit(0)
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in ("-h", "--help", "help"):
            print(msg)
            exit()
        return arg
    return None


def main():
    target_v = to_version()
    repo = Repo(str(Path(__file__).absolute().parent.parent))
    repo.heads.master.checkout()
    repo.remotes.origin.pull()
    tags = list(sorted(repo.tags, key=lambda t: t.commit.committed_datetime))
    if target_v is None:
        target_v = tags[-1]
    else:
        try:
            target_v = repo.tags[target_v]
        except Exception as e:
            print(e)
            print(f"Invalid tag: {target_v}")
            exit(0)
    target_commit = target_v.commit
    repo.git.checkout(target_commit)
    print(f"Successfully switched to {target_v}")


if __name__ == '__main__':
    git_path = Path(sys.executable).parent.parent / "PortableGit" / "bin"
    assert git_path.exists(), git_path
    with push_path(str(git_path)):
        main()
