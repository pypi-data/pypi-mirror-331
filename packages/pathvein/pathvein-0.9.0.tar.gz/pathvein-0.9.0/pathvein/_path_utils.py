import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Generator, List, Tuple

logger = logging.getLogger(__name__)


def stream_copy(source: Path, destination: Path, chunk_size=256 * 1024) -> None:
    """Copy a file from source to destination using a streaming copy"""
    logger.debug(
        "Stream copy initiated", extra={"file": source, "destination": destination}
    )
    with destination.open("wb") as writer, source.open("rb") as reader:
        # Localize variable access to minimize overhead.
        read = reader.read
        write = writer.write
        while chunk := read(chunk_size):
            write(chunk)
    logger.debug(
        "Copied file",
        extra={
            "file": source,
            "destination": destination,
        },
    )


def walk(source: Path) -> Generator[Tuple[Path, List[str], List[str]], None, None]:
    """
    Recursively walk a directory path and return a list of directories and filesystem

    Independent of os.walk or pathlib.Path.walk, this function just uses iterdir() to walk the directory tree

    In this way it works for both pathlib.Path objects as well as third-party pathlib objects so long as they
    implement iterdir(), is_dir, and is_file() methods.

    This does not offer a sophisticated symlink following mechanism. If `type` is Path, this will short circuit
    to os.walk which provides better symlink handling capability.
    """
    if type(source) is Path:
        for dirpath, dirnames, filenames in os.walk(source):
            yield Path(dirpath), dirnames, filenames
    else:
        dir_stack = []
        dir_stack.append(source)
        while dir_stack:
            path = dir_stack.pop()
            try:
                path, dirnames, filenames = iterdir(path)
            except PermissionError:
                logger.warning("Permission denied for %s", path)
                continue
            yield path, dirnames, filenames
            # Breadth-first traversal
            dirs = [path / dirname for dirname in dirnames]
            logger.debug("dirs: %s", dirs)
            dir_stack.extend(dirs)


@lru_cache(maxsize=None)
def iterdir(path: Path) -> Tuple[Path, List[str], List[str]]:
    """Return a list of all files and directories in a directory path"""
    contents = list(path.iterdir())
    filenames = [content.name for content in contents if content.is_file()]
    dirnames = [content.name for content in contents if content.is_dir()]
    return path, dirnames, filenames
