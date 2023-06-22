import csv
import enum
import pathlib
import random
import shutil
import tempfile
import time
from threading import Thread

from .models import Contact


class DownloadStatus(enum.StrEnum):
    WAITING = enum.auto()
    RUNNING = enum.auto()
    COMPLETE = enum.auto()


# I took a slightly different path from the book. But from what I understood
# the goal is to have a singleton
class Archiver:
    def __init__(self):
        self._status = DownloadStatus.WAITING
        self._temp_dir_path: pathlib.Path
        self._archive_path: pathlib.Path
        self._init_paths()
        self._progress: float = 0
        self._thread: Thread | None = None

    def reset(self):
        shutil.rmtree(self._temp_dir_path, ignore_errors=True)
        self._init_paths()
        self._status = DownloadStatus.WAITING
        self._progress = 0
        self._thread = None

    def _init_paths(self) -> None:
        self._temp_dir_path = pathlib.Path(tempfile.mkdtemp())
        self._archive_path = self._temp_dir_path / 'contacts.csv'

    def _create_archive(self) -> None:
        with self._archive_path.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['firstname', 'lastname', 'email', 'phone'])
            writer.writeheader()
            count = Contact.objects.count()
            for index, contact in enumerate(Contact.objects.all(), start=1):
                self._progress = round(index / count * 100, 2)
                # simulate some work time
                time.sleep(random.random())
                writer.writerow(contact.to_dict())

        # we check for a potential reset
        if self._status is not DownloadStatus.RUNNING:
            return
        self._status = DownloadStatus.COMPLETE

    def run(self) -> None:
        if self._status is DownloadStatus.WAITING:
            self._status = DownloadStatus.RUNNING
            self._thread = Thread(target=self._create_archive)
            self._thread.start()

    @property
    def archive_file(self) -> pathlib.Path:
        return self._archive_path

    @property
    def progress(self) -> float:
        return self._progress

    @property
    def status(self) -> str:
        return str(self._status)


_instance: Archiver | None = None


def get_archiver() -> Archiver:
    global _instance
    if _instance is None:
        _instance = Archiver()
        return _instance
    return _instance
